"""Import user-provided TV1 run and TV5 repair evidence without publishing logs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
import import_member_artifacts as importer

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'summaries/milestone1/updated-20261107'


def load_archive(path):
    archive = zipfile.ZipFile(path)
    if archive.testzip() is not None:
        raise ValueError('Corrupt ZIP')
    return archive


def save(directory, name, raw, provenance):
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe archive member')
    target = directory / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() != raw:
        raise ValueError(f'Refusing to overwrite {target}')
    target.write_bytes(raw)
    provenance['files'][name] = dict(original_sha256=importer.digest(raw), published_sha256=importer.digest(raw))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tv1', type=Path, required=True)
    parser.add_argument('--tv5-retry', type=Path, required=True)
    parser.add_argument('--tv5-audit', type=Path, required=True)
    args = parser.parse_args()
    for role, path in [('TV1', args.tv1), ('TV5', args.tv5_audit)]:
        directory = DEST / role
        if directory.exists():
            raise ValueError('Immutable destination already exists')
        if role == 'TV5':
            shutil.copytree(ROOT/'summaries/milestone1/preliminary-20261104/TV5', directory)
            provenance = json.loads((directory/'provenance.json').read_text(encoding='utf-8'))
        else:
            directory.mkdir(parents=True)
            provenance = dict(archive_name=path.name, archive_sha256=importer.digest(path.read_bytes()),
                              drive_url='', files={})
        provenance['checked_on'] = '2026-11-07'
        provenance['supplementary_archives'] = []
        with load_archive(path) as archive:
            if role == 'TV1':
                for name in archive.namelist():
                    if Path(name).name not in importer.ALLOWED:
                        continue
                    raw = archive.read(name)
                    public = raw
                    if Path(name).name in {'benchmark.json', 'run.json'}:
                        doc = json.loads(raw)
                        command = doc.get('command', [])
                        doc['command'] = [v for i,v in enumerate(command) if i != 0
                            and v not in {'--output','--timings'}
                            and command[i-1] not in {'--output','--timings'}]
                        doc.pop('output_dir', None)
                        doc.get('environment', {}).pop('executable', None)
                        public = (json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
                    save(directory,name,public,provenance)
                    provenance['files'][name]['original_sha256'] = importer.digest(raw)
            else:
                # Keep the historical benchmark, replace only the selected full-range audit.
                audit = json.loads(archive.read('assignment-audit.json'))
                expected = {f'2410.{i:05d}' for i in range(3025,8025)}
                assert {p['paper_id'] for p in audit['paper_results']} == expected
                assert audit['assigned_input_count']==5000 and audit['unresolved_discovery_ids']==[]
                raw=archive.read('assignment-audit.json')
                target=directory/'assignment-audit.json'
                target.write_bytes(raw)
                provenance['files']['assignment-audit.json'] = dict(original_sha256=importer.digest(raw),published_sha256=importer.digest(raw))
                save(directory,'source-retry/source-results.json',archive.read('source-results.json'),provenance)
                provenance['supplementary_archives'].append(dict(archive_name=path.name,sha256=importer.digest(path.read_bytes())))
        if role == 'TV5':
            with load_archive(args.tv5_retry) as archive:
                raw=archive.read('after-status.json')
                doc=json.loads(raw)
                assert len(doc)==4 and all(v['status']=='success' for v in doc.values())
                save(directory,'lookup-retry/after-status.json',raw,provenance)
                save(directory,'lookup-retry/retry-results.json',archive.read('retry-results.json'),provenance)
            provenance['supplementary_archives'].append(dict(archive_name=args.tv5_retry.name,sha256=importer.digest(args.tv5_retry.read_bytes())))
        provenance['note'] = ('User-provided local archive; no independent live-corpus inspection. '
            'TV1 statistics cover only six IDs; inputs.json is not an executed audit. '
            'TV5 retains its historical benchmark and uses the separate full-range audit from 7 November. '
            'Private backups and pipeline logs are not published.')
        (directory/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    main()
