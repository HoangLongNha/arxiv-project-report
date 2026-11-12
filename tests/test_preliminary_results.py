"""Protect reporting conclusions against missing or contradictory evidence."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'utils'))
from preliminary_results import load_members, coverage_rows, performance_rows, audit_assessment
from preliminary_results import progress_rows, assignment_outcomes, session_members, corpus_metrics, validate_cumulative


class PreliminaryResultsTests(unittest.TestCase):
    def test_real_artifacts_do_not_claim_completion(self):
        members = load_members(ROOT)
        rows = {r['Thành viên']: r for r in coverage_rows(members)}
        self.assertEqual(rows['TV1']['Unseen IDs'],0)
        self.assertEqual(rows['TV1']['Validation Pass/Fail'],'4315 / 685')
        self.assertEqual(rows['TV3']['Unseen IDs'], 0)
        self.assertEqual(rows['TV4']['Unresolved IDs'], 0)
        self.assertEqual(rows['TV3']['Validation Pass/Fail'], '4820 / 180')
        self.assertEqual(rows['TV4']['Validation Pass/Fail'], '4882 / 118')
        self.assertEqual(rows['TV3']['Audit Complete (gốc)'], 'false')
        self.assertEqual(rows['TV4']['Audit Complete (gốc)'], 'false')
        self.assertEqual(rows['TV2']['Audit Complete (gốc)'], 'false')
        self.assertIn('version', rows['TV2']['Đánh giá'])
        self.assertEqual(rows['TV2']['Dải audit xác minh'], 'Có')
        self.assertEqual(rows['TV5']['Unseen IDs'], 0)
        self.assertEqual(rows['TV5']['Unresolved IDs'], 0)
        self.assertEqual(rows['TV5']['Validation Pass/Fail'], '4620 / 380')

    def test_sparse_ram_is_not_presented_as_representative(self):
        rows = {r['Thành viên']: r for r in performance_rows(load_members(ROOT))}
        for member in ['TV2', 'TV5']:
            self.assertIsNone(rows[member]['Peak RSS MiB (quan sát)'])
            self.assertIsNone(rows[member]['Mean RSS MiB'])
        self.assertGreater(rows['TV3']['Peak RSS MiB (quan sát)'], 0)
        self.assertGreater(rows['TV4']['Peak RSS MiB (quan sát)'], 0)

    def test_unverified_range_cannot_be_complete(self):
        audit = dict(audit_complete=True, unseen_ids=[], unresolved_discovery_ids=[],
                     validation_fail_papers=0, diagnostics=[])
        self.assertIn('Chưa xác minh', audit_assessment(audit, False))

    def test_group_report_and_verified_coverage_stay_separate(self):
        members = load_members(ROOT)
        rows = {r['Thành viên']: r for r in progress_rows(members)}
        self.assertEqual(sum(r['Đã chạy theo báo cáo nhóm'] for r in rows.values()), 25000)
        for member in ['TV1']:
            self.assertEqual(rows[member]['ID có kết quả ghi nhận'], 5000)
            self.assertEqual(rows[member]['Lookup còn lỗi'], 0)
        self.assertEqual(rows['TV5']['ID có kết quả ghi nhận'], 5000)
        self.assertEqual(rows['TV5']['Lookup còn lỗi'], 0)
        for member in ['TV3','TV4']:
            self.assertEqual(rows[member]['ID có kết quả ghi nhận'], 5000)
            self.assertEqual(rows[member]['ID chưa ghi nhận'], 0)
            self.assertEqual(rows[member]['Lookup còn lỗi'], 0)
        tv1 = next(m for m in members if m['member']=='TV1')
        self.assertIsNone(tv1['statistics'])
        self.assertTrue(tv1['verified'])
        self.assertEqual(tv1['audit']['discovery_statuses']['success'],5000)
        self.assertEqual(next(m for m in members if m['member']=='TV5')['audit']['known_version_count'],8348)
        full = {r['Thành viên']: r for r in assignment_outcomes(members)}
        self.assertEqual(full['TV3']['Paper phát hiện thành công'], 5000)

    def test_supplementary_sessions_are_not_added_to_assignment_counts(self):
        members = load_members(ROOT)
        sessions = session_members(ROOT, members)
        self.assertEqual(len(sessions), 8)
        self.assertEqual(sum(s['member'] == 'TV4' for s in sessions), 3)
        self.assertEqual(len({s['benchmark']['run_id'] for s in sessions}), len(sessions))
        self.assertEqual(len(progress_rows(members)), 5)

    def test_weighted_inventory_totals_use_repaired_tv5_snapshot(self):
        members=load_members(ROOT)
        rows=corpus_metrics(members)
        total=rows[-1]
        self.assertEqual(total['assigned'],25000)
        self.assertEqual(total['discovered'],25000)
        self.assertEqual(total['versions'],40683)
        self.assertEqual(total['references'],904844)
        self.assertEqual(total['source_files'],37145)
        self.assertEqual(total['paired'],22149)
        self.assertAlmostEqual(total['mean_references'],904844/22383)
        expected=sum(r['mean_before']*r['paired'] for r in rows[:-1])/22149
        self.assertAlmostEqual(total['mean_before'],expected)
        self.assertNotAlmostEqual(total['mean_before'],sum(r['mean_before'] for r in rows[:-1])/4)
        tv5=next(m for m in members if m['member']=='TV5')
        self.assertEqual(tv5['audit']['discovery_statuses']['success'],5000)
        self.assertEqual(tv5['cumulative']['counts']['discovery_success_papers'],5000)
        self.assertEqual(tv5['cumulative']['unresolved_discovery_ids'],[])
        old=ROOT/'summaries/milestone1/cumulative/TV5/cumulative-statistics.json'
        import json
        self.assertEqual(json.loads(old.read_bytes())['counts']['discovery_success_papers'],4996)

    def test_inconsistent_inventory_totals_are_rejected(self):
        import copy
        doc=copy.deepcopy(next(m for m in load_members(ROOT) if m['member']=='TV3')['cumulative'])
        doc['counts']['references']+=1
        with self.assertRaisesRegex(ValueError,'totals mismatch'):
            validate_cumulative(doc,'TV3')

    def test_resume_statistics_are_not_promoted_to_cumulative(self):
        members = load_members(ROOT)
        tv1=next(m for m in members if m['member']=='TV1')
        self.assertEqual(tv1['cumulative']['counts']['recorded_ids'],5000)
        self.assertEqual(len(tv1['cumulative']['unseen_ids']),0)
        self.assertTrue(tv1['verified'])
        self.assertEqual(tv1['audit']['discovered_assigned_ids'],5000)
        self.assertIn('TV1',[r['member'] for r in corpus_metrics(members)])
        self.assertEqual(sum(m['cumulative'] is not None for m in members),5)
        tv3 = next(m for m in members if m['member']=='TV3')
        self.assertEqual(tv3['statistics']['counts']['papers'], 828)
        self.assertTrue(tv3['verified'])


if __name__ == '__main__':
    unittest.main()
