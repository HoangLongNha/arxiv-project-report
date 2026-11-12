"""Create a Colab inventory notebook with hash-checked, read-only corpus tooling."""
from pathlib import Path
import hashlib
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]
hashes = {name:hashlib.sha256((ROOT/name).read_text(encoding='utf-8').encode('utf-8')).hexdigest()
          for name in ['scripts/export_cumulative_ms1.py','utils/cumulative_statistics.py']}
cells = [nb.v4.new_markdown_cell('''# Xuất thống kê corpus MS1 tích lũy

Dùng sau khi đã dừng pipeline và các tiến trình audit đang ghi cùng thư mục dữ liệu. Notebook chỉ đọc dữ liệu hiện có, không tải lại paper và không sửa corpus/checkpoint. Tệp xuất không chứa số đo runtime/RAM của các phiên trước.

Chọn đúng thành viên và sửa đường dẫn nếu dữ liệu không nằm trong thư mục mặc định. Giữ tệp audit mới nhất riêng để đối chiếu chất lượng; công cụ này chỉ đọc validation đã lưu.'''),
nb.v4.new_code_cell("from google.colab import drive\ndrive.mount('/content/drive')"),
nb.v4.new_code_cell('''from pathlib import Path
import urllib.request, hashlib, sys, subprocess, uuid
MEMBER = 'TV3' # @param ['TV1','TV2','TV3','TV4','TV5']
DATA = Path('/content/drive/MyDrive/arxiv_ms1_data') / MEMBER.lower() / 'data'
WRITERS_STOPPED = False # @param {type:'boolean'}
assert WRITERS_STOPPED, 'Dừng pipeline/audit ghi dữ liệu rồi xác nhận WRITERS_STOPPED=True.'
assert DATA.is_dir(), f'Chỉnh DATA tới thư mục dữ liệu hiện có: {DATA}'
TOOLS = Path('/content/ms1-cumulative-tools')
EXPECTED = ''' + repr(hashes) + '''
for name, digest in EXPECTED.items():
    url = 'https://raw.githubusercontent.com/HoangLongNha/arxiv-project-report/main/' + name
    raw = urllib.request.urlopen(url, timeout=60).read()
    assert hashlib.sha256(raw).hexdigest() == digest, 'Code đã đổi; lấy notebook mới từ repository trước khi chạy.'
    path = TOOLS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
RESULT = DATA.parent / 'artifacts' / ('cumulative_' + uuid.uuid4().hex) / 'cumulative-statistics.json'
command = [sys.executable, str(TOOLS / 'scripts/export_cumulative_ms1.py'),
           '--member', MEMBER, '--output', str(DATA), '--save', str(RESULT), '--writers-stopped']
subprocess.run(command, check=True)
'''),
nb.v4.new_code_cell('''import json
from google.colab import files
report = json.loads(RESULT.read_text(encoding='utf-8'))
print('Thành viên:', report['member'], 'Dải:', report['assigned_range'])
print('Số liệu:', report['counts'])
print('ID chưa ghi nhận:', len(report['unseen_ids']))
print('Lookup còn lỗi:', len(report['unresolved_discovery_ids']))
print('Diagnostics:', len(report['diagnostics']))
print('Đã lưu trên Drive:', RESULT)
files.download(str(RESULT))
'''),
nb.v4.new_markdown_cell('''Gửi tệp JSON vừa xuất cho TV5. Không cộng nó với statistics của các phiên resume. Nếu công cụ báo dữ liệu thay đổi khi đang quét, dừng tiến trình ghi và chạy lại để tạo tệp mới. Số diagnostics cần được xem cùng số liệu trước khi tổng hợp nhóm.''')]
doc = nb.v4.new_notebook(cells=cells)
doc.metadata['kernelspec'] = dict(display_name='Python 3',language='python',name='python3')
for cell in doc.cells:
    cell.id = hashlib.sha256((cell.cell_type+cell.source).encode()).hexdigest()[:12]
nb.write(doc, ROOT/'colab/MS1_Cumulative_Statistics.ipynb')
