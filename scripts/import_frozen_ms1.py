"""Reproduce the frozen report inventory from the four ZIPs and TV2 audit.

Input directory must contain TV1-final.zip, TV3-final.zip, TV4-final.zip,
TV5-final.zip and TV2-assignment-audit.json, downloaded from the reviewed sources.
The existing provenance identifies original SHA-256 and entry SHA-256.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args()
    target=ROOT/'summaries/milestone1/frozen-20261127'
    receipt=json.loads((target/'provenance.json').read_bytes())
    papers=[]
    for source in receipt['sources']:
        member=source['member']
        path=args.input/('TV2-assignment-audit.json' if member=='TV2' else member+'-final.zip')
        original=path.read_bytes()
        if hashlib.sha256(original).hexdigest()!=source['original_sha256']:
            raise ValueError('Original source hash mismatch: '+member)
        if member=='TV2':
            raw=original
            rows=json.loads(raw)['paper_results']
        else:
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None: raise ValueError('Corrupt ZIP')
                raw=archive.read(source['entry'])
                rows=[dict(p['validation'],discovery_status=p['record']['status'],
                           discovery_versions=len(p['record']['versions'])) for p in json.loads(raw)['papers']]
        if hashlib.sha256(raw).hexdigest()!=source['entry_sha256']:
            raise ValueError('Source entry hash mismatch: '+member)
        if len(rows)!=5000 or len({r['paper_id'] for r in rows})!=5000:
            raise ValueError('Invalid paper coverage: '+member)
        for p in rows:
            papers.append(dict(member=member,paper_id=p['paper_id'],valid=p['valid'],counts=p['counts'],
                discovery_status=p.get('discovery_status','success'),
                discovery_versions=p.get('discovery_versions',p['counts']['versions']),
                error_codes=sorted({e.get('code','unknown') for e in p.get('errors',[])})))
    raw=(json.dumps({'scope':'frozen_group_ms1','papers':papers},ensure_ascii=False,indent=2)+'\n').encode()
    if hashlib.sha256(raw).hexdigest()!=receipt['public_sha256']:
        raise ValueError('Derived report inventory differs from reviewed snapshot')
    destination=target/'corpus.json'
    if destination.exists() and destination.read_bytes()!=raw:
        raise ValueError('Refusing to replace different evidence')
    destination.write_bytes(raw)
    print('Verified frozen inventory:',len(papers),'papers')


if __name__=='__main__': main()
