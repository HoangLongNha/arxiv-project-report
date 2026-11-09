"""Import reviewed TV1/TV2 audit updates while preserving older evidence."""
import argparse
import json
from pathlib import Path
import shutil
import zipfile
import import_member_artifacts as base

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'summaries/milestone1/updated-20261109'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tv1',type=Path,required=True)
    parser.add_argument('--tv2-audit',type=Path,required=True)
    args=parser.parse_args()
    for member in ('TV1','TV2'):
        folder=DEST/member
        if folder.exists():
            raise ValueError('Refusing to overwrite an immutable evidence snapshot')
        if member=='TV1':
            folder.mkdir(parents=True)
            provenance=dict(checked_on='2026-11-09',archive_name=args.tv1.name,
                archive_sha256=base.digest(args.tv1.read_bytes()),drive_url='',files={})
            with zipfile.ZipFile(args.tv1) as archive:
                assert archive.testzip() is None
                for name in archive.namelist():
                    relative=Path(name)
                    if relative.name not in base.ALLOWED: continue
                    if relative.is_absolute() or '..' in relative.parts: raise ValueError('Unsafe path')
                    raw=archive.read(name); public=raw
                    if relative.name in {'run.json','benchmark.json'}:
                        doc=json.loads(raw); command=doc.get('command',[])
                        doc['command']=[v for i,v in enumerate(command) if i and v not in {'--output','--timings'}
                            and command[i-1] not in {'--output','--timings'}]
                        doc.pop('output_dir',None);doc.get('environment',{}).pop('executable',None)
                        public=(json.dumps(doc,ensure_ascii=False,indent=2)+'\n').encode()
                    target=folder/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(public)
                    provenance['files'][name]=dict(original_sha256=base.digest(raw),published_sha256=base.digest(public))
        else:
            shutil.copytree(ROOT/'summaries/milestone1/preliminary-20261104/TV2',folder)
            provenance=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
            raw=args.tv2_audit.read_bytes()
            (folder/'assignment-audit.json').write_bytes(raw)
            provenance['checked_on']='2026-11-09'
            provenance['files']['assignment-audit.json']=dict(original_sha256=base.digest(raw),published_sha256=base.digest(raw))
            provenance['supplementary_files']=[dict(filename=args.tv2_audit.name,sha256=base.digest(raw))]
        audit=json.loads((folder/'assignment-audit.json').read_bytes())
        first,last=(12872,17871) if member=='TV1' else (15788,20787)
        prefix='2508' if member=='TV1' else '2506'
        assert len(audit['paper_results'])==5000
        assert {p['paper_id'] for p in audit['paper_results']}=={f'{prefix}.{i:05d}' for i in range(first,last+1)}
        assert not audit['unseen_ids'] and not audit['unresolved_discovery_ids']
        assert audit['audit_complete'] is False
        provenance['note']='User-provided evidence. Audit and benchmark dates/scopes remain separate. No private logs or corpus are published.'
        (folder/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__': main()
