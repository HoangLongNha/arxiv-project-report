"""Export accumulated corpus statistics offline; never invoke a crawler or edit corpus files."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'utils'))
from cumulative_statistics import summarize

RANGES = dict(TV1='2508.12872:2508.17871', TV2='2506.15788:2506.20787',
              TV3='2411.08799:2411.13798', TV4='2410.18025:2410.23024', TV5='2410.03025:2410.08024')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--member', choices=RANGES, required=True)
    parser.add_argument('--output', type=Path, required=True, help='Existing data/ root, read only')
    parser.add_argument('--save', type=Path, required=True, help='New JSON outside data/; no overwrite')
    parser.add_argument('--writers-stopped', action='store_true', help='Confirm pipeline/audit writers have stopped')
    args = parser.parse_args(argv)
    if not args.writers_stopped:
        parser.error('Stop pipeline and audit writers first, then pass --writers-stopped')
    target, source = args.save.resolve(), args.output.resolve()
    if target.is_relative_to(source) or target.exists():
        parser.error('Save to a new file outside the corpus root')
    report = summarize(source, RANGES[args.member], args.member)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(dict(member=args.member, counts=report['counts'],
                          unseen=len(report['unseen_ids']), unresolved=len(report['unresolved_discovery_ids']),
                          diagnostics=len(report['diagnostics']), saved=str(target))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
