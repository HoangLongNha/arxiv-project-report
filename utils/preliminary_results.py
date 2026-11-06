"""Evidence-scoped report tables. Missing observations remain missing, never zero."""
import hashlib
import json
from collections import Counter
from pathlib import Path

SNAPSHOT = 'preliminary-20261104'
RANGES = dict(TV1='2508.12872:2508.17871', TV2='2506.15788:2506.20787',
              TV3='2411.08799:2411.13798', TV4='2410.18025:2410.23024',
              TV5='2410.03025:2410.08024')


def read(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None


def expected_ids(spec):
    start, end = spec.split(':')
    month, first = start.split('.')
    end_month, last = end.split('.')
    if month != end_month:
        raise ValueError('Expected same-month assignment')
    return {f'{month}.{i:05d}' for i in range(int(first), int(last) + 1)}


def range_verified(directory, audit, spec):
    if not audit or audit.get('assigned_input_count') != 5000:
        return False
    expected = expected_ids(spec)
    # Prefer inputs adjacent to a byte-identical nested audit.
    for p in directory.glob('audit-*/assignment-audit.json'):
        if read(p) == audit:
            inputs = read(p.parent / 'inputs.json')
            if inputs and inputs.get('ranges') == [{'range': spec}]:
                return True
    # TV2 has no inputs.json, but enumerates every assigned paper identity.
    papers = audit.get('paper_results', [])
    return (len(papers) == 5000 and {p.get('paper_id') for p in papers} == expected
            and audit.get('unseen_ids') == [] and audit.get('unresolved_discovery_ids') == [])


def audit_assessment(audit, verified):
    if audit is None:
        return 'Chưa có audit; chưa kết luận'
    required = ('audit_complete', 'unseen_ids', 'unresolved_discovery_ids',
                'validation_fail_papers', 'diagnostics')
    if any(k not in audit for k in required):
        return 'Audit thiếu trường; chưa kết luận'
    formula = (not audit['unseen_ids'] and not audit['unresolved_discovery_ids']
               and audit['validation_fail_papers'] == 0 and not audit['diagnostics'])
    if audit['audit_complete'] != formula:
        return 'Audit mâu thuẫn với định nghĩa source; cần chạy lại'
    if not verified:
        return 'Chưa xác minh đúng dải audit'
    if audit['audit_complete'] is True:
        return 'Đủ điều kiện theo audit được cung cấp; chưa tái kiểm corpus độc lập'
    return 'Chưa đạt: còn lỗi Discovery/validation hoặc diagnostics'


def validate_cumulative(doc, member):
    expected = expected_ids(RANGES[member])
    if (doc.get('scope') != 'on_disk_assignment_statistics' or doc.get('member') != member
            or doc.get('assigned_range') != RANGES[member] or doc.get('assigned_input_count') != len(expected)
            or doc.get('snapshot_stable') is not True or len(doc.get('input_fingerprint', '')) != 64):
        raise ValueError(f'Cumulative statistics scope/snapshot mismatch: {member}')
    counts, papers, versions = doc['counts'], doc['papers'], doc['versions']
    identities = [p['paper_id'] for p in papers]
    pairs = [(v['paper_id'], v['version']) for v in versions]
    unseen = doc['unseen_ids']
    if (counts['assigned_ids'] != len(expected) or len(set(unseen)) != len(unseen)
            or not set(unseen).issubset(expected) or counts['recorded_ids']+len(unseen) != len(expected)
            or sum(doc['discovery_statuses'].values()) != counts['recorded_ids']
            or len(identities) != len(set(identities)) or not set(identities).issubset(expected)
            or counts['discovery_success_papers'] != len(papers)
            or counts['expected_versions'] != len(versions) or len(pairs) != len(set(pairs))
            or any(identifier not in identities or type(version) is not int or version < 1 for identifier,version in pairs)):
        raise ValueError(f'Cumulative statistics identity/count mismatch: {member}')


def load_members(root):
    base = Path(root) / 'summaries/milestone1' / SNAPSHOT
    result = []
    for member, spec in RANGES.items():
        updated = Path(root) / 'summaries/milestone1/updated-20261106' / member
        directory = updated if (updated / 'provenance.json').is_file() else base / member
        provenance = read(directory / 'provenance.json')
        if provenance:
            for name, hashes in provenance['files'].items():
                data = (directory / name).read_bytes()
                if hashlib.sha256(data).hexdigest() != hashes['published_sha256']:
                    raise ValueError(f'Evidence hash mismatch: {member}/{name}')
        benchmark = read(directory / 'benchmark.json')
        statistics = read(directory / 'statistics.json')
        audit = read(directory / 'assignment-audit.json')
        verified = range_verified(directory, audit, spec)
        authenticated = bool(statistics and benchmark and benchmark.get('run_id')
                             and statistics.get('run_id') == benchmark['run_id']
                             and statistics.get('label') == benchmark.get('label')
                             and benchmark.get('statistics_status') == 'current_run')
        cumulative_dir = Path(root) / 'summaries/milestone1/cumulative' / member
        cumulative = read(cumulative_dir / 'cumulative-statistics.json')
        if cumulative:
            validate_cumulative(cumulative, member)
            receipt = read(cumulative_dir / 'provenance.json')
            digest = hashlib.sha256((cumulative_dir / 'cumulative-statistics.json').read_bytes()).hexdigest()
            if not receipt or receipt.get('sha256') != digest:
                raise ValueError(f'Cumulative statistics provenance mismatch: {member}')
        result.append(dict(member=member, assigned_range=spec, directory=directory,
                           provenance=provenance, benchmark=benchmark, statistics=statistics,
                           audit=audit, verified=verified, authenticated=authenticated, cumulative=cumulative,
                           assessment=audit_assessment(audit, verified)))
    return result


def coverage_rows(members):
    rows = []
    for m in members:
        a = m['audit']
        rows.append({'Thành viên': m['member'], 'Assigned IDs': 5000,
                     'Dải audit xác minh': 'Có' if m['verified'] else 'Chưa xác minh',
                     'Audit Complete (gốc)': str(a['audit_complete']).lower() if a else 'Chưa có dữ liệu',
                     'Unseen IDs': len(a['unseen_ids']) if a else None,
                     'Unresolved IDs': len(a['unresolved_discovery_ids']) if a else None,
                     'Validation Pass/Fail': f"{a['validation_pass_papers']} / {a['validation_fail_papers']}" if a else 'Chưa có dữ liệu',
                     'Đánh giá': 'Chờ dữ liệu' if not m['provenance'] else m['assessment']})
    return rows


def run_range(benchmark):
    command = benchmark.get('command', [])
    return command[command.index('--range')+1] if '--range' in command else 'Chưa xác minh'


def collection_rows(members):
    rows = []
    for m in members:
        s, a, b = m['statistics'], m['audit'], m['benchmark']
        if a:
            rows.append({'Thành viên': m['member'], 'Phạm vi': m['assigned_range'],
                         'Nguồn': 'assignment-audit (toàn dải, theo artifact)',
                         'ID có record': a['discovered_assigned_ids'],
                         'Discovery success': a['discovery_statuses'].get('success', 0),
                         'Versions đã biết': a['known_version_count'],
                         'Source tải thành công': None, 'References': None,
                         'Validation pass': a['validation_pass_papers'],
                         'Validation fail': a['validation_fail_papers']})
        if m['authenticated']:
            counts = s['counts']
            papers = s.get('papers', [])
            statuses = [p.get('validation_valid') for p in papers]
            rows.append({'Thành viên': m['member'], 'Phạm vi': run_range(b),
                         'Nguồn': 'statistics (riêng run resume)',
                         'ID có record': counts['papers'],
                         'Discovery success': counts['discovery_success_papers'],
                         'Versions đã biết': counts['expected_versions'],
                         'Source tải thành công': s['download_statuses'].get('success', 0),
                         'References': counts['references'],
                         'Validation pass': statuses.count(True) if statuses and all(isinstance(x, bool) for x in statuses) else None,
                         'Validation fail': statuses.count(False) if statuses and all(isinstance(x, bool) for x in statuses) else None})
    return rows


def performance_rows(members):
    rows = []
    for m in members:
        b = m['benchmark']
        if not b:
            continue
        ram = b['ram']
        usable_ram = b['sample_count'] >= 2 and ram['observed_seconds'] > 0
        rows.append({'Thành viên': m['member'], 'Phạm vi run': run_range(b),
                     'Run ID': b.get('run_id'), 'Loại': 'Resume, bị ngắt' if b['exit_code'] == 130 else 'Resume',
                     'Exit code': b['exit_code'], 'Wall seconds (artifact)': b['wall_seconds'],
                     'RAM samples': b['sample_count'],
                     'Peak RSS MiB (quan sát)': ram['peak_rss_bytes']/1024**2 if usable_ram else None,
                     'Mean RSS MiB': ram['time_weighted_mean_rss_bytes']/1024**2 if usable_ram and ram['time_weighted_mean_rss_bytes'] is not None else None,
                     'Giới hạn RAM': 'Chỉ là mẫu quan sát' if usable_ram else 'Không đủ mẫu; không diễn giải peak/mean',
                     'Disk final GiB': b['disk']['final_bytes']/1024**3 if b['disk'].get('final_bytes') is not None else None})
    return rows


def progress_rows(members):
    """Group-reported completion and artifact verification are separate observations."""
    rows = []
    for m in members:
        a = m['audit'] if m['verified'] else None
        rows.append({'Thành viên': m['member'], 'ID được giao': 5000,
                     'Đã chạy theo báo cáo nhóm': 5000,
                     'ID có kết quả ghi nhận': a['discovered_assigned_ids'] if a else None,
                     'ID chưa ghi nhận': len(a['unseen_ids']) if a else None,
                     'Lookup còn lỗi': len(a['unresolved_discovery_ids']) if a else None})
    return rows


def assignment_outcomes(members):
    """Never fill assignment-scale results from a shorter benchmark session."""
    rows = []
    for m in members:
        a = m['audit'] if m['verified'] else None
        rows.append({'Thành viên': m['member'],
                     'Paper phát hiện thành công': a['discovery_statuses'].get('success', 0) if a else None,
                     'ID không tìm thấy': a['discovery_statuses'].get('not_found', 0) if a else None,
                     'Version đọc được từ kiểm định': a['known_version_count'] if a else None})
    return rows


def quality_rows(members):
    rows = []
    for m in members:
        a = m['audit'] if m['verified'] else None
        passed = a['validation_pass_papers'] if a else None
        failed = a['validation_fail_papers'] if a else None
        total = passed + failed if a else None
        rows.append({'Thành viên': m['member'], 'Paper đã kiểm định': total,
                     'Đạt': passed, 'Còn lỗi': failed,
                     'Tỷ lệ đạt (%)': 100*passed/total if total else None})
    return rows


ERROR_LABELS = {
    'upstream_failure': 'Stage thu thập/xử lý chưa thành công',
    'artifact_location': 'Đường dẫn đầu ra chưa đúng hợp đồng',
    'invalid_artifact': 'Tệp đầu ra thiếu hoặc không hợp lệ',
    'invalid_source': 'Source thiếu, rỗng hoặc không hợp lệ',
    'invalid_corpus_file': 'Tệp corpus bị báo rỗng/nhị phân',
    'invalid_corpus': 'Corpus thiếu hoặc không hợp lệ',
    'inconsistent_status': 'Trạng thái các bước chưa nhất quán',
    'validation_read_error': 'Không đọc/diễn giải được dữ liệu kiểm định',
}


def error_groups(members):
    rows = []
    for m in members:
        if not m['audit'] or not m['verified']:
            continue
        counts = Counter()
        for paper in m['audit']['paper_results']:
            if paper['valid']:
                continue
            codes = {e['code'] for e in paper.get('errors', [])}
            if 'error' in paper:
                codes.add('validation_read_error')
            counts.update(codes)
        rows.extend({'Thành viên': m['member'], 'Nhóm vấn đề': ERROR_LABELS.get(k, k),
                     'Paper bị ảnh hưởng': v} for k, v in counts.most_common())
    return rows


def session_members(root, members):
    """Expose earlier TV4 sessions separately; never sum overlapping runs."""
    result = [dict(m, session=m['member'] + ' (' + m['benchmark']['started_at'][:10] + ')')
              for m in members if m['benchmark']]
    seen = {m['benchmark']['run_id'] for m in result}
    corrected = Path(root) / 'summaries/milestone1/updated-20261106/TV4-session-20261102'
    if corrected.is_dir():
        provenance = read(corrected / 'provenance.json')
        for name, hashes in provenance['files'].items():
            if hashlib.sha256((corrected / name).read_bytes()).hexdigest() != hashes['published_sha256']:
                raise ValueError('Corrected session evidence hash mismatch')
        b = read(corrected / 'benchmark.json')
        result.append(dict(member='TV4', session='TV4 (2026-11-02)', directory=corrected,
                           benchmark=b, provenance=provenance))
        seen.add(b['run_id'])
    base = Path(root) / 'summaries/milestone1/supplementary-20261104'
    for directory in sorted(base.glob('TV4-*')):
        provenance = read(directory / 'provenance.json')
        for name, hashes in provenance['files'].items():
            if hashlib.sha256((directory / name).read_bytes()).hexdigest() != hashes['published_sha256']:
                raise ValueError(f'Evidence hash mismatch: {directory.name}/{name}')
        paths = list(directory.glob('*/benchmark.json'))
        if len(paths) != 1:
            raise ValueError('Expected one benchmark per supplementary session')
        b = read(paths[0])
        if b['run_id'] not in seen:
            result.append(dict(member='TV4', session=directory.name, directory=paths[0].parent,
                               benchmark=b, provenance=provenance))
            seen.add(b['run_id'])
    historical = Path(root) / 'summaries/milestone1/preliminary-20261104/TV4'
    b = read(historical / 'benchmark.json')
    if b and b['run_id'] not in seen:
        p = read(historical / 'provenance.json')
        for name, hashes in p['files'].items():
            if hashlib.sha256((historical / name).read_bytes()).hexdigest() != hashes['published_sha256']:
                raise ValueError('Historical session evidence hash mismatch')
        result.append(dict(member='TV4', session='TV4 (2026-11-03)', directory=historical,
                           benchmark=b, provenance=p))
    return result


def cumulative_rows(members):
    return [{'Thành viên': m['member'],
             'Paper phát hiện': m['cumulative']['counts']['discovery_success_papers'] if m['cumulative'] else None,
             'Version đã biết': m['cumulative']['counts']['expected_versions'] if m['cumulative'] else None,
             'Source có tệp': m['cumulative']['counts']['source_versions_verified'] if m['cumulative'] else None,
             'References': m['cumulative']['counts']['references'] if m['cumulative'] else None,
             'Thống kê tích lũy': m['cumulative']['generated_at'] if m['cumulative'] else 'Chưa xuất từ corpus'} for m in members]
