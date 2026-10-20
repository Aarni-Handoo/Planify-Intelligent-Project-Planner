import unittest
from scheduler.intelligence import normalize_skill, normalize_skills, project_plan
from scheduler.engine import build_schedule

class IntelligenceTests(unittest.TestCase):
    def test_aliases(self):
        self.assertEqual(normalize_skill('web prgm')['canonical'],'web development')
        self.assertEqual(normalize_skill('pghnon')['canonical'],'python')
        self.assertEqual(normalize_skill('pyhton')['canonical'],'python')
    def test_java_not_javascript(self):
        self.assertEqual(normalize_skill('java')['canonical'],'java')
        self.assertEqual(normalize_skill('javascript')['canonical'],'javascript')
    def test_school_mess(self):
        plan=project_plan('School Mess Food Maker App')
        self.assertEqual(plan['detected_domain'],'mess')
        self.assertTrue(any('meal' in t['title'].lower() for t in plan['tasks']))
    def test_schedule_typo(self):
        p={'deadline_days':1,'members':[{'id':'A','skills':['pghnon'],'daily_capacity':5}],
           'tasks':[{'id':'T1','required_skills':['python'],'estimated_hours':3,'dependencies':[]}]}
        self.assertTrue(build_schedule(p)['all_tasks_scheduled'])
    def test_collaboration_with_alias(self):
        p={'deadline_days':1,'members':[{'id':'A','skills':['pyhton'],'daily_capacity':5},
           {'id':'B','skills':['reactjs'],'daily_capacity':5}],
           'tasks':[{'id':'T1','required_skills':['python','react'],'estimated_hours':6,'dependencies':[]}]}
        self.assertTrue(build_schedule(p)['all_tasks_scheduled'])
if __name__=='__main__': unittest.main()
