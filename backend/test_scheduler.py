import unittest
from scheduler.engine import build_schedule

class SchedulerTests(unittest.TestCase):
    def test_shared_member_across_tasks(self):
        result = build_schedule({"deadline_days": 1, "tasks": [
            {"id": "T1", "required_skills": ["python", "machine learning"], "estimated_hours": 7, "priority": "high"},
            {"id": "T2", "required_skills": ["react", "testing"], "estimated_hours": 6, "priority": "high"}],
            "members": [
                {"id": "A", "skills": ["python", "react"], "daily_capacity": 5},
                {"id": "B", "skills": ["python", "machine learning"], "daily_capacity": 5},
                {"id": "C", "skills": ["react", "testing"], "daily_capacity": 5}]})
        self.assertTrue(result['all_tasks_scheduled'])
        self.assertEqual(set(a['task_id'] for a in result['assignments'] if a['member_id']=='A'), {'T1','T2'})
        self.assertTrue(all(m['daily_hours']['1'] <= m['daily_capacity'] for m in result['member_workload']))
        self.assertAlmostEqual(sum(a['hours'] for a in result['assignments']), 13)

    def test_complementary_specialists(self):
        result = build_schedule({"deadline_days": 3,
            "tasks": [{"id": "T1", "required_skills": ["python", "react"], "estimated_hours": 8}],
            "members": [{"id": "M1", "skills": ["python"], "daily_capacity": 5},
                        {"id": "M2", "skills": ["react"], "daily_capacity": 5}]})
        self.assertTrue(result['all_tasks_scheduled'])
        self.assertEqual(set(result['task_teams'][0]['contributors']), {'M1','M2'})

    def test_dependencies(self):
        result = build_schedule({"deadline_days": 3,
            "tasks": [{"id": "T1", "required_skills": ["sql"], "estimated_hours": 6},
                      {"id": "T2", "required_skills": ["python"], "estimated_hours": 8, "dependencies": ["T1"]}],
            "members": [{"id": "M1", "skills": ["sql", "python"], "daily_capacity": 5}]})
        t1days = [a['day'] for a in result['assignments'] if a['task_id']=='T1']
        t2days = [a['day'] for a in result['assignments'] if a['task_id']=='T2']
        self.assertTrue(t2days and min(t2days) > max(t1days))
        self.assertFalse(result['all_tasks_scheduled'])

    def test_missing_skills(self):
        result = build_schedule({"deadline_days": 2,
            "tasks": [{"id": "T1", "required_skills": ["rust"], "estimated_hours": 4}],
            "members": [{"id": "M1", "skills": ["python"], "daily_capacity": 5}]})
        self.assertFalse(result['all_tasks_scheduled'])
        self.assertIn('rust', result['unscheduled_tasks'][0]['reason'])

if __name__ == '__main__':
    unittest.main()
