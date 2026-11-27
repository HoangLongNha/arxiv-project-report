"""Protect the group-level final results and their interpretation."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FrozenMS1Tests(unittest.TestCase):
    def setUp(self):
        folder = ROOT/'summaries/milestone1/frozen-20261127'
        raw = (folder/'corpus.json').read_bytes()
        receipt = json.loads((folder/'provenance.json').read_bytes())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt['public_sha256'])
        self.papers = json.loads(raw)['papers']

    def test_full_group_has_unique_papers_and_final_quality(self):
        self.assertEqual(len(self.papers), 25000)
        self.assertEqual(len({p['paper_id'] for p in self.papers}), 25000)
        self.assertEqual(sum(p['valid'] for p in self.papers), 24641)
        self.assertEqual(sum(p['counts']['references'] for p in self.papers), 1005198)

    def test_versions_are_summed_from_details(self):
        self.assertEqual(sum(p['discovery_versions'] for p in self.papers), 40683)
        tv2 = [p for p in self.papers if p['member']=='TV2']
        self.assertEqual(sum(p['discovery_versions'] for p in tv2), 7987)

    def test_final_report_does_not_assign_open_tasks_to_individuals(self):
        for name in ['preliminary-results.ipynb','performance.ipynb','discussion.md']:
            text = (ROOT/'milestone1'/name).read_text(encoding='utf-8')
            self.assertNotIn('TV5 còn', text)
            self.assertNotIn('cần xuất lại', text)


if __name__ == '__main__':
    unittest.main()
