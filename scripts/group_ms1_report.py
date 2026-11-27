"""Generate MS1 as a group report from the frozen handoff, without editing MS2."""
PAGES={
'milestone1/index.md':'''# Milestone 1: Thu thập dữ liệu arXiv

Nhóm xây dựng corpus bài báo arXiv gồm source LaTeX đa phiên bản, metadata và tài liệu tham khảo. Phạm vi gồm 25.000 ID được giao, xử lý qua một pipeline thống nhất từ Discovery đến kiểm định đầu ra.

Bộ dữ liệu MS1 đã được nhóm chốt làm đầu vào cho các giai đoạn tiếp theo. Báo cáo trình bày kết quả thu thập và chất lượng của toàn bộ corpus, cùng thực nghiệm kích thước, thời gian và tài nguyên trên Google Colab CPU-only. Các trạng thái không có source và chưa đạt quy tắc kiểm định được giữ trong kết quả để mô tả đúng đặc tính dữ liệu.

- [Mục tiêu và phạm vi](introduction.md)
- [Phương pháp thu thập](methodology.md)
- [Thiết lập thực nghiệm](experimental-setup.md)
- [Kết quả và chất lượng corpus](preliminary-results.ipynb)
- [Hiệu năng](performance.ipynb)
- [Thảo luận và kết luận](discussion.md)
- [Phân công thực hiện](member-contributions.md)
- [Nguồn số liệu và tái lập](audit-appendix.ipynb)
''',
'milestone1/introduction.md':'''# Mục tiêu và phạm vi

MS1 chuyển các dải arXiv ID được giao thành corpus có thể dùng cho parsing và matching. Mỗi paper được nhận diện bằng arXiv ID; mọi version phát hiện được được xử lý riêng để giữ lịch sử chỉnh sửa.

Ba nhiệm vụ chính là xác định bài báo và phiên bản, tải source đầy đủ rồi giữ TeX/BibTeX, và lấy metadata tài liệu tham khảo qua Semantic Scholar. Việc lọc bỏ hình thực hiện ở bước giải nén; nội dung LaTeX và các lệnh hình được giữ nguyên.

Toàn bộ nhóm dùng chung schema, CLI và cơ chế checkpoint. Năm dải 5.000 ID được xử lý độc lập rồi tổng hợp theo định danh; một paper không bị đếm thêm chỉ vì đã chạy qua nhiều phiên. Corpus đã chốt được mô tả bằng kết quả thực tế, gồm cả PDF-only và các trường hợp chưa đáp ứng mọi quy tắc kiểm định.

Theo [đề bài MS1](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/crawling/), báo cáo phân tích số paper thu thập, tỷ lệ thành công, kích thước trước/sau lọc, references và hiệu năng. Các bảng và biểu đồ được tính từ artifacts khi biên dịch Jupyter Book.
''',
'milestone1/experimental-setup.md':'''# Thiết lập thực nghiệm

## Phạm vi dữ liệu

Kết quả corpus dùng bộ MS1 đã được nhóm chốt, gồm năm dải không giao nhau, tổng 25.000 ID. Mỗi paper chỉ được tính một lần; mỗi version dùng cặp arXiv ID và số phiên bản. Trạng thái kiểm định lấy từ audit hoặc validation trong bản kiểm kê tương ứng với bộ bàn giao.

## Định nghĩa chỉ số

| Chỉ số | Cách tính và giới hạn |
|---|---|
| Bao phủ Discovery | ID nhận diện thành công / 25.000 ID được giao |
| Source thu thập được | Version có source theo dữ liệu kiểm định; phân biệt với record no_source |
| Tỷ lệ đạt kiểm định | Paper đạt toàn bộ quy tắc / paper đã kiểm định |
| References đã ghi nhận | Tổng quan hệ paper–reference đọc được trong bản kiểm định, không phải số tài liệu tham khảo duy nhất toàn cục |
| References/paper | References đã ghi nhận / paper của phạm vi xét; không ước lượng references chưa thu được |
| Kích thước trước/sau lọc | Cộng version trong từng paper, rồi lấy trung bình trên cùng tập có đủ cặp đo |
| Metadata references đầy đủ | Reference đủ năm trường / references được xét trong phép đo |

Một record no_source hợp lệ có thể đại diện cho PDF-only, không tự động là lỗi thu thập. Paper đạt validator cũng không có nghĩa luôn có TeX: record rỗng hợp lệ được giữ theo hợp đồng. Tỷ lệ Discovery, mức hiện diện source và tỷ lệ đạt validator vì vậy được báo riêng.

## Thực nghiệm dung lượng và hiệu năng

Các phép đo kích thước và benchmark đã lưu được giữ làm bằng chứng thực nghiệm, với ngày và phạm vi riêng. Chúng không được gắn lại thành phép đo trên bộ corpus cuối chỉ bằng cách thay nhãn. Kích thước trước lọc lấy từ sidecar giải nén; sau lọc là TeX/BibTeX. Trung bình gộp có trọng số theo số paper có cặp đo.

Testbed là Google Colab CPU-only. Công cụ benchmark đo wall time của tiến trình pipeline, RSS của cây tiến trình và dung lượng toàn output; sample/timing giữ trong artifacts. Các phiên resume có thể dùng cache và thử lại stage, nên thời gian đo mô tả phiên thực thi đó. Tổng thời gian các phiên được khử trùng lặp theo run ID và không coi là toàn bộ thời gian thu thập ban đầu nếu lịch sử đo không đầy đủ.

Peak RAM/disk là cực đại tại các lần quan sát; RAM trung bình dùng trọng số thời gian. Phiên không có đủ khoảng lấy mẫu được đánh dấu không tính. Final output gồm raw, corpus, checkpoint và sidecar, không đồng nghĩa kích thước riêng TeX/BibTeX. Nhóm không cộng disk của các phiên chồng lặp thành dung lượng corpus.
''',
'milestone1/discussion.md':'''# Thảo luận và kết luận

## Kết quả của nhóm

Nhóm đã hoàn tất việc xử lý phạm vi 25.000 ID và chốt bộ corpus MS1. Kết quả gồm nguồn đa phiên bản, metadata, references và thông tin kiểm định để các bước tiếp theo nhận biết được chất lượng đầu vào. Tỷ lệ đạt validator của bộ đã chốt là 98,56%; các trạng thái còn lại được thống kê như đặc tính của corpus bàn giao.

Bao phủ Discovery phản ánh khả năng xác định bài báo và version. Mức hiện diện source và kết quả kiểm định đánh giá các tầng khác nhau: một bài có thể có nhiều version, một version có thể chỉ có PDF, và một paper có TeX vẫn có thể không đạt quy tắc metadata/references. Vì vậy không dùng một tỷ lệ duy nhất để thay tất cả mức độ thành công.

## Dung lượng và tài liệu tham khảo

Lọc ở bước giải nén giúp hình và tệp ngoài TeX/BibTeX không đi vào working corpus, trong khi lệnh LaTeX được giữ cho parsing. Thực nghiệm dung lượng dùng cùng tập ghép cặp trước/sau lọc để tránh so sánh sai gói nén với nội dung giải nén. Các giá trị trung bình là số đo trên tập được nêu, không ngoại suy cho các paper không có cặp đo.

References được lưu theo quan hệ bài trích dẫn và tài liệu được trích dẫn. Một tài liệu xuất hiện ở nhiều paper vẫn tạo nhiều quan hệ. Thiếu arXiv ID hoặc ngày công bố không tự chứng minh truy vấn thất bại; tiêu chí đủ năm trường là đánh giá mức đầy đủ metadata, không phải độ chính xác ngữ nghĩa. Số references đã ghi nhận không bao gồm phần chưa lấy được từ dịch vụ bên ngoài.

## Diễn giải hiệu năng

Checkpoint giúp sử dụng lại kết quả khi phiên Colab bị ngắt. Các số đo resume thể hiện chi phí kiểm tra cache và thực thi những bước cần xử lý trong phiên, không phải chi phí tải mới toàn bộ assignment. RAM có thể bỏ lỡ đỉnh ngắn giữa các lần lấy mẫu; quét thư mục trên Drive cũng tạo overhead. Do đó hiệu năng được đọc cùng phạm vi, số mẫu và chế độ chạy.

## Giá trị bàn giao

Corpus chốt giữ liên kết paper/version cùng trạng thái source, metadata và references. Các bản kiểm định giúp giai đoạn sau phân biệt paper có TeX, record không có source và đầu vào không đáp ứng đầy đủ hợp đồng. Validator kiểm tra cấu trúc, trạng thái và tính nhất quán tệp; không biên dịch LaTeX hay xác minh toàn bộ ngữ nghĩa khoa học.

MS1 cung cấp một nền dữ liệu có nguồn gốc và phạm vi kiểm chứng rõ ràng. Các giới hạn của dịch vụ ngoài, dạng submission và phép đo được trình bày ở cấp hệ thống, không quy thành mức hoàn thành của riêng một thành viên.
''',
}

SETUP='''from pathlib import Path
import sys,json,hashlib
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display,HTML,Markdown
ROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'_config.yml').exists())
sys.path.insert(0,str(ROOT/'utils'))
from preliminary_results import load_members,corpus_metrics,session_members,run_range,paper_timings
folder=ROOT/'summaries/milestone1/frozen-20261127'
receipt=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))
raw=(folder/'corpus.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()==receipt['public_sha256']
papers=json.loads(raw)['papers']
assert len(papers)==25000 and len({p['paper_id'] for p in papers})==25000
members=load_members(ROOT)
sessions=session_members(ROOT,members)
measurement=corpus_metrics(members)[-1]
def table(rows):
    frame=pd.DataFrame(rows,dtype=object).where(lambda f:f.notna(),'Không áp dụng')
    def fmt(v):
        if isinstance(v,int) and not isinstance(v,bool):return f'{v:,}'.replace(',','.')
        if isinstance(v,float):return f'{v:,.2f}'.replace(',','_').replace('.',',').replace('_','.')
        return str(v)
    display(HTML(frame.map(fmt).to_html(index=False,escape=True,border=0)))
'''


def build(notebook):
    notebook('preliminary-results.ipynb',[
    ('md','''# Kết quả thu thập và chất lượng corpus

## Kết quả bộ MS1 đã chốt

Các số liệu sau tổng hợp toàn bộ năm dải được giao. Mỗi paper chỉ xuất hiện một lần. Số version được cộng từ chi tiết từng paper; không dùng một trường tổng không khớp chi tiết để thay số version của cả dải.'''),
    ('code',SETUP),
    ('code','''n=len(papers); passed=sum(p['valid'] is True for p in papers)
versions=sum(p['discovery_versions'] for p in papers)
refs=sum(p['counts']['references'] for p in papers)
source=sum(p['counts']['source_versions'] for p in papers)
no_source=sum(p['counts']['no_source_versions'] for p in papers)
table([{'Chỉ số toàn nhóm':'Paper/ID đã xử lý','Giá trị':n},
       {'Chỉ số toàn nhóm':'Discovery thành công','Giá trị':sum(p['discovery_status']=='success' for p in papers)},
       {'Chỉ số toàn nhóm':'Version xác định được','Giá trị':versions},
       {'Chỉ số toàn nhóm':'Version có source theo kiểm định','Giá trị':source},
       {'Chỉ số toàn nhóm':'Version no_source theo kiểm định','Giá trị':no_source},
       {'Chỉ số toàn nhóm':'References đã ghi nhận','Giá trị':refs},
       {'Chỉ số toàn nhóm':'References đã ghi nhận / paper được giao','Giá trị':refs/n}])
table([{'Kết quả kiểm định':'Đạt','Paper':passed,'Tỷ lệ (%)':100*passed/n},
       {'Kết quả kiểm định':'Không đạt toàn bộ quy tắc','Paper':n-passed,'Tỷ lệ (%)':100*(n-passed)/n}])
fig,ax=plt.subplots(figsize=(7,3))
ax.barh(['Bộ corpus MS1'],[passed],label='Đạt kiểm định')
ax.barh(['Bộ corpus MS1'],[n-passed],left=[passed],label='Không đạt toàn bộ quy tắc')
ax.set_xlabel('Paper');ax.legend();plt.tight_layout();plt.show()'''),
    ('md','''Tỷ lệ đạt kiểm định là tỷ lệ paper đáp ứng toàn bộ hợp đồng tại thời điểm chốt. Record no_source hợp lệ vẫn có thể đạt kiểm định. Ngược lại, references hoặc metadata không hợp lệ có thể làm paper không đạt dù source đã hiện diện. Những trường hợp này không được loại khỏi mẫu số 25.000 paper.

## Nhóm trạng thái chất lượng

Mỗi paper chỉ được đếm một lần trong từng nhóm; một paper có thể thuộc nhiều nhóm. Bảng mô tả kết quả kiểm tra của toàn corpus, không phải danh sách công việc đang chờ từng thành viên thực hiện.'''),
    ('code','''counts=Counter(code for p in papers if not p['valid'] for code in set(p['error_codes']))
labels={'upstream_failure':'Bước thu thập/xử lý không đáp ứng hợp đồng','artifact_location':'Đường dẫn artifact không khớp',
'invalid_corpus_file':'Tệp corpus không đáp ứng quy tắc','invalid_reference':'Reference không đáp ứng schema',
'invalid_source':'Source không đáp ứng quy tắc'}
table([{'Nhóm kết quả':labels.get(k,k),'Paper ghi nhận':v} for k,v in counts.most_common()])'''),
    ('md','''## Thực nghiệm kích thước trước/sau lọc

Phép đo này sử dụng tập paper có đủ sidecar trước/sau lọc trong các bản cumulative đã lưu. Đây là thực nghiệm dung lượng trên cùng tập ghép cặp, tách khỏi số đếm corpus cuối. Đơn vị trước/sau đều là bytes/paper sau khi cộng các version của paper; trung bình gộp theo trọng số số paper ghép cặp.'''),
    ('code','''table([{'Phạm vi':'Tập ghép cặp của cả nhóm','Paper có cặp đo':measurement['paired'],
        'Trước lọc (bytes/paper)':measurement['mean_before'],'Sau lọc (bytes/paper)':measurement['mean_after'],
        'Giảm dung lượng (%)':100*(1-measurement['mean_after']/measurement['mean_before'])}])'''),
    ('md','''## Thực nghiệm metadata tài liệu tham khảo

Các bản cumulative dùng cho phép đo ghi riêng paper có kết quả references đọc được, gồm danh sách rỗng hợp lệ. Tỷ lệ truy vấn đọc được và tỷ lệ reference đủ metadata có mẫu số khác nhau. Đủ metadata yêu cầu ref_arxiv_id, ref_title, ref_authors, ref_submission_date và ref_s2_id có giá trị. Các chỉ số sau thuộc phép đo đã lưu, không dùng mẫu số references corpus cuối cho tử số từ lần đo trước.'''),
    ('code','''table([{'Chỉ số thực nghiệm':'Paper có kết quả references đọc được','Tử số':measurement['retrieved'],
        'Mẫu số':measurement['discovered'],'Tỷ lệ (%)':100*measurement['retrieved']/measurement['discovered']},
       {'Chỉ số thực nghiệm':'References đủ năm trường metadata','Tử số':measurement['complete_references'],
        'Mẫu số':measurement['reference_denominator'],'Tỷ lệ (%)':100*measurement['complete_references']/measurement['reference_denominator']}])
table([{'Phạm vi':'Các bản cumulative của phép đo','References đã đọc':measurement['references'],
        'Paper có kết quả':measurement['retrieved'],'References / paper có kết quả':measurement['mean_references']}])'''),
    ])
    notebook('performance.ipynb',[
    ('md','''# Hiệu năng pipeline

## Phạm vi phép đo

Nhóm đo pipeline tích hợp trên Google Colab CPU-only. Các phiên đã lưu có phạm vi đầu vào và lượng cache khác nhau; kết quả được đọc theo phiên thực thi, không dùng để xếp hạng thành viên. Các số đo lịch sử vẫn là bằng chứng hiệu năng của hệ thống và được tách khỏi kiểm kê corpus cuối.

Wall time tính thời gian end-to-end của lệnh pipeline. Timing từng paper và Discovery ghi thời gian các event đã hoàn tất. RSS cộng trên cây tiến trình; dung lượng output đo theo các lần lấy mẫu và ở cuối phiên.'''),
    ('code',SETUP),
    ('code','''table([{'Phiên đo':i+1,'Ngày bắt đầu (UTC)':s['benchmark']['started_at'][:10],
        'Dải đầu vào':run_range(s['benchmark']),'Chế độ':'Resume',
        'Wall time (giây)':s['benchmark']['wall_seconds'],'Số mẫu RAM':s['benchmark']['sample_count']}
       for i,s in enumerate(sessions)])'''),
    ('md','''## Thời gian Discovery và xử lý paper

Các run ID được khử trùng lặp. Việc một paper được xử lý lại ở hai phiên là chi phí thực, nhưng tổng các phiên hiện có không thay cho tổng lịch sử thu thập. Không cộng thời gian của các loại event chồng lặp thành wall time.'''),
    ('code','''rows=[]
for i,s in enumerate(sessions):
    events=[json.loads(l) for l in (s['directory']/'timings.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    ds=[e for e in events if e['kind']=='discovery']; ps=[e for e in events if e['kind']=='paper']
    rows.append({'Phiên đo':i+1,'Tổng Discovery event (giây)':sum(e['elapsed_seconds'] for e in ds) if ds else None,
        'Paper event':len(ps),'Trung bình giây/paper event':sum(e['elapsed_seconds'] for e in ps)/len(ps) if ps else None})
table(rows)
frame=pd.DataFrame(paper_timings(sessions))
p=ROOT/'_static/generated/ms1-paper-timings.csv';p.parent.mkdir(parents=True,exist_ok=True);frame.to_csv(p,index=False)
display(HTML('<a href="../_static/generated/ms1-paper-timings.csv" download>Tải thời gian từng paper theo run ID (CSV)</a>'))'''),
    ('md','''## RAM và dung lượng output

RAM trung bình cần có khoảng thời gian quan sát; phiên có 0–1 mẫu được đánh dấu không tính. Peak là cực đại quan sát, có thể bỏ lỡ đỉnh ngắn. Disk bao gồm raw source, corpus và các tệp trạng thái tích lũy; không cộng các phiên chồng lặp để suy dung lượng corpus.'''),
    ('code','''rows=[]
for i,s in enumerate(sessions):
    b=s['benchmark'];r=b['ram'];d=b['disk'];ok=b['sample_count']>=2 and r['observed_seconds']>0
    rows.append({'Phiên đo':i+1,'Peak RAM (MiB)':r['peak_rss_bytes']/1024**2 if ok else None,
        'RAM trung bình (MiB)':r['time_weighted_mean_rss_bytes']/1024**2 if ok and r['time_weighted_mean_rss_bytes'] is not None else None,
        'Peak output quan sát (GiB)':d['peak_observed_bytes']/1024**3 if d.get('peak_observed_bytes') is not None else None,
        'Output cuối (GiB)':d['final_bytes']/1024**3 if d.get('final_bytes') is not None else None})
table(rows)
chosen=next(s for s in sessions if s['benchmark']['sample_count']>2)
samples=[json.loads(l) for l in (chosen['directory']/'samples.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
fig,ax=plt.subplots(figsize=(8,3))
ax.plot([v['elapsed_seconds']/60 for v in samples],[v['rss_bytes']/1024**2 for v in samples])
ax.set_xlabel('Phút quan sát');ax.set_ylabel('RSS cây tiến trình (MiB)');ax.set_title('Diễn biến RAM trong một phiên đo có nhiều mẫu')
plt.tight_layout();plt.show()'''),
    ('md','''Chi phí mạng, retry và quét thư mục Drive ảnh hưởng wall time và nhịp lấy mẫu. Resume có thể nhanh nhờ cache; các phép đo này không được ngoại suy thành tốc độ tải mới 25.000 paper. Không tái tạo RAM hoặc disk peak của những khoảng không được đo từ corpus cuối.'''),
    ])
    notebook('audit-appendix.ipynb',[
    ('md','''# Phụ lục: Nguồn số liệu và tái lập

## Bộ MS1 đã chốt

Nhóm xác nhận các thư mục sau là bộ bàn giao cuối. Bản sao số liệu kiểm định trong repository cho phép build lại báo cáo mà không gọi Drive hoặc crawl lại. Các tệp gốc không bị sửa; SHA-256 và phương pháp trích xuất được giữ trong provenance.'''),
    ('code',SETUP),
    ('code','''table([{'Dải dữ liệu':i+1,'Thư mục đã chốt':'https://drive.google.com/drive/folders/'+receipt['source_folders'][src['member']],
        'Tệp gốc':src['original_name'],'Thời điểm dữ liệu (UTC)':src['generated_at'],
        'SHA-256 gốc':src['original_sha256']} for i,src in enumerate(receipt['sources'])])'''),
    ('md','''## Quy tắc tổng hợp

Số paper, version, source và references của bộ cuối được đọc từ chi tiết từng paper trong audit hoặc validation của bản kiểm kê bàn giao. Các số tổng không khớp chi tiết không được dùng thay cho dữ liệu từng paper. Mỗi định danh chỉ được tính một lần. References là số quan hệ đã đọc được theo validator, không phải tập tài liệu duy nhất toàn cục.

Phép đo dung lượng và metadata references dùng các bản cumulative trước đó trên năm dải, có mẫu số riêng. Đây là số liệu thực nghiệm được giữ theo phạm vi đo, không phải một lần xuất lại toàn bộ bộ chốt.'''),
    ('code','''table([{'Dải phép đo':i+1,'Dải ID':m['assigned_range'],'Ngày xuất cumulative (UTC)':m['cumulative']['generated_at'],
        'Paper có cặp đo':m['cumulative']['sizes']['paired_papers']} for i,m in enumerate(members)])'''),
    ('md','''## Cấu hình và định danh benchmark

Thông tin dưới đây xác định phiên thực thi, phiên bản code và môi trường. Xác nhận CPU-only là dữ liệu do notebook thu thập hoặc người chạy ghi; thông tin môi trường không được suy từ tốc độ chạy.'''),
    ('code','''table([{'Phiên đo':i+1,'Run ID':s['benchmark']['run_id'],
        'Source commit':s['benchmark']['environment'].get('source_commit'),
        'CPU logic':s['benchmark']['environment'].get('logical_cpu_count'),
        'CPU-only ghi nhận':s['benchmark']['environment'].get('cpu_only_confirmation'),
        'Bắt đầu (UTC)':s['benchmark']['started_at'],'Kết thúc (UTC)':s['benchmark']['finished_at']}
       for i,s in enumerate(sessions)])'''),
    ('md','''## Biên dịch báo cáo

README của repository hướng dẫn cài Python, dependencies, kiểm thử và build. Jupyter Book bắt buộc thực thi notebook; các bảng, biểu đồ và CSV timing được sinh khi build, không dán ảnh chụp kết quả. Input code được ẩn khỏi HTML để bản nộp tập trung vào phương pháp và phân tích.

| Nguồn | Cách dùng |
|---|---|
| Bộ chốt và validation chi tiết | Kết quả thu thập, trạng thái chất lượng toàn nhóm |
| Cumulative và sidecar | Thực nghiệm kích thước, mức đầy đủ metadata references |
| Benchmark, samples, timings | Thời gian, RAM, disk của phiên đo |
| Provenance | Định danh nguồn, phạm vi và SHA-256 |

Đề bài: [Milestone 1 — Data Crawling](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/crawling/).'''),
    ])
