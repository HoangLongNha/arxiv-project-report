"""Cumulative scans must include earlier sessions and avoid cached-state double counting."""
import json
import hashlib
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'utils'))
from cumulative_statistics import summarize
sys.path.insert(0, str(ROOT / 'scripts'))
from export_cumulative_ms1 import main as export_main


class CumulativeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, doc):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc), encoding='utf-8')

    def paper(self, identifier, refs=None):
        rec = dict(arxiv_id=identifier, status='success', versions=[dict(version=1)])
        self.write(f'state/discovery/{identifier}.json', rec)
        for stage, artifact in [('download', {'source':f'raw/{identifier}/v1/source'}),
                                ('extract', {'corpus':f'corpus/{identifier}/v1'}),
                                ('metadata', {}), ('references', {})]:
            version = 1 if stage in {'download','extract'} else None
            status = 'no_data' if stage == 'references' and not refs else 'success'
            self.write(f'state/stages/{stage}/{identifier}/{version or "paper"}.json',
                       dict(stage=stage,paper_id=identifier,version=version,status=status,artifacts=artifact))
        self.write(f'raw/{identifier}/v1/source', {'raw':'source'})
        self.write(f'raw/{identifier}/v1/download_metadata.json', {'raw_size_bytes':50})
        self.write(f'corpus/{identifier}/v1/extract_metadata.json', {'raw_size_bytes':100,'corpus_size_bytes':10})
        self.write(f'corpus/{identifier}/v1/main.tex', {'text':'TeX'})
        self.write(f'metadata/{identifier}.json', {'arxiv_id':identifier})
        self.write(f'references/{identifier}.json', refs or [])
        self.write(f'validation/{identifier}.json', {'valid':True})
        return rec

    def scan(self):
        return summarize(self.root, '2410.00001:2410.00002', 'TV5')

    def test_includes_earlier_sessions_when_last_manifest_has_one_paper(self):
        self.paper('2410.00001')
        latest = self.paper('2410.00002')
        self.write('manifests/discovery.json', [latest])
        before = {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        report = self.scan()
        after = {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(report['counts']['recorded_ids'], 2)
        self.assertEqual(report['counts']['expected_versions'], 2)
        self.assertEqual(report['counts']['source_versions_verified'], 2)
        self.assertEqual(report['sizes']['paired_papers'], 2)
        self.assertEqual(report['sizes']['mean_before_bytes'], 100)
        self.assertEqual(before, after)

    def test_deduplicates_manifest_and_reference_rows(self):
        ref = dict(ref_s2_id='same',ref_arxiv_id='2401.00001',ref_title='A',ref_authors=['B'],ref_submission_date='2024')
        rec = self.paper('2410.00001', [ref, ref])
        self.write('manifests/discovery.json', [rec, rec])
        report = self.scan()
        self.assertEqual(report['counts']['recorded_ids'], 1)
        self.assertEqual(report['counts']['references'], 1)
        self.assertEqual(report['references']['duplicate_rows'], 1)
        self.assertEqual(report['unseen_ids'], ['2410.00002'])

    def test_hashed_checkpoint_names_include_previous_sessions(self):
        for identifier in ['2410.00001','2410.00002']:
            self.paper(identifier)
            source=self.root/f'state/discovery/{identifier}.json'
            source.rename(source.with_name(hashlib.sha256(identifier.encode()).hexdigest()+'.json'))
        self.write('manifests/discovery.json', [dict(arxiv_id='2410.00002',status='success',versions=[dict(version=1)])])
        report=self.scan()
        self.assertEqual(report['counts']['recorded_ids'],2)
        self.assertEqual(report['unseen_ids'],[])
        self.assertEqual(report['counts']['source_versions_verified'],2)

    def test_checkpoint_error_supersedes_old_success_manifest(self):
        rec = self.paper('2410.00001')
        self.write('manifests/discovery.json', [rec])
        self.write('state/discovery/2410.00001.json', dict(arxiv_id='2410.00001',status='api_error'))
        report = self.scan()
        self.assertEqual(report['counts']['discovery_success_papers'], 0)
        self.assertEqual(report['unresolved_discovery_ids'], ['2410.00001'])

    def test_missing_source_is_not_verified_from_success_status_alone(self):
        self.paper('2410.00001')
        (self.root/'raw/2410.00001/v1/source').unlink()
        report = self.scan()
        self.assertEqual(report['download_statuses']['success'], 1)
        self.assertEqual(report['counts']['source_versions_verified'], 0)

    def test_failed_reference_is_not_an_empty_success(self):
        self.paper('2410.00001')
        self.paper('2410.00002')
        self.write('state/stages/references/2410.00002/paper.json',
                   dict(stage='references',paper_id='2410.00002',version=None,status='api_error'))
        report = self.scan()
        self.assertEqual(report['counts']['retrieved_reference_papers'], 1)
        self.assertEqual(report['references']['mean_per_retrieved_paper'], 0)

    def test_concurrent_change_rejects_snapshot(self):
        self.paper('2410.00001')
        original = Path.read_bytes
        reads = 0
        def changing(path):
            nonlocal reads
            if path.name == '2410.00001.json' and path.parent.name == 'discovery':
                reads += 1
                if reads == 2:
                    path.write_text('{}', encoding='utf-8')
            return original(path)
        with patch.object(Path, 'read_bytes', changing):
            with self.assertRaisesRegex(ValueError, 'changed'):
                self.scan()

    def test_export_refuses_destination_inside_corpus(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            export_main(['--member','TV5','--output',str(self.root),
                         '--save',str(self.root/'statistics.json'),'--writers-stopped'])
        self.assertFalse((self.root/'statistics.json').exists())

    def test_export_requires_stopped_writer_confirmation(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            export_main(['--member','TV5','--output',str(self.root),
                         '--save',str(self.root.parent/'report.json')])
