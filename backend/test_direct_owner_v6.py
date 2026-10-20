import unittest
from scheduler.engine import build_schedule
class DirectOwnerTests(unittest.TestCase):
 def test_owner_overrides_keyword_gate(self):
  r=build_schedule({'deadline_days':5,'members':[{'id':'M1','name':'Meera','skills':['Data Visualization'],'daily_capacity':4}], 'tasks':[{'id':'T1','title':'EDA','required_skills':['matplotlib','seaborn'],'preferred_member_ids':['M1'],'estimated_hours':8,'dependencies':[]}]})
  self.assertTrue(r['all_tasks_scheduled'])
  self.assertEqual({a['member_id'] for a in r['assignments']},{'M1'})
 def test_no_owner_still_rejects_unknown_skills(self):
  r=build_schedule({'deadline_days':5,'members':[{'id':'M1','name':'Meera','skills':['Data Visualization'],'daily_capacity':4}], 'tasks':[{'id':'T1','title':'Docker','required_skills':['kubernetes'],'estimated_hours':8,'dependencies':[]}]})
  self.assertFalse(r['all_tasks_scheduled'])
if __name__=='__main__': unittest.main()
