"""Protect reporting conclusions against missing or contradictory evidence."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'utils'))
from preliminary_results import load_members, coverage_rows, performance_rows, audit_assessment


class PreliminaryResultsTests(unittest.TestCase):
    def test_real_artifacts_do_not_claim_completion(self):
        members = load_members(ROOT)
        rows = {r['Thành viên']: r for r in coverage_rows(members)}
        self.assertIsNone(rows['TV1']['Unseen IDs'])
        self.assertIsNone(rows['TV3']['Unseen IDs'])
        self.assertIsNone(rows['TV4']['Unresolved IDs'])
        self.assertIn('mâu thuẫn', rows['TV2']['Đánh giá'])
        self.assertEqual(rows['TV2']['Dải audit xác minh'], 'Có')
        self.assertEqual(rows['TV5']['Unseen IDs'], 0)
        self.assertEqual(rows['TV5']['Unresolved IDs'], 4)
        self.assertEqual(rows['TV5']['Validation Pass/Fail'], '4617 / 379')

    def test_sparse_ram_is_not_presented_as_representative(self):
        rows = {r['Thành viên']: r for r in performance_rows(load_members(ROOT))}
        for member in ['TV2', 'TV4', 'TV5']:
            self.assertIsNone(rows[member]['Peak RSS MiB (quan sát)'])
            self.assertIsNone(rows[member]['Mean RSS MiB'])
        self.assertGreater(rows['TV3']['Peak RSS MiB (quan sát)'], 0)

    def test_unverified_range_cannot_be_complete(self):
        audit = dict(audit_complete=True, unseen_ids=[], unresolved_discovery_ids=[],
                     validation_fail_papers=0, diagnostics=[])
        self.assertIn('Chưa xác minh', audit_assessment(audit, False))


if __name__ == '__main__':
    unittest.main()
