"""MS1 prose and evidence-scoped notebook sections, updated 6 November 2026."""
PAGES = {
'intro.md': '''# arXiv Project, nhóm 6

Nhóm xây dựng corpus bài báo arXiv gồm source LaTeX theo phiên bản, metadata và tài liệu tham khảo từ Semantic Scholar. Corpus phục vụ parsing ở Milestone 2 và matching ở Milestone 3.

## Milestone 1: Thu thập dữ liệu

Phạm vi được giao là 25.000 arXiv ID, chia đều cho năm thành viên. Nhóm báo cáo đã chạy hết các dải cá nhân. Audit được nộp đến ngày 06/11/2026 xác nhận đủ record cho bốn dải TV2–TV5, tương ứng 20.000 ID. TV3 và TV4 đã bổ sung audit toàn dải; cả hai không còn ID chưa ghi nhận hoặc lookup chưa giải quyết trong lần kiểm tra ngày 04/11.

Kết quả thu thập và chất lượng được trình bày theo ngày kiểm tra. Một số paper vẫn còn lỗi validation; thống kê kích thước và references toàn corpus chưa được xuất. Các lượt resume riêng được giữ trong phần hiệu năng để mô tả những phiên thực sự đã đo.

- [Báo cáo Milestone 1](milestone1/index.md)
- [Mã nguồn pipeline](https://github.com/LeoTkiet/arxiv-data-science)
- [Repository báo cáo](https://github.com/HoangLongNha/arxiv-project-report)
- [Đề bài chính thức](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/)
''',
'milestone1/index.md': '''# Milestone 1: Thu thập dữ liệu arXiv

Pipeline nhận dải ID, xác định phiên bản, tải source, tạo corpus TeX/BibTeX, chuẩn hóa metadata và lấy references. Mỗi thành viên chạy pipeline tích hợp trên dải 5.000 ID cá nhân.

Audit hiện có xác nhận đủ record đầu vào cho TV2–TV5. Bốn dải này có 19.996 lookup thành công và bốn lookup còn lỗi, theo các lần audit ngày 02–04/11/2026. TV1 chưa có bộ audit trong nguồn được cung cấp. Các con số về validation mô tả snapshot được kiểm tra, chưa phản ánh những thay đổi sau thời điểm đó.

Phần phương pháp giải thích cách hệ thống thu thập và kiểm định dữ liệu. Phần kết quả dùng audit toàn dải; hiệu năng được gắn với từng phiên đo. Nguồn ZIP, thời điểm và định danh run nằm trong phụ lục.
''',
'milestone1/experimental-setup.md': '''# Thiết lập thực nghiệm và cách đánh giá

## Dữ liệu và môi trường

Mỗi thành viên xử lý dải 5.000 ID được phân công. Các phiên có thể bị gián đoạn rồi chạy tiếp từ checkpoint.

Môi trường benchmark theo đề bài là Google Colab CPU-only. Cấu hình, commit source, mốc thời gian và xác nhận CPU-only do từng run ghi lại được trình bày ở phụ lục. Các run có chế độ cache và phạm vi khác nhau, nên chưa dùng để xếp hạng tốc độ giữa thành viên.

## Tiến độ, kết quả và chất lượng

| Cấp đánh giá | Đơn vị và cách xác định |
|---|---|
| Tiến độ đầu vào | ID có record, ID chưa ghi nhận và lookup chưa giải quyết trên đúng dải 5.000 ID |
| Kết quả thu thập | Paper phát hiện được, version đã biết, source/corpus và metadata/references đã lưu |
| Chất lượng | Paper được kiểm định, số đạt/chưa đạt, loại lỗi và cảnh báo |

Một record lỗi cho biết ID đã được thử xử lý. Lookup chỉ được xem là giải quyết khi có kết quả thành công hoặc không tìm thấy hợp lệ. Cờ hoàn tất audit còn xét validation và diagnostics, nên được đọc riêng với tiến độ chạy ID.

## Thống kê corpus tích lũy

Thống kê toàn dải phải đọc checkpoint Discovery của mọi ID được giao, dùng manifest làm dữ liệu dự phòng khi không có checkpoint, rồi đối chiếu các stage và tệp hiện có. Mỗi paper được nhận diện bằng arXiv ID; source/corpus dùng cặp ID và version. References lấy từ tệp hiện hành của từng paper để tránh đếm lại qua các phiên.

Công cụ thống kê cũ chỉ chọn paper trong manifest của một lượt hoàn tất. Vì vậy một lượt resume sáu ID có thể tạo statistics sáu ID dù thư mục dữ liệu đã tích lũy gần đủ assignment. Bản thống kê mới có phạm vi riêng cho toàn dải và không mang nhãn benchmark của lượt cuối.

| Chỉ số | Mẫu số/phạm vi |
|---|---|
| Bao phủ đầu vào | ID có record / ID được giao |
| Discovery thành công | Paper phát hiện được / ID được giao của dải xét |
| Tải source | Version download thành công theo checkpoint; số có tệp thực tế được ghi riêng |
| Paper đủ source | Mọi version đã biết có source và corpus, theo quy tắc kiểm tra |
| Validation pass | Paper đạt / paper đã kiểm định; báo riêng paper chưa được kiểm định |
| Kích thước trước/sau lọc | Cùng tập paper có đủ cặp đo, cộng các version của từng paper |
| References trung bình | Tổng references / paper có kết quả truy vấn đọc được, gồm danh sách rỗng hợp lệ |
| Metadata references đầy đủ | References đủ trường / references đã đọc |

Giá trị thiếu không được thay bằng 0. Kích thước trước lọc lấy từ sidecar trích xuất; nếu sidecar không còn thì chưa tính được cặp đo. Thống kê đọc các báo cáo validation đã lưu; muốn kết luận về chất lượng hiện tại phải audit lại.

## Thời gian, RAM và dung lượng

Thời gian và RAM mô tả các phiên được đo. Khi tổng hợp, chỉ đếm mỗi run ID một lần; chi phí xử lý lại ID vẫn là thời gian đã sử dụng. Tổng thời gian hoạt động của các phiên khác với thời gian lịch có cả lúc nghỉ/ngắt máy. Số liệu từ một phần phiên chạy được ghi rõ là một phần lịch sử.

RAM gộp được tính từ các phiên có đủ mẫu, theo trọng số thời gian quan sát; peak là cực đại đã quan sát. Không thể khôi phục RAM hoặc runtime của phiên không có log từ corpus cuối. Final disk đo cả output root tại mốc kết thúc, có thể gồm dữ liệu tích lũy, raw source, corpus, checkpoint và sidecar. Nó không phải riêng kích thước corpus TeX/BibTeX.
''',
'milestone1/discussion.md': '''# Thảo luận, hạn chế và kết luận

## Kết quả đã xác minh

Audit TV2–TV5 xác nhận mỗi dải đã có record cho đủ 5.000 ID. TV3 và TV4 có thêm bằng chứng toàn dải: mọi lookup đều thành công trong audit ngày 04/11, với lần lượt 4.820 và 4.882 paper đạt validation. TV5 còn bốn lookup lỗi trong bản ngày 03/11. Phần assignment của TV1 mới có thông tin tiến độ do nhóm cung cấp.

Các kết quả này ghi nhận tiến độ đầu vào và những paper đã được kiểm tra. Số source, kích thước và references cần được tổng hợp từ dữ liệu tích lũy. Statistics của lượt resume cuối không đủ để suy các chỉ số đó cho toàn nhóm.

## Chất lượng và ảnh hưởng tới MS2

TV3 còn 180 paper chưa đạt, TV4 còn 118, theo audit được nộp. Validator có thể báo lỗi do stage upstream, tệp/đường dẫn hoặc trạng thái checkpoint chưa nhất quán. Mỗi paper cần được xem theo version và loại lỗi trước khi quyết định chạy lại bước nào. Một lỗi references cũng có thể làm paper fail dù source LaTeX vẫn hiện diện.

Audit TV2 vẫn có mâu thuẫn giữa cờ hoàn tất và số paper fail. TV5 còn lỗi Discovery và validation. Những bản này cần được xác minh lại trước khi chốt chất lượng cuối cùng. Các số đếm trong báo cáo giữ nguyên theo nguồn và ngày audit, không tự chuyển thành trạng thái của corpus ngày 06/11.

Trước MS2, nhóm cần kiểm tra các version thiếu source/corpus và liên kết metadata. Trường hợp PDF-only được giữ trạng thái riêng. Những tệp bị báo rỗng/nhị phân cần kiểm tra mẫu; validator không biên dịch LaTeX và không kiểm chứng toàn bộ ngữ nghĩa nội dung.

## Giới hạn của phép đo

Benchmark hiện có ghi lại một số phiên resume. Các run đã được khử trùng lặp theo định danh; tổng thời gian được ghi là thời gian của các phiên đã nộp. Chưa có đủ lịch sử để coi đó là toàn bộ chi phí thu thập 25.000 ID hoặc một benchmark fresh thống nhất.

Mẫu RAM có thể bỏ lỡ đỉnh ngắn. RSS của cây tiến trình có thể đếm shared pages nhiều lần; thao tác quét file trên Drive cũng làm khoảng lấy mẫu dài hơn cấu hình. Dung lượng output được đo theo mốc thời gian, gồm cả dữ liệu các phiên trước. Kích thước trước/sau lọc phải dùng cùng tập dữ liệu giải nén.

## Phần cần hoàn thiện

Nhóm cần bổ sung audit TV1, rà soát các lỗi còn mở và xuất thống kê tích lũy trên các dải cá nhân. Công cụ đọc checkpoint/corpus đã được chuẩn bị trong repository báo cáo; thao tác này không crawl lại dữ liệu. Những tệp thống kê được xuất sẽ cung cấp số source/corpus, cặp đo kích thước và references cho phần kết quả.

Pipeline đã tích hợp các bước thu thập và QA. Bốn assignment có bằng chứng bao phủ record đầy đủ, nhưng chất lượng và thống kê cuối cùng của cả nhóm vẫn cần các bước trên trước khi nghiệm thu.
''',
}


def build(notebook, setup):
    setup = setup.replace('session_members, coverage_rows)', 'session_members, coverage_rows, cumulative_rows)')
    notebook('preliminary-results.ipynb', [
    ('md', '''# Kết quả thu thập và chất lượng dữ liệu

## Tiến độ xử lý đầu vào

'''),
    ('code', setup),
    ('code', 'table(progress_rows(members))'),
    ('md', '''Bốn dải có audit tương ứng 20.000 ID được ghi nhận, trong đó 19.996 lookup thành công và bốn còn lỗi. Đây là kết quả của các dải đã đối chiếu, chưa phải tổng kết 25.000 ID. Cờ hoàn tất audit còn xét validation và không được dùng thay riêng số ID đã xử lý.

## Dữ liệu được ghi nhận trên toàn dải

Số version dưới đây được cộng từ dữ liệu mà validator đọc được. Nếu một kết quả kiểm định không đọc được, số version có thể thiếu; chưa dùng cột này thay tổng version xác định từ toàn bộ Discovery.'''),
    ('code', 'table(assignment_outcomes(members))'),
    ('md', '''### Source, kích thước corpus và references

Các ZIP mới của TV3/TV4 đã có audit, nhưng chưa có thống kê tích lũy đầy đủ. Statistics TV3 vẫn chỉ chứa 828 ID; bản TV4 cuối và TV5 trước đó chỉ chứa sáu ID. Hai phiên TV4 có audit bổ sung chưa có statistics của snapshot hoàn tất.

Các chỉ số sau cần được xuất từ checkpoint và dữ liệu tích lũy trên đúng dải 5.000 ID. Chúng sẽ được bổ sung khi có tệp thống kê toàn dải; những giá trị của lượt resume cuối không được dùng làm trung bình toàn corpus.'''),
    ('code', '''available = [m for m in members if m['cumulative']]
if available:
    table(cumulative_rows(members))
    table([{'Thành viên': m['member'], 'Paper có cặp đo': m['cumulative']['sizes']['paired_papers'],
            'Trước lọc (bytes/paper)': m['cumulative']['sizes']['mean_before_bytes'],
            'Sau lọc (bytes/paper)': m['cumulative']['sizes']['mean_after_bytes'],
            'References/paper truy vấn được': m['cumulative']['references']['mean_per_retrieved_paper']}
           for m in available])
    table([{'Thành viên':m['member'],
            'Paper truy vấn references đọc được':m['cumulative']['counts']['retrieved_reference_papers'],
            'Paper Discovery thành công':m['cumulative']['counts']['discovery_success_papers'],
            'References đủ metadata':m['cumulative']['references']['complete_numerator'],
            'References đã đọc':m['cumulative']['references']['complete_denominator'],
            'Diagnostics':len(m['cumulative']['diagnostics'])} for m in available])
else:
    table([{'Chỉ số cần bổ sung': 'Source/corpus thành công và paper đủ mọi version', 'Nguồn cần đọc': 'Discovery, checkpoint download/extract và tệp thực tế'},
           {'Chỉ số cần bổ sung': 'Kích thước trung bình trước và sau lọc', 'Nguồn cần đọc': 'Cùng tập paper/version có đủ sidecar trích xuất'},
           {'Chỉ số cần bổ sung': 'References, trung bình và tỷ lệ metadata đầy đủ', 'Nguồn cần đọc': 'Checkpoint và tệp references hiện hành từng paper'}])'''),
    ('md', '''Kích thước trước/sau lọc cần cặp đo trên cùng tập paper. References rỗng hợp lệ được tính vào mẫu số trung bình; lỗi API và chưa được index được báo riêng. Công cụ xuất thống kê tích lũy được liên kết ở [phụ lục](audit-appendix.ipynb), không yêu cầu crawl lại 5.000 ID.

## Chất lượng dữ liệu

Tỷ lệ dưới đây dùng số paper đã được kiểm định làm mẫu số, không gồm lookup chưa phát hiện được paper. Kết quả phản ánh ngày audit được nộp.'''),
    ('code', '''quality = quality_rows(members)
table(quality)
verified = [r for r in quality if r['Paper đã kiểm định'] is not None]
fig, ax = plt.subplots(figsize=(8,4))
ax.bar([r['Thành viên'] for r in verified], [r['Đạt'] for r in verified], label='Đạt kiểm định')
ax.bar([r['Thành viên'] for r in verified], [r['Còn lỗi'] for r in verified],
       bottom=[r['Đạt'] for r in verified],label='Còn lỗi')
ax.set_ylabel('Paper đã kiểm định');ax.legend();plt.tight_layout();plt.show()'''),
    ('md', '''Các paper chưa đạt có thể vướng một version, một stage hoặc quy tắc kiểm tra. Cần xem nguyên nhân cụ thể trước khi quyết định tải lại. Audit TV2 có cờ hoàn tất mâu thuẫn với số fail; số đếm gốc được giữ ở phụ lục để xác minh tiếp.

### Nhóm vấn đề được validator ghi nhận

Mỗi paper chỉ đếm một lần trong từng nhóm; một paper có thể thuộc nhiều nhóm. Các cột không cộng thành tổng paper fail. Đây là phân loại thông báo kiểm định, chưa khẳng định nguyên nhân gốc hoặc trách nhiệm người chạy.'''),
    ('code', 'table(error_groups(members))'),
    ('md', '''## Phạm vi kết luận

Bằng chứng hiện có xác nhận đủ record đầu vào ở TV2–TV5, đồng thời cho biết các lỗi lookup và validation còn mở trong những snapshot này. Chưa có audit TV1 và thống kê tích lũy đầy đủ của năm thành viên. Vì vậy chưa công bố số source hợp lệ, trung bình kích thước/references hoặc tỷ lệ thành công cuối cùng cho toàn bộ nhóm.'''),
    ])

    notebook('performance.ipynb', [
    ('md', '''# Hiệu năng pipeline

Các số đo dưới đây thuộc những phiên resume đã nộp. Phạm vi giữa các phiên khác nhau; trạng thái cache, retry và thời gian chờ mạng cũng khác. Bảng không được dùng để xếp hạng tốc độ giữa thành viên hoặc thay benchmark fresh toàn assignment.

## Các phiên được ghi nhận

Mỗi run ID chỉ được tính một lần, kể cả khi cùng run xuất hiện trong ZIP cũ và ZIP đã sửa. Audit được chạy sau phiên benchmark không thay đổi phạm vi hoặc trạng thái kết thúc của phiên ấy.'''),
    ('code', setup),
    ('code', '''table([{'Phiên': s['session'], 'Phạm vi': run_range(s['benchmark']),
        'Wall time (giây)': s['benchmark']['wall_seconds'],
        'Trạng thái': 'Bị ngắt' if s['benchmark']['exit_code']==130 else ('Exit 0' if s['benchmark']['exit_code']==0 else 'Có lỗi'),
        'Số mẫu RAM': s['benchmark']['sample_count']} for s in sessions])'''),
    ('md', '''## Thời gian xử lý

Tổng wall time các phiên đã nộp bao gồm chi phí xử lý lại ID trong chính những phiên đó. Đếm trùng cùng một run ID sẽ làm sai tổng, còn việc một ID được chạy lại ở hai phiên là chi phí thực tế. Lịch sử hiện có chưa đầy đủ, nên tổng này không phải thời gian hoàn thành toàn bộ assignment. Thời gian nghỉ/ngắt máy cũng không nằm trong tổng wall time hoạt động.

Các mốc bắt đầu/kết thúc bao quanh phép đo có thể khác trường wall time; cần làm rõ biên đo và overhead trước benchmark tổng cuối cùng.'''),
    ('code', '''table([{'Thành viên': member, 'Số phiên có tệp': len(subset),
        'Tổng wall time đã nộp (giây)': sum(s['benchmark']['wall_seconds'] for s in subset)}
       for member in sorted({s['member'] for s in sessions})
       for subset in [[s for s in sessions if s['member']==member]]])
timings = []
for s in sessions:
    events=[json.loads(line) for line in (s['directory']/'timings.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    disc=[e for e in events if e['kind']=='discovery']; paper=[e for e in events if e['kind']=='paper']
    timings.append({'Phiên': s['session'], 'Discovery (tổng giây event)': sum(e['elapsed_seconds'] for e in disc) if disc else None,
        'Paper event hoàn tất': len(paper),
        'Giây/paper event': sum(e['elapsed_seconds'] for e in paper)/len(paper) if paper else None,
        'Event dùng cache': sum(e.get('cached') is True for e in events)})
table(timings)'''),
    ('md', '''Paper event có thể bao gồm thời gian các stage, nên không cộng tất cả loại event thành runtime. Event đang dở khi ngắt có thể chưa được ghi. Trung bình của event trong một lượt resume chưa phải thời gian trung bình xử lý mới một paper.

## RAM và dung lượng output

RAM là tổng RSS quan sát trên cây tiến trình. Phiên không có khoảng lấy mẫu không đủ cơ sở diễn giải peak/mean đại diện. Disk đo toàn bộ output tại mốc tương ứng, có thể gồm dữ liệu tích lũy từ các phiên trước. Final disk không phải riêng kích thước corpus TeX/BibTeX.'''),
    ('code', '''rows=[]
for s in sessions:
    b=s['benchmark'];r=b['ram'];d=b['disk'];usable=b['sample_count']>=2 and r['observed_seconds']>0
    rows.append({'Phiên':s['session'], 'Peak RSS (MiB)':r['peak_rss_bytes']/1024**2 if usable else 'Không đủ mẫu',
        'Mean RSS (MiB)':r['time_weighted_mean_rss_bytes']/1024**2 if usable and r['time_weighted_mean_rss_bytes'] is not None else 'Không đủ mẫu',
        'Peak output (GiB)':d['peak_observed_bytes']/1024**3 if d.get('peak_observed_bytes') is not None else None,
        'Final output (GiB)':d['final_bytes']/1024**3 if d.get('final_bytes') is not None else None})
table(rows)
chosen=next(s for s in sessions if s['member']=='TV3')
samples=[json.loads(line) for line in (chosen['directory']/'samples.jsonl').read_text().splitlines() if line.strip()]
if len(samples)>1:
    fig,ax=plt.subplots(figsize=(8,4));ax.plot([v['elapsed_seconds']/60 for v in samples],[v['rss_bytes']/1024**2 for v in samples])
    ax.set_xlabel('Thời gian lấy mẫu (phút)');ax.set_ylabel('Tổng RSS (MiB)');ax.set_title('RAM trong phiên resume TV3 ngày 03/11')
    plt.tight_layout();plt.show()'''),
    ('md', '''Biểu đồ mô tả một phiên có mẫu, chưa đại diện toàn bộ lịch sử thu thập. Không thể khôi phục runtime/RAM bị thiếu từ corpus cuối. Đỉnh ngắn có thể bị bỏ lỡ, shared pages có thể bị đếm nhiều lần khi cộng RSS, và quét file trên Drive có overhead.'''),
    ])

    notebook('audit-appendix.ipynb', [
    ('md', '''# Phụ lục: Bằng chứng và tái lập

## Nguồn kết quả

TV3 và TV4 đã bổ sung audit ngày 04/11; bộ ZIP sửa được nhập vào snapshot `updated-20261106`. Audit TV4 được chọn từ bản có thời điểm tạo mới nhất trong hai ZIP được gửi. Cả hai bản đều ghi 5.000 record, 0 unseen/unresolved, 4.882 pass và 118 fail. Bản TV2/TV5 và mọi snapshot cũ được giữ nguyên.

Ngày cập nhật báo cáo là 06/11/2026; ngày kiểm tra thực tế nằm trong từng audit. Kiểm hash artifacts khi build bảo đảm đúng tệp đã lưu, chưa thay việc tái kiểm corpus sống. ZIP TV5 vẫn là bản cục bộ cùng tên/kích thước bản chia sẻ, chưa đối chiếu hash cloud.

Thông tin nhóm đã chạy 5.000 ID/người được nhóm cung cấp; số kiểm chứng trong bảng lấy từ audit. Thư mục nguồn: [arxiv_ms1_data](https://drive.google.com/drive/folders/123TUmjXMX38gKRLnJIKDl2yZF8jK6e9n).'''),
    ('code', setup),
    ('code', '''for s in sessions:
    p=s['provenance']
    display(Markdown('**'+s['session']+'**: ['+p['archive_name']+']('+p['drive_url']+')'))
    display(Markdown('SHA-256 ZIP: `'+p['archive_sha256']+'`'))
table([{'Thành viên':m['member'],'Audit tạo lúc (UTC)':m['audit']['generated_at'] if m['audit'] else None,
        'Nguồn':m['provenance']['drive_url'] if m['provenance'] else None} for m in members])
table([{'Phiên':s['session'],'Run ID':s['benchmark']['run_id'],'Bắt đầu (UTC)':s['benchmark']['started_at'],
        'Kết thúc (UTC)':s['benchmark']['finished_at'],'Source commit':s['benchmark']['environment'].get('source_commit'),
        'CPU logic':s['benchmark']['environment'].get('logical_cpu_count'),
        'CPU-only ghi nhận':s['benchmark']['environment'].get('cpu_only_confirmation')} for s in sessions])'''),
    ('md', '''## Đối chiếu audit

Ở các commit source mà benchmark khai báo, cờ hoàn tất audit yêu cầu không còn ID chưa thấy, Discovery chưa giải quyết, validation fail và diagnostics. Vì vậy `audit_complete=false` của TV3/TV4 đến từ validation, trong khi cả hai đã có đủ record và lookup được giải quyết.

Phạm vi TV3/TV4/TV5 được đối chiếu với input đi cùng bản audit trùng nội dung; TV2 liệt kê đủ 5.000 định danh đúng dải. Trường `discovered_assigned_ids` đếm ID có record, kể cả record lỗi. Số Discovery thành công được đọc riêng từ bảng trạng thái.

Audit TV2 ghi `audit_complete=true` cùng 2.579 paper fail, chưa phù hợp công thức source được khai báo. Cần xác minh code audit thực dùng và độ mới của validation. TV5 còn bốn Discovery lỗi: 2410.04689, 2410.04690, 2410.05043, 2410.05044.'''),
    ('code','table(coverage_rows(members))'),
    ('md', '''## Xuất thống kê corpus tích lũy

Notebook [MS1_Cumulative_Statistics.ipynb](https://colab.research.google.com/github/HoangLongNha/arxiv-project-report/blob/main/colab/MS1_Cumulative_Statistics.ipynb) đọc dữ liệu đang có trên Drive. Dừng các tiến trình ghi trước khi chạy, chọn đúng thành viên và đường dẫn `data/`. Notebook chỉ xuất một tệp JSON mới ở ngoài corpus; không gọi API thu thập và không sửa checkpoint/corpus.

Công cụ đọc mọi checkpoint Discovery trên dải được giao, đối chiếu stage/tệp và tránh đếm lặp paper/version qua nhiều phiên. References được đọc một lần mỗi paper. Trước/sau lọc chỉ tính trên những paper có đủ sidecar; số paper tạo mẫu số được ghi trong kết quả. Validation được đọc từ báo cáo đã có, không được coi là một lượt revalidate mới.

Kết quả `cumulative-statistics.json` cần được gửi lại cho TV5 để đối chiếu/import. Không đổi run ID của statistics resume thành toàn dải và không ghi đè manifest để ép tạo thống kê. Khi đủ tệp của năm thành viên mới tổng hợp số liệu toàn nhóm.

## Vai trò từng tệp

| Tệp | Phạm vi |
|---|---|
| assignment-audit.json | Coverage và validation trên dải audit |
| inputs.json | Dải dự định kiểm tra, chưa phải kết quả thực thi |
| statistics.json | Các paper được manifest của lượt chạy chọn |
| cumulative-statistics.json | Toàn dải từ checkpoint và dữ liệu tích lũy, có phạm vi riêng |
| benchmark/samples/timings | Thời gian và tài nguyên của một phiên |
| provenance.json | Nguồn ZIP và hash gốc/bản công bố |

README hướng dẫn cài môi trường, export và build. Notebook báo cáo vẫn thực thi khi build; code tính toán được ẩn khỏi HTML. Tài liệu bàn giao gốc nằm ở [Đóng góp thành viên](member-contributions.md).'''),
    ])
