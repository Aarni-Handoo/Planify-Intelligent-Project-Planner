"""Hybrid planning: Gemini task decomposition; trained ML effort/priority;
conservative skill validation; deterministic capacity-aware scheduling.
"""
from collections import defaultdict
from pathlib import Path
import joblib
from datetime import date
from scheduler.engine import build_schedule
from scheduler.intelligence import normalize_skills
from gemini_skill_matching import recommend_task_owners


def clean_members(raw):
    members=[]
    for i,m in enumerate(raw):
        skills=normalize_skills(m.get('skills', []))['normalized_skills']
        members.append({'id':str(m.get('id') or f'M{i+1}'), 'name':str(m.get('name') or f'Member {i+1}'),
                        'skills':skills,'daily_capacity':float(m.get('daily_capacity',5))})
    return members


RISK_MODEL_PATH = Path(__file__).resolve().parent / 'ml' / 'models' / 'planning_v3' / 'overrun_model.joblib'
RISK_MODEL = joblib.load(RISK_MODEL_PATH) if RISK_MODEL_PATH.exists() else None

def risk_assessment(tasks, members, days, schedule):
    from ml.train_feasibility import features
    if RISK_MODEL is None:
        return {'available':False}
    probability=float(RISK_MODEL.predict_proba([features(tasks,members,days,schedule)])[0,1])
    return {'available':True,'estimated_overrun_probability':round(probability,3),
            'risk_level':'high' if probability>=.65 else 'medium' if probability>=.35 else 'low',
            'model':'trained_simulated_overrun_v3',
            'caution':'Trained on simulated scheduling outcomes; not validated on historical projects.'}

def make_plan(generated, members, days, predictor, project_type='General'):
    tasks=[]
    for t in generated['tasks']:
        analysis=predictor(t['title'],t.get('description',''),project_type,days,len(members))
        suggested=normalize_skills(t.get('required_skills',[]))['normalized_skills']
        # Critical technical skills come from the task specification; ML skill
        # predictions are advisory because source CSV assigns technologies randomly.
        skills=suggested or analysis['required_skills']
        tasks.append({**t,'required_skills':skills,'estimated_hours':analysis['estimated_hours'],
                      'priority':analysis['priority'],'complexity':analysis['complexity'],
                      'category':analysis['category'],'ml_delay_probability_experimental':analysis['delay_probability'],
                      'gemini_estimated_hours':t.get('estimated_hours'),
                      'ml_suggested_skills':analysis['required_skills'],
                      'effort_source':'trained_ml_v2'})
    recommendations, matching_info = recommend_task_owners(tasks, members)
    if not recommendations and members:
        # Explicitly marked heuristic fallback: do not masquerade as Gemini.
        # Keep every task assignable; specialist qualifications are flagged for review.
        for task in tasks:
            words = set(__import__('re').findall(r'[a-z0-9+#.]+',
                (task['title'] + ' ' + task.get('description','')).lower()))
            def score(member):
                skills = ' '.join(member.get('skills',[])).lower()
                tokens = set(__import__('re').findall(r'[a-z0-9+#.]+', skills))
                overlap = len(words & tokens)
                return (overlap, member.get('daily_capacity',0))
            chosen = max(members, key=score)
            recommendations[str(task['id'])] = {
                'member_ids':[str(chosen['id'])], 'needs_training':True,
                'reason':'Heuristic fallback; task skills must be confirmed by the team'}
        matching_info = {**matching_info, 'assignment_fallback':'heuristic_task_owner',
                         'warning': matching_info.get('warning','Gemini unavailable') + '; owners require review'}
    if recommendations:
        for task in tasks:
            rec = recommendations[str(task['id'])]
            task['gemini_assignment'] = rec
            # The AI has evaluated the entire task, not individual string tokens.
            # The deterministic scheduler still enforces hours and dependencies.
            task['preferred_member_ids'] = rec['member_ids']
            task['skill_eligibility'] = {
                str(member['id']): {str(skill).lower(): str(member['id']) in rec['member_ids']
                                    for skill in task['required_skills']}
                for member in members}
            task['gemini_assignment_needs_training'] = rec['needs_training']
    schedule=build_schedule({'tasks':tasks,'members':members,'deadline_days':days})
    remaining=sum(x['remaining_hours'] for x in schedule['unscheduled_tasks'])
    total=sum(x['estimated_hours'] for x in tasks)
    return {'success':True,'tasks':tasks,'schedule_result':schedule,
            'planning_summary':{'total_estimated_person_hours':round(total,2),
                                'unscheduled_person_hours':round(remaining,2),
                                'deadline_feasible_under_scheduler':schedule['all_tasks_scheduled'],
                                'method':'ML effort + collaborative constraint-aware scheduling',
                                'warning':'Feasibility is based on estimated effort, available skills and the scheduling heuristic; not a real-world guarantee.'},
            'generation_method':generated.get('method','unknown'),
            'skill_matching':matching_info,
            'deadline_risk':risk_assessment(tasks,members,days,schedule)}


def reschedule_existing(tasks,members,days):
    """Replan remaining tasks; completed work is removed from the capacity calculation.
    Completed dependencies are removed; unfinished dependencies remain intact.
    """
    done={str(t['id']) for t in tasks if t.get('completed') or t.get('deleted')}
    remaining=[]
    for t in tasks:
        if str(t['id']) in done:continue
        work=dict(t)
        work['dependencies']=[d for d in t.get('dependencies',[]) if d not in done]
        work['estimated_hours']=float(t.get('remaining_hours',t.get('estimated_hours',1)))
        remaining.append(work)
    schedule=build_schedule({'tasks':remaining,'members':members,'deadline_days':days})
    return {'success':True,'tasks':remaining,'schedule_result':schedule,
            'planning_summary':{'deadline_feasible_under_scheduler':schedule['all_tasks_scheduled'],
                                'unscheduled_person_hours':round(sum(x['remaining_hours'] for x in schedule['unscheduled_tasks']),2)},
            'deadline_risk':risk_assessment(remaining,members,days,schedule)}
