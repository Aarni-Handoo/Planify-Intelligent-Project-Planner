import unittest
from scheduler.engine import build_schedule

def task(i, skills, deps=(), hours=3):
 return dict(id=str(i),title=str(i),required_skills=skills,dependencies=list(map(str,deps)),estimated_hours=hours,priority='medium')
def member(i,skills,hours=5):
 return dict(id=str(i),name=str(i),skills=skills,daily_capacity=hours)

class GeneratedScenarioTests(unittest.TestCase):
 def assert_valid(self, result):
  self.assertTrue(result['all_tasks_scheduled'],result['unscheduled_tasks'])
  for m in result['member_workload']:
   self.assertTrue(all(v <= m['daily_capacity']+1e-6 for v in m['daily_hours'].values()))
  ends={}
  for a in result['assignments']: ends[a['task_id']]=max(ends.get(a['task_id'],0),a['day'])
  return ends
 def test_portfolio(self):
  members=[member('A',['HTML','CSS','JavaScript','Responsive Design','UI/UX'],5),member('R',['Git','GitHub','Testing','SEO','Deployment','Accessibility'],4)]
  tasks=[task('setup',['html','git']),task('about',['html'],['setup']),task('nav',['javascript'],['setup']),task('gallery',['html'],['setup']),task('contact',['javascript'],['setup']),task('formapi',['api'],['contact']),task('seo',['seo'],['setup']),task('access',['accessibility'],['nav']),task('browser',['testing'],['gallery','nav']),task('deploy',['deployment'],['formapi','browser']),task('polish',['css'],['gallery'])]
  self.assert_valid(build_schedule(dict(tasks=tasks,members=members,deadline_days=10)))
 def test_library(self):
  members=[member('D',['Python','Flask','SQL','SQLite','DBMS','REST API']),member('A',['HTML','CSS','JavaScript','Responsive Design'],4),member('R',['Software Testing','Git','GitHub','Deployment','Documentation'],3)]
  tasks=[task('setup',['flask','sql']),task('auth',['security'],['setup']),task('catalog',['flask'],['auth']),task('search',['javascript'],['catalog']),task('borrow',['flask'],['catalog']),task('fines',['sql'],['borrow']),task('ui',['html','css'],['setup']),task('tests',['pytest'],['fines','search']),task('deploy',['gunicorn'],['tests']),task('student',['flask','html'],['setup'])]
  self.assert_valid(build_schedule(dict(tasks=tasks,members=members,deadline_days=18)))
 def test_student_ml(self):
  members=[member('M',['Python','Pandas','NumPy','Data Cleaning','EDA']),member('A',['Machine Learning','scikit-learn','Classification','Regression','Model Evaluation']),member('N',['Streamlit','Python','Data Visualization','UI Design'],4),member('K',['Testing','GitHub','Deployment','Documentation'],3)]
  tasks=[task('scope',['requirements analysis','project management']),task('clean',['pandas'],['scope']),task('eda',['matplotlib','seaborn'],['clean']),task('train',['scikit-learn'],['eda']),task('evaluate',['model evaluation'],['train']),task('db',['database design','sql'],['scope']),task('dashboard',['streamlit'],['evaluate']),task('integration',['integration','sql'],['dashboard','db']),task('test',['pytest'],['integration']),task('deploy',['docker'],['test'])]
  result=build_schedule(dict(tasks=tasks,members=members,deadline_days=25))
  # Docker and database expertise are genuinely absent: never invent credentials.
  self.assertFalse(result['all_tasks_scheduled'])
  reasons=' '.join(x['reason'] for x in result['unscheduled_tasks'])
  self.assertIn('docker',reasons)
  self.assertIn('sql',reasons)
