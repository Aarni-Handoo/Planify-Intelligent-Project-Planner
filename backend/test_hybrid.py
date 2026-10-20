import unittest
from planning import make_plan, clean_members, reschedule_existing

class HybridPlanningTests(unittest.TestCase):
    def setUp(self):
        self.members=clean_members([
            {'id':'M1','name':'Dev A','skills':['python','api','react','sql','database','testing'],'daily_capacity':5},
            {'id':'M2','name':'Dev B','skills':['react','css','python','api','testing'],'daily_capacity':5}])
        self.generated={'method':'gemini_llm_generation','tasks':[
            {'id':'T1','title':'Build React UI','description':'Build React UI','required_skills':['react'],'estimated_hours':30,'priority':'high','dependencies':[]},
            {'id':'T2','title':'Implement API','description':'Implement Python API','required_skills':['python','api'],'estimated_hours':20,'priority':'high','dependencies':['T1']} ]}
    def predict(self,*args):
        return {'category':'frontend','complexity':3,'priority':'high','estimated_hours':5,
                'required_skills':['vue'],'delay_probability':0}
    def test_ml_effort_replaces_gemini_and_skills_preserved(self):
        result=make_plan(self.generated,self.members,5,self.predict)
        self.assertEqual(result['tasks'][0]['estimated_hours'],5)
        self.assertEqual(result['tasks'][0]['gemini_estimated_hours'],30)
        self.assertEqual(result['tasks'][0]['required_skills'],['react'])
        self.assertTrue(result['schedule_result']['all_tasks_scheduled'])
        self.assertTrue(result['deadline_risk']['available'])
    def test_missing_skill_blocks_assignment(self):
        data={**self.generated,'tasks':[{**self.generated['tasks'][0],'required_skills':['rust']} ]}
        result=make_plan(data,self.members,5,self.predict)
        self.assertFalse(result['schedule_result']['all_tasks_scheduled'])
        self.assertIn('rust',result['schedule_result']['unscheduled_tasks'][0]['reason'])
    def test_replanning_removes_completed_dependencies(self):
        plan=make_plan(self.generated,self.members,5,self.predict)
        tasks=[{**t,'completed':t['id']=='T1'} for t in plan['tasks']]
        updated=reschedule_existing(tasks,self.members,5)
        self.assertEqual(len(updated['tasks']),1)
        self.assertEqual(updated['tasks'][0]['dependencies'],[])
        self.assertTrue(updated['schedule_result']['all_tasks_scheduled'])

if __name__=='__main__':unittest.main()
