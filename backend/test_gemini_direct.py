import unittest
from unittest.mock import patch
from planning import make_plan,clean_members

class GeminiDirectTests(unittest.TestCase):
 def test_gemini_owners_override_literal_skills(self):
  members=clean_members([{'id':'M1','name':'Dev','skills':['python','flask'],'daily_capacity':5}])
  generated={'tasks':[{'id':'T1','title':'Deploy app','description':'Configure gunicorn','required_skills':['gunicorn'],'dependencies':[]}]}
  predictor=lambda *args:{'estimated_hours':2,'priority':'medium','complexity':2,'category':'backend','required_skills':['gunicorn'],'delay_probability':.1}
  with patch('planning.recommend_task_owners',return_value=({'T1':{'member_ids':['M1'],'needs_training':True,'reason':'Best available developer'}},{'source':'gemini_direct_assignment'})):
   plan=make_plan(generated,members,3,predictor)
  self.assertTrue(plan['schedule_result']['all_tasks_scheduled'])
  self.assertEqual(plan['tasks'][0]['gemini_assignment']['member_ids'],['M1'])
  self.assertTrue(plan['tasks'][0]['gemini_assignment_needs_training'])
