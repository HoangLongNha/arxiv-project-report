"""Import immutable report evidence; never extract a ZIP into a corpus directory."""
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'summaries/milestone1/preliminary-20261104'
SOURCES = {
    'TV2': ('tv2-artifacts.zip', '1LKh8kYa-Y05kka8gQsZmMr5BHxoVJa66'),
    'TV3': ('tv3-artifacts.zip', '1BOHcygxqjmWErfJLAYJT2qpbq23Q4mJy'),
    'TV4': ('tv4-artifacts.zip', '16X_IelLnODvrIoJaY4WBgBuQ-vULPTjm'),
    'TV5': ('TV_tv5_MS1_RESULTS_run_20261102T165345Z_4ab59b82a8794c90a708b6f83eaaf7ac.zip',
            '1_sN3CUnnL-ROt6vaA6wwklhCQXJtF-hb'),
}
ALLOWED = {'assignment-audit.json', 'inputs.json', 'benchmark.json', 'run.json',
           'statistics.json', 'statistics-revalidated.json', 'statistics_error.json',
           'summary.json', 'samples.jsonl', 'timings.jsonl'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    for member, (filename, drive_id) in SOURCES.items():
        raw = (ROOT.parent / filename).read_bytes()
        archive = zipfile.ZipFile(io.BytesIO(raw))
        assert archive.testzip() is None
        nested = [n for n in archive.namelist() if n.endswith('.zip')]
        if nested:
            assert len(nested) == 1 and len(archive.namelist()) == 1
            archive = zipfile.ZipFile(io.BytesIO(archive.read(nested[0])))
            assert archive.testzip() is None
        target = DEST / member
        target.mkdir(parents=True, exist_ok=True)
        provenance = dict(checked_on=globals().get('CHECKED_ON', '2026-11-04'),
                          archive_name=globals().get('ARCHIVE_TITLES', {}).get(member, filename),
                          drive_url=f'https://drive.google.com/file/d/{drive_id}/view',
                          archive_sha256=digest(raw), files={},
                          note=globals().get('NOTE', 'Archive evidence only; no independent revalidation of live corpus. '
                               'TV5 uses the local ZIP with the same name/size as the shared Drive file.'))
        for name in archive.namelist():
            path = Path(name)
            if path.name not in ALLOWED:
                continue
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Unsafe archive member')
            original = archive.read(name)
            public = original
            if path.name in {'benchmark.json', 'run.json'}:
                doc = json.loads(original)
                # Keep scope/flags, omit local output paths and host executable.
                command = doc.get('command', [])
                doc['command'] = [v for i, v in enumerate(command)
                                  if i != 0 and v not in {'--output', '--timings'}
                                  and (i == 0 or command[i-1] not in {'--output', '--timings'})]
                doc.pop('output_dir', None)
                doc.get('environment', {}).pop('executable', None)
                public = (json.dumps(doc, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
            dest = target / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.read_bytes() != public:
                raise ValueError(f'Refusing to overwrite different evidence: {dest}')
            dest.write_bytes(public)
            provenance['files'][name] = dict(original_sha256=digest(original),
                                            published_sha256=digest(public))
        (target / 'provenance.json').write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
