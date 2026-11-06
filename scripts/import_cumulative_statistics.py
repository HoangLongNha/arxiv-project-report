"""Validate a received whole-assignment statistics JSON and preserve its original bytes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'utils'))
from preliminary_results import RANGES, validate_cumulative


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--member', choices=RANGES, required=True)
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    validate_cumulative(json.loads(raw), args.member)
    folder = ROOT / 'summaries/milestone1/cumulative' / args.member
    if folder.exists():
        parser.error('An import already exists; preserve it and choose a new reviewed snapshot')
    folder.mkdir(parents=True)
    (folder / 'cumulative-statistics.json').write_bytes(raw)
    receipt = dict(imported_at=datetime.now(timezone.utc).isoformat(),
                   original_filename=args.input.name, sha256=hashlib.sha256(raw).hexdigest())
    (folder / 'provenance.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
