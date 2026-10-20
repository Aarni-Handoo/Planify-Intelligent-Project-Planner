"""Train a simulated-overrun risk predictor on project-level scheduling scenarios.
Labels are Monte Carlo simulated schedule outcomes, NOT real historical delays.
Separate held-out project scenarios are used for evaluation.
"""
from pathlib import Path
import json, random
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, brier_score_loss
from sklearn.model_selection import train_test_split
from scheduler.engine import build_schedule

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'models'/'planning_v3';OUT.mkdir(parents=True,exist_ok=True)
R=random.Random(421)
SKILLS=['python','react','javascript','sql','database','api','testing','docker','cloud','machine learning','css','ui/ux']
FEATURES=['total_hours','capacity_hours','workload_ratio','days','task_count','member_count','missing_skills','dependency_count','max_chain','avg_complexity','baseline_unscheduled_hours','baseline_utilization']

def features(tasks,members,days,schedule):
    total=sum(float(t['estimated_hours']) for t in tasks)
    capacity=sum(float(m['daily_capacity']) for m in members)*days
    have=set(s for m in members for s in m['skills'])
    missing=len(set(s for t in tasks for s in t['required_skills'])-have)
    deps={t['id']:t.get('dependencies',[]) for t in tasks}
    memo={}
    def depth(tid):
        if tid not in memo:memo[tid]=1+max((depth(d) for d in deps.get(tid,[]) if d in deps),default=0)
        return memo[tid]
    chain=max((depth(t['id']) for t in tasks),default=0)
    unscheduled=sum(float(t['remaining_hours']) for t in schedule['unscheduled_tasks'])
    return [total,capacity,total/max(capacity,1),days,len(tasks),len(members),missing,
            sum(len(x) for x in deps.values()),chain,
            sum(float(t.get('complexity',3)) for t in tasks)/max(1,len(tasks)),
            unscheduled,1-unscheduled/max(total,1)]

def scenario():
    nm=R.randint(2,7);nt=R.randint(4,15);days=R.randint(3,22)
    members=[]
    for i in range(nm):
        members.append({'id':f'M{i}','name':f'M{i}', 'skills':R.sample(SKILLS,R.randint(2,5)),
                        'daily_capacity':R.randint(3,7)})
    tasks=[]
    for i in range(nt):
        skills=R.sample(SKILLS,R.randint(1,2))
        # Many tasks match the available team; some deliberately need missing skills.
        if R.random()<.78:
            skills=R.sample(sorted(set(s for m in members for s in m['skills'])),R.randint(1,2))
        dependencies=([f'T{R.randrange(i)}'] if i and R.random()<.25 else [])
        tasks.append({'id':f'T{i}','title':f'Task {i}', 'estimated_hours':round(R.uniform(3,26),2),
                      'required_skills':skills,'priority':R.choice(['high','medium','low']),
                      'complexity':R.randint(1,5),'dependencies':dependencies})
    return tasks,members,days

def main():
    X=[];y=[]
    for n in range(1600):
        tasks,members,days=scenario()
        baseline=build_schedule({'tasks':tasks,'members':members,'deadline_days':days})
        X.append(features(tasks,members,days,baseline))
        # Random actual effort overrun, approximately log-normal; labels indicate
        # whether a stochastic realization of the plan missed the deadline.
        perturbed=[{**t,'estimated_hours':round(t['estimated_hours']*R.lognormvariate(.12,.22),2)} for t in tasks]
        actual=build_schedule({'tasks':perturbed,'members':members,'deadline_days':days})
        y.append(int(not actual['all_tasks_scheduled']))
    X=np.array(X);y=np.array(y)
    data=pd.DataFrame(X,columns=FEATURES)
    data["missed_deadline_in_simulation"]=y
    data["scenario_id"]=[f"SIM-{i:05d}" for i in range(len(y))]
    data.to_csv(OUT/"simulated_project_outcomes.csv",index=False)
    xt,xv,yt,yv=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
    model=HistGradientBoostingClassifier(max_iter=125,max_leaf_nodes=12,l2_regularization=3,random_state=42)
    model.fit(xt,yt);prob=model.predict_proba(xv)[:,1];pred=(prob>=.5).astype(int)
    metrics={'data_source':'synthetic scheduling scenarios and stochastic effort-overrun simulations',
             'train_scenarios':len(xt),'heldout_scenarios':len(xv),
             'positive_rate_heldout':round(float(yv.mean()),4),
             'accuracy':round(float(accuracy_score(yv,pred)),4),
             'f1':round(float(f1_score(yv,pred)),4),
             'roc_auc':round(float(roc_auc_score(yv,prob)),4),
             'brier':round(float(brier_score_loss(yv,prob)),4),
             'limitations':'Simulated labels only; risk probabilities not calibrated on actual projects.'}
    joblib.dump(model,OUT/'overrun_model.joblib')
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2))
    (OUT/'features.json').write_text(json.dumps(FEATURES,indent=2))
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
