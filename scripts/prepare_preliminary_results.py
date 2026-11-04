"""Regenerate only the preliminary results notebook; no API or corpus writes."""
from pathlib import Path
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]
cells = []


def md(text):
    cells.append(nb.v4.new_markdown_cell(text))


def code(text):
    cells.append(nb.v4.new_code_cell(text))


md('''# Preliminary Results & Data Collection Progress — Kết quả sơ bộ và tiến độ thu thập dữ liệu

Ngày đối chiếu: **04/11/2026**. Nhóm đã chia sẻ artifacts của **TV2–TV5 (4/5 thành viên)**; chưa có bộ kết quả TV1 trong thư mục được cung cấp. Việc nộp ZIP/artifacts không đồng nghĩa hoàn tất assignment hoặc đạt validation. Các bảng dưới đây được sinh khi build từ snapshot `preliminary-20261104`, độc lập với biến `TV5_RUN` dùng cho các mẫu lịch sử.

**Assignment Coverage** đo việc ghi nhận và giải quyết lookup của ID được giao; **Collection Success** đo paper/version và đầu ra thu thập thành công; **Data Validity** đo việc vượt qua validator. Một lookup `not_found` đã được giải quyết nhưng không tạo paper. 5.000 ID không đồng nghĩa 5.000 paper hay 5.000 source tải thành công.

Đây là kiểm tra artifacts được nộp, chưa phải tái kiểm độc lập toàn corpus trên Drive. Không cộng các run resume, không suy kết quả của một run thành kết quả toàn nhóm.''')
code('''from pathlib import Path
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / '_config.yml').exists())
sys.path.insert(0, str(ROOT / 'utils'))
from preliminary_results import load_members, coverage_rows, collection_rows, performance_rows, run_range
members = load_members(ROOT)
def table(rows):
    frame = pd.DataFrame(rows, dtype=object)
    display(frame.where(frame.notna(), 'Chưa có dữ liệu'))
''')
md('''## Preliminary Observations

### 1. Assignment Coverage

#### Assignment Coverage by Member

`Audit Complete (gốc)` giữ nguyên giá trị trong file. Đánh giá chỉ xác nhận hoàn tất khi đúng dải 5.000 ID, `audit_complete=true`, không còn unseen/unresolved, và không mâu thuẫn với định nghĩa source.

Trong [source commit 3985747](https://github.com/LeoTkiet/arxiv-data-science/blob/3985747848bf902fadc155078e3ff61083643e15/src/arxiv_pipeline/reporting/milestone1/audit.py) (TV2) và [4ea44c4](https://github.com/LeoTkiet/arxiv-data-science/blob/4ea44c42810f3bb1564080c19d1ed889f3498ee0/src/arxiv_pipeline/reporting/milestone1/audit.py) (TV3–TV5), công thức là:

```python
audit_complete = not unseen_ids and not unresolved_discovery_ids and not validation_fail_papers and not diagnostics
```

Do đó `audit_complete` còn phụ thuộc validation và diagnostics, không chỉ lookup coverage. `discovered_assigned_ids` trong hai phiên bản này thực chất là số ID **có record** (`len(selected)`), kể cả record lỗi; số paper phát hiện thành công được đọc riêng từ `discovery_statuses.success`.''')
code('''table(coverage_rows(members))
table([{'Thành viên': m['member'], 'Dải được giao': m['assigned_range'],
        'Ngày audit (UTC)': m['audit']['generated_at'] if m['audit'] else None,
        'ID có record (audit)': m['audit']['discovered_assigned_ids'] if m['audit'] else None,
        'Diagnostics': len(m['audit']['diagnostics']) if m['audit'] else None}
       for m in members])''')
md('''**Diễn giải kết quả:**

- **TV1:** chưa có dữ liệu để đánh giá.
- **TV2:** audit liệt kê đủ 5.000 paper ID đúng dải, unseen/unresolved đều rỗng; nhưng `audit_complete=true` mâu thuẫn với **2.579 validation fail** theo chính công thức source được benchmark khai báo. Không sửa giá trị gốc và không công nhận hoàn tất; cần xác minh code audit thực dùng và chạy lại audit. Không có `inputs.json` kèm theo; phạm vi được đối chiếu bằng toàn bộ 5.000 định danh trong `paper_results`.
- **TV3:** ZIP và thư mục audit trên Drive được kiểm tra chỉ có `inputs.json`, chưa có `assignment-audit.json`. Việc khai báo dải đầu vào chưa chứng minh audit đã thực thi.
- **TV4:** ZIP có hai `inputs.json`, chưa có kết quả audit; chưa kết luận độ bao phủ toàn dải. Chưa xác minh được nội dung đích của shortcut Drive TV4 qua connector.
- **TV5:** audit đúng dải, có record cho 5.000 ID; **4 Discovery chưa giải quyết**, **4.617 pass / 379 fail**, nên `audit_complete=false`. Bốn ID unresolved là `2410.04689`, `2410.04690`, `2410.05043`, `2410.05044`.

Chưa thành viên nào trong bộ bằng chứng này đủ điều kiện được xác nhận hoàn tất toàn bộ QA MS1.''')
md('''### 2. Data Collection Outcomes

Mỗi dòng ghi rõ phạm vi và nguồn. Dòng audit toàn dải phản ánh trạng thái checkpoint/corpus tại ngày audit; dòng statistics phản ánh **riêng run resume**. Không cộng hai loại dòng. `known_version_count` chỉ cộng version đọc được từ validation; khi validation lỗi đọc, con số này có thể chưa đầy đủ (đặc biệt TV2), và không phải số version tải thành công.

TV2 không có `statistics.json` trong ZIP. `statistics_error.json` ghi: “No completed snapshot for this run_id; previous manifest is not current data”. Vì vậy chưa có số liệu Collection Success đáng tin cậy cho run đó. Các statistics TV3–TV5 có run ID/label khớp benchmark và `statistics_status=current_run`; đây chỉ là đối chiếu nội bộ artifact, chưa xác thực lại hash manifest trên corpus sống.''')
code('''table(collection_rows(members))
outcomes = []
for m in members:
    if not m['authenticated']:
        continue
    for stage, key in [('Discovery', 'discovery_statuses'), ('Download', 'download_statuses'),
                       ('Extract', 'extract_statuses'), ('References', 'reference_statuses')]:
        for status, count in m['statistics'][key].items():
            outcomes.append({'Thành viên': m['member'], 'Phạm vi run': run_range(m['benchmark']),
                             'Stage': stage, 'Status': status, 'Count': count})
table(outcomes)
table([{'Thành viên': m['member'], 'Diagnostics statistics': len(m['statistics']['diagnostics'])}
       for m in members if m['authenticated']])''')
md('''Bảng trạng thái chỉ liệt kê status có trong artifact: `no_source` là không có source, `api_error` là lỗi API, `data_error` là lỗi dữ liệu, `no_data` là không nhận được dữ liệu ở stage tương ứng, `skipped` là stage bỏ qua. Status không xuất hiện không được suy thành số 0 cho toàn assignment. Download/extract đếm theo version; references và validation đếm theo paper.

TV3 có 1.182 source thành công, 103 `no_source` và 55 download `api_error` trong **1.340 version của run 828 ID**; 158 extract `skipped` không phải 158 ID chưa lookup. TV4 và TV5 có kết quả run cuối 6 ID, tương ứng 10 và 12 version. Tỷ lệ cao trong hai run nhỏ này không đại diện toàn dải.''')
code('''fig, ax = plt.subplots(figsize=(8, 4))
for offset, status in enumerate(['success', 'no_source', 'api_error']):
    valid = [m for m in members if m['authenticated']]
    values = [m['statistics']['download_statuses'].get(status, 0) for m in valid]
    ax.bar([i + (offset-1)*0.25 for i in range(len(valid))], values, width=0.25, label=status)
ax.set_xticks(range(len(valid)), [m['member'] + ' (riêng run)' for m in valid])
ax.set_ylabel('Paper-version count'); ax.set_title('Download outcomes theo run đã nộp')
ax.legend(); plt.tight_layout(); plt.show()''')
md('''### 3. Preliminary Performance Observations

Tất cả bốn run được nộp đều dùng `--resume`, nhãn `live_unverified`; không phải bốn benchmark fresh toàn assignment có thể so tốc độ trực tiếp. TV2 bị ngắt (exit 130); TV3 exit 1 với lỗi download. TV4/TV5 exit 0 chỉ xác nhận run nhỏ kết thúc.

Wall time bên dưới là giá trị được lưu trong `benchmark.json`, không phải tổng thời gian nhiều phiên crawl. Ở cả bốn artifact, khoảng cách `finished_at − started_at` lớn hơn `wall_seconds`; chưa xác định đầy đủ overhead/biên đo, nên không dùng các số này làm tổng thời gian thu thập hoặc ngoại suy 5.000/25.000 ID.

TV2 không có RAM sample; TV4 và TV5 chỉ có một sample, `observed_seconds=0` và mean RSS `null`. Không trình bày các peak đơn lẻ này như peak đại diện cho pipeline. TV3 có 132 mẫu; sampling trên Drive có thể thưa hơn interval cấu hình 0,1 giây. Disk là logical bytes của output root đã có dữ liệu từ các phiên trước; không phải số byte do run hiện tại tải mới. CPU được mô tả qua cấu hình môi trường, chưa có số đo CPU utilization.''')
code('''table(performance_rows(members))
table([{'Thành viên': m['member'], 'Started at (UTC)': m['benchmark']['started_at'],
        'Finished at (UTC)': m['benchmark']['finished_at'],
        'Source commit': m['benchmark']['environment'].get('source_commit'),
        'Source dirty': m['benchmark']['environment'].get('source_dirty'),
        'Logical CPU': m['benchmark']['environment'].get('logical_cpu_count'),
        'Colab': m['benchmark']['environment'].get('is_colab'),
        'CPU-only khai báo': m['benchmark']['environment'].get('cpu_only_confirmation')}
       for m in members if m['benchmark']])
timing_rows = []
for m in members:
    path = m['directory'] / 'timings.jsonl'
    if not path.is_file():
        continue
    events = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    for stage in sorted({e['kind'] for e in events}):
        subset = [e for e in events if e['kind'] == stage]
        timing_rows.append({'Thành viên': m['member'], 'Kind': stage, 'Events': len(subset),
                            'Cached events': sum(e.get('cached') is True for e in subset),
                            'Elapsed sum (seconds)': sum(e['elapsed_seconds'] for e in subset)})
table(timing_rows)''')
md('''Thời gian event đọc trực tiếp từ `timings.jsonl`; paper timing có thể bao gồm stage timing nên không cộng tất cả các loại event thành wall time. Những event đang dở khi ngắt có thể chưa được ghi nhận.

### 4. Current Limitations

- Chưa có đầy đủ dữ liệu của năm thành viên; chưa có kết quả audit TV3/TV4 trong artifacts đã kiểm tra.
- Audit TV2 có mâu thuẫn giữa cờ hoàn tất và validation; cần tái kiểm với code audit được xác định rõ. Code ở commit TV2 cho phép tái sử dụng validation đã có, nên cũng phải kiểm tra độ mới của báo cáo khi chạy lại.
- TV5 còn Discovery/validation lỗi; TV3 có download lỗi trong run được nộp. Chưa kiểm tra độc lập corpus đầy đủ của bốn thành viên.
- Chưa có thống kê full-corpus tương ứng từng dải và bộ benchmark chính thức đồng nhất. Không thể công bố thống kê tổng hợp cuối cùng cho 25.000 ID.
- Run ID và hash của artifact đã công bố được đối chiếu khi build; điều đó không thay việc tái kiểm manifest/checkpoint và dữ liệu trên Drive.

## Nguồn và khả năng truy vết

Snapshot chỉ chứa artifacts báo cáo, không chứa corpus và không ghi đè dữ liệu gốc. `provenance.json` lưu URL ZIP, SHA-256 ZIP, hash từng tệp gốc và hash bản công bố; `run.json`/`benchmark.json` được lược đường dẫn cục bộ. TV2 có thêm một lớp ZIP, được kiểm CRC cả hai lớp. TV5 dùng ZIP cục bộ cùng tên/kích thước với bản Drive, chưa đối chiếu hash cloud. Mọi thời điểm trong bảng giữ UTC gốc.

Thư mục nhóm: [arxiv_ms1_data trên Drive](https://drive.google.com/drive/folders/123TUmjXMX38gKRLnJIKDl2yZF8jK6e9n). Bộ bằng chứng dưới đây được chọn một ZIP cho mỗi thành viên, không cộng các phiên có phạm vi chồng lặp.''')
code('''for m in members:
    p = m['provenance']
    if p:
        display(Markdown(f"- **{m['member']}**: [{p['archive_name']}]({p['drive_url']}); SHA-256 `{p['archive_sha256']}`"))
table([{'Artifact': 'assignment-audit.json', 'Chức năng': 'Coverage/lookup và validation toàn dải được audit'},
       {'Artifact': 'summary.json', 'Chức năng': 'Inputs/papers/versions và trạng thái một run; không có trong các ZIP này'},
       {'Artifact': 'statistics.json', 'Chức năng': 'Thống kê theo snapshot/phạm vi run'},
       {'Artifact': 'benchmark.json + timings.jsonl', 'Chức năng': 'Số đo tài nguyên và thời gian của run'},
       {'Artifact': 'validation/<paper_id>.json', 'Chức năng': 'Chi tiết tính hợp lệ từng paper; chưa tái kiểm độc lập'},
       {'Artifact': 'run.json', 'Chức năng': 'Cấu hình bắt đầu run; exit_code null không thay kết quả cuối trong benchmark.json'}])''')

doc = nb.v4.new_notebook(cells=cells)
doc.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}
doc.metadata['language_info'] = {'name': 'python', 'version': '3.12'}
nb.write(doc, ROOT / 'milestone1/preliminary-results.ipynb')
