"""Submission report based on the evidence received 9 November 2026."""
PAGES = {
'intro.md': '''# arXiv Project, nhóm 6

Nhóm xây dựng corpus source LaTeX theo phiên bản, metadata bài báo và tài liệu tham khảo để phục vụ parsing và matching ở các milestone tiếp theo.

## Milestone 1: Thu thập dữ liệu

Năm audit xác nhận đủ 25.000 ID và lookup thành công trên các dải được giao. Kiểm định vẫn ghi nhận paper chưa đạt; mức bao phủ Discovery được đọc riêng với mức hoàn thiện source và chất lượng.

Thống kê tích lũy đã có cho TV2–TV5, còn thiếu TV1. Cumulative TV5 được tạo trước lần sửa bốn lookup nên được ghi theo thời điểm riêng. Kích thước và references hiện phản ánh bốn snapshot đã nộp, chưa phải toàn bộ corpus năm thành viên.

- [Báo cáo Milestone 1](milestone1/index.md)
- [Mã nguồn pipeline](https://github.com/LeoTkiet/arxiv-data-science)
- [Repository báo cáo](https://github.com/HoangLongNha/arxiv-project-report)
- [Đề bài chính thức](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/crawling/)
''',
'milestone1/index.md': '''# Milestone 1: Thu thập dữ liệu arXiv

Pipeline xác định version, tải source, trích xuất TeX/BibTeX, chuẩn hóa metadata, truy vấn references và kiểm định đầu ra. Mỗi thành viên xử lý một dải 5.000 ID; tổng phạm vi là 25.000 ID.

Năm audit toàn dải xác nhận không còn ID chưa ghi nhận hoặc lookup chưa giải quyết. Kết quả này chứng minh bao phủ Discovery; số paper đạt kiểm định và mức đầy đủ source được báo riêng. Audit TV2 mới đã sửa cờ hoàn tất về false, phù hợp việc còn paper chưa đạt, nhưng trường tổng version vẫn chưa khớp chi tiết.

Báo cáo phân tích cumulative TV2–TV5 và các phiên Colab đã nộp. Cumulative TV5 trước sửa lookup không được ghép với audit sau sửa thành một snapshot. TV1 chưa có cumulative nên chưa được tính vào tổng kích thước và references.

- [Phương pháp](methodology.md)
- [Thiết lập và mẫu số](experimental-setup.md)
- [Kết quả thu thập và chất lượng](preliminary-results.ipynb)
- [Hiệu năng](performance.ipynb)
- [Thảo luận và hạn chế](discussion.md)
- [Bằng chứng và tái lập](audit-appendix.ipynb)
''',
'milestone1/discussion.md': '''# Thảo luận và kết luận

## Bao phủ đầu vào và mức hoàn thiện corpus

Năm audit xác nhận đủ 25.000 record và 25.000 lookup thành công. Checkpoint giúp nhóm tiếp tục sau gián đoạn và thử lại riêng ID hoặc stage lỗi. Lookup thành công cho biết đã nhận diện bài báo và version; source/corpus và kiểm định còn có thể chưa đạt.

Cumulative TV2–TV5 thống kê dữ liệu tích lũy qua nhiều phiên. Tỷ lệ paper đủ source thấp hơn bao phủ Discovery vì mỗi paper có thể có nhiều version, gặp lỗi tải/giải nén hoặc không có source TeX. Trạng thái no_source được giữ riêng để không coi mọi trường hợp thiếu TeX là lỗi mạng. Số download success và số source có tệp còn chênh lệch; cần kiểm tra checkpoint, đường dẫn và tệp trước khi dùng số trạng thái làm số source thực có.

## Kích thước và references

Chỉ giữ TeX/BibTeX làm giảm dung lượng trên tập paper có đủ cặp đo. So sánh dùng kích thước giải nén trước lọc và corpus sau lọc; không so gói nén với dữ liệu đã giải nén. Cặp đo thiếu được loại khỏi mẫu số, còn số paper được tính luôn đi kèm kết quả.

References được đếm theo paper trích dẫn, loại dòng trùng trong cùng paper. Cùng tài liệu được nhiều paper trích dẫn vẫn được đếm ở mỗi quan hệ. Trung bình bao gồm danh sách rỗng hợp lệ; truy vấn lỗi hoặc chưa được index không được coi là danh sách rỗng. Tỷ lệ truy vấn đọc được và tỷ lệ reference đủ metadata là hai chỉ số riêng.

TV2 có mức bao phủ references thấp hơn các dải còn lại; cần xem checkpoint references lỗi trước khi dùng cho matching. Tiêu chí đủ năm trường khá chặt vì nhiều tài liệu không có arXiv ID. Nó không thay độ chính xác nội dung do Semantic Scholar cung cấp.

## Chất lượng và chuẩn bị MS2

Một paper có thể vướng nhiều loại lỗi: stage upstream, artifact, corpus hoặc metadata/references. Cần phân loại theo paper/version rồi thử lại stage cần thiết. Paper chưa đạt validator vẫn có thể có TeX sử dụng được; có TeX cũng không bảo đảm mọi trường khác hợp lệ.

Audit TV2 mới đã thống nhất cờ hoàn tất với số paper fail, nhưng known_version_count ghi 3.887 trong khi cộng versions của 5.000 paper trong chính audit được 7.987, khớp cumulative. Báo cáo giữ tệp gốc, dùng cumulative cho số version và ghi mâu thuẫn trong phụ lục. TV5 đã giải quyết bốn lookup, nhưng lần thử source 2410.05044 trong bộ bằng chứng sửa lỗi vẫn bị IncompleteRead.

Validator kiểm tra cấu trúc, định danh, trạng thái và tệp; chưa biên dịch LaTeX hay đánh giá toàn bộ ngữ nghĩa. MS2 cần giữ liên kết paper/version, xử lý record không có source và dùng danh sách lỗi để tránh coi đầu vào thiếu là kết quả parsing rỗng hợp lệ.

## Giới hạn thực nghiệm

TV1 còn thiếu cumulative. Cumulative TV5 trước sửa lookup chưa phản ánh sáu version mới xác định và các thay đổi sau đó. Tổng TV2–TV5 mô tả các snapshot đã nộp, không phải số liệu đồng thời mới nhất hay tổng corpus năm thành viên.

Benchmark chủ yếu chạy resume. Phiên TV1 mới có toàn dải đầu vào và mẫu RAM trên Colab CPU-only nhưng dùng cache, nên chưa đo chi phí tải mới toàn dải. TV2/TV5 thiếu mẫu RAM đại diện trong các phiên đã nộp. Không thể khôi phục runtime, RAM hay disk peak của phiên không có log từ cumulative JSON.

Để chốt số liệu corpus hiện tại của cả nhóm, cần cumulative TV1 và bản TV5 sau sửa. Để kết luận hiệu năng end-to-end của toàn quá trình, cần lịch sử đo đầy đủ hoặc benchmark Colab CPU-only có biên đo thống nhất. Báo cáo trình bày các số đo có bằng chứng và giữ rõ những giới hạn này.
''',
}


def build(notebook, setup, previous_build):
    captured = {}
    previous_build(lambda name, content: captured.update({name: content}), setup)
    setup = setup.replace('session_members, coverage_rows)',
        'session_members, coverage_rows, corpus_metrics, snapshot_rows, percentage, paper_timings)')
    notebook('preliminary-results.ipynb', [
        ('md', '''# Kết quả thu thập và chất lượng dữ liệu

## Bao phủ 25.000 ID đầu vào

Các audit toàn dải xác nhận mỗi thành viên có đủ 5.000 record, không còn ID chưa ghi nhận và lookup chưa giải quyết. Bao phủ Discovery được đọc riêng với mức hoàn thiện source và kiểm định.'''),
        ('code', setup),
        ('code', '''table([{k:v for k,v in row.items() if k!='Đã chạy theo báo cáo nhóm'} for row in progress_rows(members)])
audits=[m['audit'] for m in members if m['verified']]
assigned=sum(a['assigned_input_count'] for a in audits)
discovered=sum(a['discovery_statuses'].get('success',0) for a in audits)
passed=sum(a['validation_pass_papers'] for a in audits)
failed=sum(a['validation_fail_papers'] for a in audits)
table([{'Chỉ số theo audit toàn nhóm':'Discovery thành công','Số paper':discovered,
        'Mẫu số':assigned,'Tỷ lệ (%)':percentage(discovered,assigned)},
       {'Chỉ số theo audit toàn nhóm':'Paper đạt validator','Số paper':passed,
        'Mẫu số':passed+failed,'Tỷ lệ (%)':percentage(passed,passed+failed)},
       {'Chỉ số theo audit toàn nhóm':'Paper chưa đạt validator','Số paper':failed,
        'Mẫu số':passed+failed,'Tỷ lệ (%)':percentage(failed,passed+failed)}])'''),
        ('md', '''## Source và corpus tích lũy

Số liệu sau lấy từ cumulative TV2–TV5 trên bốn dải 5.000 ID. TV1 chưa có cumulative. Bản TV5 trước sửa bốn lookup có 4.996 Discovery thành công, còn audit sau sửa xác nhận 5.000. Dòng gộp chỉ cộng các snapshot cumulative cùng loại, chưa phải tổng corpus năm thành viên.

Download success là trạng thái checkpoint. Source có tệp cần đúng đường dẫn và tệp khác rỗng; corpus có TeX/Bib cần extract thành công và có tệp phù hợp. Paper đủ source/corpus yêu cầu mọi version đã biết đáp ứng cả hai điều kiện.'''),
        ('code', '''metrics=corpus_metrics(members)
table([{'Phạm vi':r['member'],'Paper Discovery':r['discovered'],'Version đã biết':r['versions'],
        'Download success (checkpoint)':r['download_success'],'Source xác minh có tệp':r['source_files'],
        'Version có corpus TeX/Bib':r['corpus_versions'],'Paper đủ mọi version':r['complete_papers']} for r in metrics])
table([{'Phạm vi':r['member'],'Discovery / ID được giao (%)':percentage(r['discovered'],r['assigned']),
        'Download success / version (%)':percentage(r['download_success'],r['versions']),
        'Source có tệp / version (%)':percentage(r['source_files'],r['versions']),
        'Paper đủ source-corpus / ID được giao (%)':percentage(r['complete_papers'],r['assigned'])} for r in metrics])
table([{'Thành viên':m['member'],'Version no_source':m['cumulative']['download_statuses'].get('no_source',0),
        'Version download api_error':m['cumulative']['download_statuses'].get('api_error',0)}
       for m in members if m['cumulative']])'''),
        ('md', '''Số paper thu thập thành công phụ thuộc tiêu chí: tìm được metadata, đủ source/corpus mọi version, hay đạt toàn bộ validator. Báo cáo công bố cả ba mức; Discovery 100% không có nghĩa corpus hoàn thiện 100%. No_source có thể là đầu ra hợp lệ cho PDF-only và được giữ riêng.

## Kích thước trước và sau lọc hình

Đơn vị là bytes/paper, cộng các version trong mỗi paper. Trước lọc dùng kích thước giải nén từ sidecar, sau lọc dùng tổng TeX/BibTeX được giữ; lệnh hình trong LaTeX không bị sửa. Chỉ paper có đủ cặp đo mới vào mẫu số. Trung bình gộp dùng trọng số số paper có cặp đo.'''),
        ('code', '''table([{'Phạm vi':r['member'],'Paper có cặp đo':r['paired'],
        'Trước lọc (bytes/paper)':r['mean_before'],'Sau lọc (bytes/paper)':r['mean_after'],
        'Giảm dung lượng (%)':percentage(r['mean_before']-r['mean_after'],r['mean_before'])
            if r['mean_before'] is not None and r['mean_after'] is not None else None} for r in metrics])'''),
        ('md', '''## References và mức đầy đủ metadata

References đọc được gồm success hoặc no_data có JSON hợp lệ. Danh sách rỗng được tính vào mẫu số trung bình. Tỷ lệ đọc được lấy số paper Discovery thành công của cùng snapshot làm mẫu số, chưa gồm lookup lỗi.

Metadata đầy đủ yêu cầu cả năm trường ref_arxiv_id, ref_title, ref_authors, ref_submission_date và ref_s2_id có giá trị. Đây là độ đầy đủ theo quy tắc công cụ, không phải tỷ lệ API không lỗi hay độ chính xác ngữ nghĩa. References được đếm theo quan hệ paper–reference, loại trùng trong từng paper; không loại cùng tài liệu được nhiều paper trích dẫn.'''),
        ('code', '''table([{'Phạm vi':r['member'],'References đã đọc':r['references'],'Paper có kết quả đọc được':r['retrieved'],
        'References/paper có kết quả':r['mean_references'],
        'Truy vấn có kết quả đọc được (%)':percentage(r['retrieved'],r['discovered']),
        'References đủ metadata':r['complete_references'],
        'Metadata đủ 5 trường (%)':percentage(r['complete_references'],r['reference_denominator'])} for r in metrics])
table([{'Phạm vi':r['member'],'Success':r['reference_statuses'].get('success',0),
        'No data':r['reference_statuses'].get('no_data',0),'Not indexed':r['reference_statuses'].get('not_indexed',0),
        'API/error khác':sum(v for k,v in r['reference_statuses'].items() if k not in {'success','no_data','not_indexed'})}
       for r in metrics])'''),
        ('md', '''TV2 có nhiều checkpoint references lỗi trong snapshot đã gửi; mức bao phủ thấp hơn các dải còn lại. Không suy số reference của paper lỗi bằng trung bình các paper đã truy vấn được.

## Chất lượng theo audit toàn dải

Tỷ lệ đạt dùng số paper đã kiểm định làm mẫu số. Audit và cumulative có thể khác ngày; validation cũ trong cumulative không thay audit mới.'''),
        ('code', '''quality=quality_rows(members)
table(quality)
fig,ax=plt.subplots(figsize=(8,4))
ax.bar([r['Thành viên'] for r in quality],[r['Đạt'] for r in quality],label='Đạt kiểm định')
ax.bar([r['Thành viên'] for r in quality],[r['Còn lỗi'] for r in quality],
       bottom=[r['Đạt'] for r in quality],label='Chưa đạt')
ax.set_ylabel('Paper đã kiểm định');ax.legend();plt.tight_layout();plt.show()'''),
        ('md', '''Một paper chỉ đếm một lần trong từng nhóm lỗi; một paper có thể thuộc nhiều nhóm. Các nhóm không cộng thành tổng paper chưa đạt và chưa đủ để quy trách nhiệm cho một thành viên.'''),
        ('code','table(error_groups(members))'),
        ('md', '''## Thời điểm và phạm vi số liệu

TV1 có audit toàn dải nhưng chưa có cumulative. TV5 dùng audit sau sửa lookup và cumulative trước sửa; hai số Discovery khác nhau do thời điểm. Không sửa tệp gốc hoặc cộng thêm bốn paper vào trung bình cũ. Các mốc UTC cho phép đối chiếu từng phép kiểm tra.'''),
        ('code','table(snapshot_rows(members))'),
    ])

    performance=captured['performance.ipynb']
    performance[1]=('code',setup)
    performance.insert(3,('md','''TV1 bổ sung phiên resume ngày 07/11 UTC trên toàn dải 5.000 ID, chạy Colab CPU-only. Phiên có mẫu RAM và timing từng paper nhưng dùng lại nhiều checkpoint. Exit 1 được giữ đúng artifact; audit sau phiên không đổi trạng thái kết thúc phép đo.'''))
    performance.extend([
        ('md','''## Thời gian từng paper trong các phiên đã đo

CSV được tạo khi build từ paper event, có run ID để phân biệt paper được xử lý lại qua nhiều phiên. Thời gian có thể gồm kiểm tra cache và retry; không dùng làm thời gian crawl mới của paper đó.'''),
        ('code','''timing_frame=pd.DataFrame(paper_timings(sessions))
output=ROOT/'_static/generated/ms1-paper-timings.csv'
output.parent.mkdir(parents=True,exist_ok=True)
timing_frame.to_csv(output,index=False)
display(HTML('<a href="../_static/generated/ms1-paper-timings.csv" download>Tải CSV thời gian từng paper theo run</a>'))
table(timing_frame.head(10).to_dict('records'))'''),
        ('md','''## Mức đáp ứng bằng chứng hiệu năng

Phiên TV1 toàn dải cung cấp wall time, thời gian Discovery, thời gian từng paper và RAM cây tiến trình trên Colab CPU-only cho một lượt resume. Các phiên TV3/TV4 bổ sung số đo hoạt động thực tế. TV2/TV5 chỉ có 0–1 mẫu RAM nên không công bố peak/mean đại diện.

Khoảng lấy mẫu có thể dài hơn cấu hình vì quét output trên Drive. Disk peak là cực đại tại các lần quan sát, không bảo đảm đã thấy mọi đỉnh. Final output gồm raw, corpus, checkpoint và sidecar. Lịch sử chưa đủ để khôi phục tổng runtime/RAM/disk peak của quá trình thu thập ban đầu; không ước lượng các giá trị này từ cumulative.'''),
    ])
    notebook('performance.ipynb',performance)

    notebook('audit-appendix.ipynb',[
        ('md','''# Phụ lục: Bằng chứng và tái lập

## Bộ bằng chứng được sử dụng

Báo cáo chọn audit toàn dải mới của TV1/TV2 và giữ audit TV3/TV4/TV5 đã đối chiếu. Cumulative TV2–TV5 được nhập nguyên byte, kiểm phạm vi, định danh và hash. Snapshot cũ và benchmark trước được giữ để truy vết, không cộng trùng cùng run ID.

ZIP/JSON bổ sung do thành viên gửi trực tiếp; pipeline log và bản sao dữ liệu riêng không được công bố. Kiểm hash bảo đảm đúng tệp đã nhập, chưa thay việc kiểm định độc lập corpus trên Drive.'''),
        ('code',setup),
        ('code','''for s in sessions:
    p=s['provenance']
    source='['+p['archive_name']+']('+p['drive_url']+')' if p.get('drive_url') else p['archive_name']+' (gửi trực tiếp)'
    display(Markdown(s['session']+': '+source+'; SHA-256 ZIP: `'+p['archive_sha256']+'`'))
for m in members:
    for item in (m['provenance'] or {}).get('supplementary_archives',[]):
        display(Markdown(m['member']+': '+item['archive_name']+'; SHA-256: `'+item['sha256']+'`'))
    for item in (m['provenance'] or {}).get('supplementary_files',[]):
        display(Markdown(m['member']+': '+item['filename']+'; SHA-256: `'+item['sha256']+'`'))
    if m['cumulative']:
        receipt=json.loads((ROOT/'summaries/milestone1/cumulative'/m['member']/'provenance.json').read_text(encoding='utf-8'))
        display(Markdown(m['member']+' cumulative — '+receipt['original_filename']+'; SHA-256: `'+receipt['sha256']+'`'))
table(snapshot_rows(members))'''),
        ('md','''## Phạm vi và nhất quán audit

Năm audit được đối chiếu với dải cá nhân. TV1 có inputs và audit trùng nội dung trong ZIP; TV2/TV5 liệt kê đủ định danh. TV2 mới ghi false khi còn paper fail, thay cờ true mâu thuẫn trước đó. Các audit đều false vì validation còn lỗi; điều này không phủ nhận 25.000 lookup thành công.

Riêng TV2, known_version_count ghi 3.887 nhưng cộng versions trong paper_results của chính audit được 7.987, cũng bằng cumulative. Cờ hoàn tất đã sửa nhưng trường tổng version cần bên xuất kiểm tra lại. Bảng sau giữ nguyên số gốc để truy vết; thống kê source dùng 7.987 từ cumulative.'''),
        ('code','table(coverage_rows(members))\ntable(assignment_outcomes(members))'),
        ('md','''## Môi trường từng phiên đo

Xác nhận CPU-only là thông tin notebook ghi lại. Dòng nhắc kiểm tra CPU-only của TV2 chưa phải xác nhận đã thực hiện. Run resume không được đổi thành benchmark fresh bằng cách đổi nhãn. Với ZIP TV1 mới, run ID được đọc từ đối số --run-id đã ghi vì benchmark không có trường run_id cấp gốc.'''),
        ('code','''table([{'Phiên':s['session'],'Run ID':s['benchmark']['run_id'],
        'Bắt đầu (UTC)':s['benchmark']['started_at'],'Kết thúc (UTC)':s['benchmark']['finished_at'],
        'Source commit':s['benchmark']['environment'].get('source_commit'),
        'Colab':s['benchmark']['environment'].get('is_colab'),
        'CPU logic':s['benchmark']['environment'].get('logical_cpu_count'),
        'CPU-only ghi nhận':s['benchmark']['environment'].get('cpu_only_confirmation')} for s in sessions])'''),
        ('md','''## Tái lập

Cài môi trường theo README, chạy kiểm thử rồi build Jupyter Book. Bảng, biểu đồ và CSV timing tính lại từ artifacts đã commit, không gọi API crawl khi build. Code tính toán được ẩn khỏi HTML.

[MS1_Cumulative_Statistics.ipynb](https://colab.research.google.com/github/HoangLongNha/arxiv-project-report/blob/main/colab/MS1_Cumulative_Statistics.ipynb) xuất thống kê corpus hiện có. Dừng tiến trình ghi, chọn đúng thành viên và data. Export đọc checkpoint, sidecar và tệp thực tế, kiểm tra thay đổi trong lúc đọc; không tải lại paper hoặc sửa corpus. Validation trong cumulative là báo cáo đã lưu, không phải audit mới.

| Tệp | Phạm vi |
|---|---|
| assignment-audit.json | Coverage và kiểm định trên dải cá nhân |
| cumulative-statistics.json | Toàn dải từ dữ liệu tích lũy tại một thời điểm |
| statistics.json | Paper được manifest riêng lượt chạy chọn |
| inputs.json | Dải dự định audit; không thay kết quả thực thi |
| benchmark/samples/timings | Thời gian và tài nguyên một phiên |
| provenance.json | Nguồn và SHA-256 của bằng chứng |

## Dữ liệu còn cần bổ sung

TV1 cần cumulative toàn dải. TV5 cần xuất lại sau sửa lookup để đồng bộ thời điểm với audit mới. Muốn kết luận benchmark thu thập ban đầu, cần lịch sử đo đầy đủ hoặc phép đo mới với biên đo và môi trường Colab CPU-only được xác nhận.'''),
    ])
