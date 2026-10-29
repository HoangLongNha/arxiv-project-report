"""Create editable notebook sources. Run only when intentionally regenerating them."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]


def notebook(path, cells):
    doc = nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell(text) if kind == 'md'
                                   else nbf.v4.new_code_cell(text) for kind, text in cells])
    doc.metadata['kernelspec'] = {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}
    doc.metadata['language_info'] = {'name': 'python', 'version': '3.12'}
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(doc, target)


setup = '''from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / '_config.yml').exists())
sys.path.insert(0, str(ROOT / 'utils'))
from report_utils import load_run
run_name, summary, benchmark, samples = load_run(ROOT)
display(Markdown(f"**Run: {run_name} — label: {benchmark['label']}**"))
if benchmark['label'] == 'synthetic_demo':
    display(Markdown('> **DEMO OFFLINE: các con số không phải kết quả corpus thật hoặc benchmark Colab.**'))
elif benchmark['label'] == 'colab_cpu_sample':
    display(Markdown('> **MẪU COLAB CPU-ONLY: một paper được giao, không phải toàn bộ assignment 25.000 ID.**'))
else:
    display(Markdown('> Lượt gọi API thật; cần đối chiếu môi trường Colab CPU-only, phạm vi input và logs trước nghiệm thu.'))
'''

notebook('milestone1/statistics.ipynb', [
('md', '# Thống kê corpus\n\nBảng và biểu đồ được tạo từ JSON khi build. Tỷ lệ dùng thang 0–1; bảng hiển thị thêm phần trăm. Null nghĩa chưa có mẫu số/số đo.'),
('code', setup),
('code', "display(pd.DataFrame([summary['counts']]))\ncoverage_path = ROOT / 'summaries/milestone1' / run_name / 'corpus_coverage.json'\nif coverage_path.exists():\n    import json\n    display(Markdown('**Độ bao phủ assignment đầy đủ (khác phạm vi mẫu benchmark):**'))\n    display(pd.DataFrame([json.loads(coverage_path.read_text(encoding='utf-8'))]))\nrates = pd.DataFrame([{'metric': k, **v} for k,v in summary['rates'].items()])\nrates['percent'] = rates['value'] * 100\ndisplay(rates)"),
('md', '## Trạng thái theo version\n\nDownload và extract dùng cùng tập version đã biết. Discovery lỗi được báo riêng vì chưa biết số version.'),
('code', "fig, axes = plt.subplots(1,2,figsize=(11,4))\nfor ax,key,title in zip(axes,['download_statuses','extract_statuses'],['Download outcomes','Extraction outcomes']):\n    values = summary[key]\n    if values: ax.bar(list(values),list(values.values()))\n    ax.set_title(title); ax.set_ylabel('Paper-version count'); ax.tick_params(axis='x',rotation=25)\nplt.tight_layout(); plt.show()\ndisplay(pd.DataFrame([summary['discovery_statuses']]))"),
('md', '## Kích thước và references\n\nTrước/sau lọc là bytes đã giải nén, tổng mọi version mỗi paper trên cùng tập có đủ cặp đo. Kích thước package nén được báo riêng.'),
('code', "display(pd.DataFrame([summary['sizes']]))\nvalues = [summary['sizes']['mean_uncompressed_before_per_paper_bytes'], summary['sizes']['mean_filtered_per_paper_bytes']]\nif all(v is not None for v in values):\n    plt.figure(figsize=(7,4)); plt.bar(['Before filtering','After filtering'],values); plt.ylabel('Mean uncompressed bytes / paired paper'); plt.tight_layout(); plt.show()\npackages = [v['package_bytes'] for v in summary['versions'] if v['package_bytes'] is not None]\nif packages:\n    plt.figure(figsize=(7,4)); plt.hist(packages,bins=min(20,len(packages))); plt.xlabel('Compressed package bytes'); plt.ylabel('Paper-version count'); plt.tight_layout(); plt.show()\ndisplay(pd.DataFrame([{'mean_refs_per_retrieved_paper': summary['references']['mean_per_retrieved_paper'], **summary['references']['complete_metadata_rate']}]))\ndisplay(pd.DataFrame([summary['reference_statuses']]))"),
('md', '## Nguyên nhân lỗi và dữ liệu thiếu\n\nFile/chỉ số không đọc được hiện trong diagnostics. Validator pass được trình bày riêng với source success.'),
('code', "display(pd.DataFrame([{'cause': k, 'count': v} for k,v in summary['failure_causes'].items()]))\ndisplay(pd.DataFrame(summary['diagnostics']))\ndisplay(pd.DataFrame(summary['papers']))"),
])

notebook('milestone1/performance.ipynb', [
('md', '# Hiệu năng pipeline\n\nWall time và các đỉnh tài nguyên phải được đọc cùng nhãn run, input và môi trường. Không suy hiệu năng arXiv từ fixtures.'),
('code', setup),
('code', "display(pd.DataFrame([{'wall_seconds': benchmark['wall_seconds'], 'pipeline_exit': benchmark['exit_code'], 'discovery_seconds': benchmark['timings']['discovery_total_seconds'], 'mean_paper_seconds': benchmark['timings']['mean_paper_seconds'], 'cached_events': benchmark['timings']['cached_events'], 'sample_interval_seconds': benchmark['sample_interval_seconds'], 'access_errors': benchmark['measurement_access_errors']}]))\nenv = {k:v for k,v in benchmark['environment'].items() if k != 'packages'}\ndisplay(pd.DataFrame([{'field': k, 'value': str(v)} for k,v in env.items()]))\ndisplay(pd.DataFrame([{'package': k,'version':v} for k,v in benchmark['environment'].get('packages',{}).items()]))"),
('md', '## Thời gian từng bước và từng paper\n\nPaper lỗi cũng được tính trong attempted-input timing; alias cùng paper được cộng. Tổng stage không gồm mọi overhead của wall time. Events đang dở khi ngắt chưa có full duration.'),
('code', "stage = benchmark['timings']['stage_seconds']\nif stage:\n    plt.figure(figsize=(9,4)); plt.bar(stage.keys(),stage.values()); plt.ylabel('Total seconds / stage'); plt.xticks(rotation=25); plt.tight_layout(); plt.show()\npapers = benchmark['timings']['per_paper_seconds']\ndisplay(pd.DataFrame([{'paper_id': k, 'seconds': v} for k,v in papers.items()]))\nif papers:\n    plt.figure(figsize=(8,4)); plt.hist(list(papers.values()),bins=min(20,len(papers))); plt.xlabel('Seconds / paper'); plt.ylabel('Paper count'); plt.tight_layout(); plt.show()"),
('md', '## RAM và dung lượng đĩa\n\nRSS cộng pipeline và child processes; shared pages có thể đếm nhiều lần. Peak là cực đại quan sát được. Disk là logical bytes trong output, không gồm results của sampler.'),
('code', "display(pd.DataFrame([benchmark['ram']]))\ndisplay(pd.DataFrame([benchmark['disk']]))\nframe = pd.DataFrame(samples)\nif not frame.empty:\n    fig, axes = plt.subplots(2,1,figsize=(9,6),sharex=True)\n    axes[0].plot(frame['elapsed_seconds'],frame['rss_bytes']/1024**2); axes[0].set_ylabel('Summed RSS (MiB)')\n    axes[1].plot(frame['elapsed_seconds'],frame['disk_bytes']/1024**2); axes[1].set_ylabel('Output size (MiB)'); axes[1].set_xlabel('Elapsed seconds')\n    plt.tight_layout(); plt.show()"),
])

# Colab cells are maintained separately; preserve its member/Drive workflow.
import runpy
runpy.run_path(str(ROOT / 'scripts/sync_colab_notebook.py'), run_name='__main__')
