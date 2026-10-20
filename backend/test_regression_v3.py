import unittest
from scheduler.engine import build_schedule

MEMBERS=[
 {'id':'A','name':'Aarav','skills':['HTML','CSS','JavaScript','Responsive Design','Chart.js'],'daily_capacity':5},
 {'id':'D','name':'Divya','skills':['Python','Flask','REST API','Authentication','SQLite','SQL','DBMS'],'daily_capacity':4},
 {'id':'R','name':'Rohan','skills':['Software Testing','Debugging','Git','GitHub','Deployment','Documentation'],'daily_capacity':3},
]
TASKS=[
 ('db',['database design'],[],2),('crud',['flask'],['db','auth'],5),
 ('analytics',['sql'],['crud'],3),('ui',['html','css'],[],5),
 ('frontauth',['javascript'],['ui','auth'],4),('frontcrud',['javascript'],['crud','ui'],4),
 ('charts',['javascript'],['analytics','ui'],3),('tests',['pytest'],['crud','frontcrud'],4),
 ('deploy',['linux'],['tests','charts'],3),('auth',['flask'],['db'],5)]

class TestRealFailure(unittest.TestCase):
 def test_exact_user_failure(self):
  tasks=[{'id':t,'title':t,'required_skills':s,'dependencies':d,'estimated_hours':h,'priority':'medium'} for t,s,d,h in TASKS]
  result=build_schedule({'tasks':tasks,'members':MEMBERS,'deadline_days':20})
  self.assertTrue(result['all_tasks_scheduled'],result['unscheduled_tasks'])
  self.assertEqual(len(result['completed_tasks']),10)
  for m in result['member_workload']:
   self.assertTrue(all(h<=m['daily_capacity']+1e-6 for h in m['daily_hours'].values()))
  bytask={a['task_id']:a['member_id'] for a in result['assignments']}
  self.assertEqual(bytask['tests'],'R');self.assertEqual(bytask['deploy'],'R')
  self.assertEqual(bytask['db'],'D')
 def test_hundred_variants(self):
  for i in range(10):
   tasks=[{'id':t,'title':t,'required_skills':s,'dependencies':d,'estimated_hours':h*(.6+(i%9)*.08),'priority':'high' if i%3==0 else 'medium'} for t,s,d,h in TASKS]
   result=build_schedule({'tasks':tasks,'members':MEMBERS,'deadline_days':20})
   self.assertTrue(result['all_tasks_scheduled'],(i,result['unscheduled_tasks']))
 def test_hundred_small_scenarios(self):
  for i in range(100):
   result=build_schedule({'tasks':[{'id':'t','title':'Test','required_skills':['pytest'],'estimated_hours':1+(i%5),'dependencies':[]}],'members':[MEMBERS[2]],'deadline_days':5})
   self.assertTrue(result['all_tasks_scheduled'])
 def test_impossible_deadline_is_honest(self):
  result=build_schedule({'tasks':[{'id':'x','title':'x','required_skills':['flask'],'estimated_hours':500,'dependencies':[]}], 'members':MEMBERS,'deadline_days':1})
  self.assertFalse(result['all_tasks_scheduled'])
