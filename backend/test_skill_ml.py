import unittest
from scheduler.skill_ml import compatible
from scheduler.engine import build_schedule

class SkillMLTests(unittest.TestCase):
    def test_domskill(self):self.assertTrue(compatible('DOMSKILL',['JavaScript'])['match'])
    def test_debugging_paraphrase(self):self.assertTrue(compatible('finding errors',['debugging'])['match'])
    def test_arrays_language_specific(self):
        self.assertTrue(compatible('2D array in C',['C'])['match'])
        self.assertFalse(compatible('2D array in C',['Python'])['match'])
    def test_sql(self):self.assertTrue(compatible('data manipulation in dbms',['SQL'])['match'])
    def test_hard_negative(self):
        self.assertFalse(compatible('kubernetes',['docker'])['match'])
        self.assertFalse(compatible('git',['react'])['match'])
    def test_scheduler_uses_compatibility(self):
        tasks=[{'id':'T1','title':'DOM binding','required_skills':['DOMSKILL'],'estimated_hours':3,'priority':'high','dependencies':[]}]
        members=[{'id':'M1','name':'Aarav','skills':['javascript'],'daily_capacity':5}]
        result=build_schedule({'tasks':tasks,'members':members,'deadline_days':2})
        self.assertTrue(result['all_tasks_scheduled'])
if __name__=='__main__':unittest.main()
