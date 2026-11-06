"""Read a complete assigned range from accumulated checkpoints without crawling or rewriting data."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


def expand(spec):
    match = re.fullmatch(r'(\d{4})\.(\d{5}):(\d{4})\.(\d{5})', spec)
    if not match or match[1] != match[3] or int(match[2]) > int(match[4]):
        raise ValueError('Expected an ascending same-month arXiv range')
    return {f'{match[1]}.{n:05d}' for n in range(int(match[2]), int(match[4])+1)}


def summarize(output_dir, assigned_range, member):
    root = Path(output_dir).resolve()
    if not root.is_dir():
        raise ValueError('Corpus root does not exist')
    expected = expand(assigned_range)
    diagnostics, observed, directories = [], {}, {}

    def path(relative):
        p = (root / relative).resolve()
        if not p.is_relative_to(root):
            raise ValueError('Artifact path escapes corpus root')
        return p

    def signature(p):
        if not p.is_file():
            return None
        st = p.stat()
        return [st.st_size, st.st_mtime_ns]

    def read(relative):
        p = path(relative)
        if not p.is_file():
            observed[relative] = (None, None)
            return None
        before = signature(p)
        raw = p.read_bytes()
        after = signature(p)
        if before != after:
            raise ValueError(f'Data changed while reading {relative}')
        observed[relative] = (after, hashlib.sha256(raw).hexdigest())
        try:
            return json.loads(raw)
        except (ValueError, UnicodeError):
            diagnostics.append(dict(path=relative, problem='Unreadable JSON'))
            return None

    def exists(relative):
        p = path(relative)
        info = signature(p)
        observed[relative] = (info, None)
        return info is not None and info[0] > 0

    manifest = read('manifests/discovery.json')
    manifest = manifest if isinstance(manifest, list) else []
    fallback = {}
    for rec in manifest:
        if isinstance(rec, dict):
            identifier = rec.get('arxiv_id') or rec.get('input_id')
            if identifier in expected:
                fallback[identifier] = rec
    selected = {}
    for identifier in sorted(expected):
        relative = f'state/discovery/{identifier}.json'
        record = read(relative)
        # A corrupt existing checkpoint must not silently fall back to an older success.
        if observed[relative][0] is None:
            record = fallback.get(identifier)
        if not isinstance(record, dict) or not isinstance(record.get('status'), str):
            continue
        if (record.get('arxiv_id') or record.get('input_id')) != identifier:
            diagnostics.append(dict(path=relative, problem='Discovery identity mismatch'))
            continue
        selected[identifier] = record

    def stage(name, identifier, version=None):
        relative = f'state/stages/{name}/{identifier}/{version or "paper"}.json'
        doc = read(relative)
        if (not isinstance(doc, dict) or not isinstance(doc.get('status'), str)
                or not isinstance(doc.get('artifacts', {}), dict)
                or (doc.get('stage'), doc.get('paper_id'), doc.get('version')) != (name, identifier, version)):
            diagnostics.append(dict(path=relative, problem='Missing/mismatched stage checkpoint'))
            return dict(status='missing', artifacts={})
        return doc

    papers, versions, before_values, after_values = [], [], [], []
    totals = Counter()
    discovery = Counter(r.get('status', 'missing') for r in selected.values())
    for identifier, record in sorted(selected.items()):
        if record.get('status') != 'success':
            continue
        items = record.get('versions')
        numbers = [v.get('version') for v in items] if isinstance(items, list) and all(isinstance(v, dict) for v in items) else []
        if not numbers or any(type(n) is not int for n in numbers) or sorted(numbers) != list(range(1, len(numbers)+1)):
            diagnostics.append(dict(path=identifier, problem='Invalid/incomplete version list'))
            totals['unknown_version_papers'] += 1
            numbers = []
        paired, before, after, complete = bool(numbers), 0, 0, bool(numbers)
        for n in sorted(numbers):
            dl, ex = stage('download', identifier, n), stage('extract', identifier, n)
            source = f'raw/{identifier}/v{n}/source'
            source_ok = dl['status'] == 'success' and dl.get('artifacts', {}).get('source') == source and exists(source)
            totals['source_versions_verified'] += bool(source_ok)
            dlmeta = read(f'raw/{identifier}/v{n}/download_metadata.json') if source_ok else None
            exmeta = read(f'corpus/{identifier}/v{n}/extract_metadata.json') if ex['status'] == 'success' else None
            b = exmeta.get('raw_size_bytes') if isinstance(exmeta, dict) else None
            a = exmeta.get('corpus_size_bytes') if isinstance(exmeta, dict) else None
            if type(b) is int and b >= 0 and type(a) is int and a >= 0:
                before += b
                after += a
            else:
                paired = False
            folder = path(f'corpus/{identifier}/v{n}')
            has_corpus = False
            if ex['status'] == 'success' and ex.get('artifacts', {}).get('corpus') == f'corpus/{identifier}/v{n}':
                entries = sorted(folder.rglob('*')) if folder.is_dir() else []
                directories[f'corpus/{identifier}/v{n}'] = [p.relative_to(root).as_posix() for p in entries]
                for p in entries:
                    if p.is_file() and p.suffix.lower() in {'.tex', '.bib'}:
                        has_corpus |= exists(p.relative_to(root).as_posix())
            complete &= source_ok and has_corpus
            versions.append(dict(paper_id=identifier, version=n, download=dl['status'], extract=ex['status'],
                                 source_exists=bool(source_ok), corpus_exists=bool(has_corpus),
                                 package_bytes=dlmeta.get('raw_size_bytes') if isinstance(dlmeta, dict) else None))
        if paired:
            before_values.append(before)
            after_values.append(after)
        meta, refs = stage('metadata', identifier), stage('references', identifier)
        metadata_doc = read(f'metadata/{identifier}.json') if meta['status'] == 'success' else None
        totals['metadata_readable_papers'] += isinstance(metadata_doc, dict) and metadata_doc.get('arxiv_id') == identifier
        ref_count = None
        if refs['status'] in {'success', 'no_data'}:
            doc = read(f'references/{identifier}.json')
            if isinstance(doc, list) and all(isinstance(r, dict) for r in doc) and bool(doc) == (refs['status'] == 'success'):
                unique = {}
                for ref in doc:
                    s2, arxiv = ref.get('ref_s2_id'), ref.get('ref_arxiv_id')
                    key = ('s2', s2) if isinstance(s2, str) and s2 else (('arxiv', arxiv) if isinstance(arxiv, str) and arxiv else ('record', json.dumps(ref, sort_keys=True)))
                    if key in unique:
                        totals['duplicate_reference_rows'] += 1
                    unique[key] = ref
                ref_count = len(unique)
                totals['retrieved_reference_papers'] += 1
                totals['references'] += ref_count
                for ref in unique.values():
                    fields = ('ref_arxiv_id', 'ref_title', 'ref_authors', 'ref_submission_date', 'ref_s2_id')
                    totals['complete_references'] += all(ref.get(f) not in (None, '', []) for f in fields)
            else:
                diagnostics.append(dict(path=f'references/{identifier}.json', problem='Invalid/missing references outcome'))
        validation = read(f'validation/{identifier}.json')
        valid = validation.get('valid') if isinstance(validation, dict) else None
        papers.append(dict(paper_id=identifier, source_complete=bool(complete), metadata=meta['status'],
                           reference_status=refs['status'], references=ref_count,
                           validation_valid=valid if type(valid) is bool else None))

    # Recheck JSON bytes and artifact metadata after the scan; callers must stop writers first.
    for relative, (info, digest) in observed.items():
        p = path(relative)
        if signature(p) != info or (digest and hashlib.sha256(p.read_bytes()).hexdigest() != digest):
            raise ValueError(f'Data changed during scan: {relative}; stop writers and repeat')
    for relative, entries in directories.items():
        current = [p.relative_to(root).as_posix() for p in sorted(path(relative).rglob('*'))]
        if current != entries:
            raise ValueError(f'Data changed during scan: {relative}; stop writers and repeat')
    fingerprint = hashlib.sha256(json.dumps(observed, sort_keys=True).encode()).hexdigest()
    retrieved = totals['retrieved_reference_papers']
    counts = dict(assigned_ids=len(expected), recorded_ids=len(selected), discovery_success_papers=len(papers),
                  expected_versions=len(versions), unknown_version_papers=totals['unknown_version_papers'],
                  source_versions_verified=totals['source_versions_verified'],
                  source_complete_papers=sum(p['source_complete'] for p in papers),
                  metadata_readable_papers=totals['metadata_readable_papers'], references=totals['references'],
                  retrieved_reference_papers=retrieved)
    return dict(schema_version='1.0', scope='on_disk_assignment_statistics', member=member,
                generated_at=datetime.now(timezone.utc).isoformat(), assigned_range=assigned_range,
                assigned_input_count=len(expected), snapshot_stable=True, input_fingerprint=fingerprint,
                unseen_ids=sorted(expected-selected.keys()),
                unresolved_discovery_ids=sorted(k for k,r in selected.items() if r.get('status') not in {'success','not_found'}),
                counts=counts, discovery_statuses=dict(discovery),
                download_statuses=dict(Counter(v['download'] for v in versions)),
                extract_statuses=dict(Counter(v['extract'] for v in versions)),
                sizes=dict(paired_papers=len(before_values),
                           mean_before_bytes=sum(before_values)/len(before_values) if before_values else None,
                           mean_after_bytes=sum(after_values)/len(after_values) if after_values else None),
                references=dict(mean_per_retrieved_paper=totals['references']/retrieved if retrieved else None,
                                complete_numerator=totals['complete_references'], complete_denominator=totals['references'],
                                duplicate_rows=totals['duplicate_reference_rows']),
                diagnostics=diagnostics, papers=papers, versions=versions,
                note='Offline accumulated-state inventory; cached validation is not a fresh audit. '
                     'Sizes before filtering come from extraction sidecars; no runtime/RAM is reconstructed.')
