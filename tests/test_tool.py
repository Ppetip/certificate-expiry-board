import unittest
import tool

class BehaviorTests(unittest.TestCase):
    def test_case_0(self):
        self.assertEqual([x["kind"] for x in tool.analyze({'now': '2026-01-01T00:00:00Z', 'certificates': []})], [])

    def test_case_1(self):
        self.assertEqual([x["kind"] for x in tool.analyze({'now': '2026-01-01T00:00:00Z', 'certificates': [{'name': 'x', 'not_before': '2025-01-01T00:00:00Z', 'not_after': '2026-01-01T00:00:00Z'}]})], ['expired'])

    def test_case_2(self):
        self.assertEqual([x["kind"] for x in tool.analyze({'now': '2026-01-01T00:00:00Z', 'certificates': [{'name': 'x', 'not_before': '2027-01-01T00:00:00Z', 'not_after': '2028-01-01T00:00:00Z'}]})], ['not_yet_valid'])

    def test_missing_required_input(self):
        with self.assertRaises((KeyError, ValueError, TypeError)):
            tool.analyze({})


    def test_timezone_equivalence(self):
        cert={'name':'x','not_before':'2025-01-01T00:00:00Z','not_after':'2026-01-01T01:00:00+01:00'}
        self.assertEqual(tool.analyze({'now':'2026-01-01T00:00:00Z','certificates':[cert]})[0]['kind'],'expired')
    def test_invalid_validity_rejected(self):
        with self.assertRaises(ValueError): tool.analyze({'now':'2026-01-01T00:00:00Z','certificates':[{'name':'x','not_before':'2027-01-01T00:00:00Z','not_after':'2026-01-01T00:00:00Z'}]})
