"""Load a chosen run consistently for both notebooks; never silently substitute demo data."""
import json
import os
from pathlib import Path


def load_run(book_root):
    root = Path(book_root).resolve() / 'summaries/milestone1'
    name = os.environ.get('TV5_RUN', 'demo')
    selected = (root / name).resolve()
    if not selected.is_relative_to(root.resolve()):
        raise ValueError('TV5_RUN must stay within summaries/milestone1')
    benchmark = json.loads((selected / 'benchmark.json').read_text(encoding='utf-8'))
    summary = json.loads((selected / 'statistics.json').read_text(encoding='utf-8'))
    samples = [json.loads(line) for line in (selected / 'samples.jsonl').read_text().splitlines() if line.strip()]
    if benchmark['label'] != summary['label']:
        raise ValueError('Benchmark and statistics labels differ')
    return name, summary, benchmark, samples
