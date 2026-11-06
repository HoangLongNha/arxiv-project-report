"""Generate the reader-facing MS1 report. All notebook inputs are hidden in HTML."""
from pathlib import Path
import nbformat as nb

ROOT = Path(__file__).resolve().parents[1]

SETUP = '''from pathlib import Path
import sys, json
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, HTML
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / '_config.yml').exists())
sys.path.insert(0, str(ROOT / 'utils'))
from preliminary_results import (load_members, progress_rows, assignment_outcomes,
    quality_rows, error_groups, performance_rows, run_range, session_members, coverage_rows)
members = load_members(ROOT)
sessions = session_members(ROOT, members)
def table(rows):
    frame = pd.DataFrame(rows, dtype=object)
    frame = frame.where(frame.notna(), 'Chưa đủ bằng chứng')
    def number(value):
        if isinstance(value, float):
            return f'{value:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')
        if isinstance(value, int) and not isinstance(value, bool):
            return f'{value:,}'.replace(',', '.')
        return str(value)
    display(HTML(frame.map(number).to_html(index=False, escape=True, border=0, classes='dataframe')))
'''


def notebook(name, content):
    cells = []
    for kind, text in content:
        cell = nb.v4.new_markdown_cell(text) if kind == 'md' else nb.v4.new_code_cell(text)
        if kind != 'md':
            cell.metadata['tags'] = ['remove-input']
        import hashlib
        cell.id = hashlib.sha256((kind + text).encode()).hexdigest()[:12]
        cells.append(cell)
    doc = nb.v4.new_notebook(cells=cells)
    doc.metadata['kernelspec'] = dict(display_name='Python 3', language='python', name='python3')
    doc.metadata['language_info'] = dict(name='python', version='3.12')
    nb.write(doc, ROOT / 'milestone1' / name)


PAGES = {
'intro.md': '''# arXiv Project — Nhóm 6

Báo cáo trình bày quá trình xây dựng corpus bài báo khoa học từ arXiv, gồm source LaTeX theo phiên bản, metadata và tài liệu tham khảo từ Semantic Scholar. Corpus này là đầu vào cho các bước parsing và matching ở các milestone tiếp theo.

## Milestone 1: Thu thập dữ liệu

Nhóm được giao **25.000 arXiv ID**, chia thành năm dải, mỗi thành viên chạy **5.000 ID**. Theo tổng hợp tiến độ do nhóm cung cấp, các thành viên đã chạy hết phạm vi cá nhân. Báo cáo tách tiến độ này khỏi kết quả thu thập thành công và chất lượng dữ liệu; các chỉ số thực nghiệm chỉ công bố trong phạm vi artifacts đã đối chiếu.

```{note}
Kết quả được cập nhật ngày **04/11/2026**. Bản hiện tại trình bày kết quả sơ bộ: tiến độ nhóm báo cáo và mức kiểm chứng từ dữ liệu thực nghiệm được phân biệt rõ. Chưa công bố tỷ lệ thành công cuối cùng của toàn bộ 25.000 ID.
```

Nội dung gồm mục tiêu và dữ liệu, phương pháp, thiết lập thực nghiệm, kết quả thu thập và chất lượng, hiệu năng, thảo luận và đóng góp thành viên. Mã nguồn, cấu hình chi tiết và nguồn artifacts được liên kết riêng để hỗ trợ tái lập.

- [Đọc báo cáo Milestone 1](milestone1/index.md)
- [Repository mã nguồn](https://github.com/LeoTkiet/arxiv-data-science)
- [Repository báo cáo](https://github.com/HoangLongNha/arxiv-project-report)
- [Đề bài chính thức](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/)
''',
'milestone1/index.md': '''# Milestone 1 — Thu thập dữ liệu arXiv

Milestone 1 xây dựng và kiểm tra corpus từ các ID được phân công. Hệ thống xác định toàn bộ phiên bản, tải source, giữ các tệp TeX/BibTeX, chuẩn hóa metadata và thu thập references.

Báo cáo đi từ **phạm vi đầu vào → phương pháp → thực nghiệm → kết quả → phân tích**. Phần kết quả trả lời lần lượt: mỗi thành viên đã chạy đến đâu, thu được gì và dữ liệu có đạt yêu cầu hay không. Hiệu năng được trình bày ở một mục riêng, gắn với phạm vi thực sự được đo.

Các bảng và biểu đồ được sinh từ artifacts khi biên dịch Jupyter Book. Chi tiết đối chiếu audit, định danh phiên chạy và nguồn dữ liệu được đặt trong phụ lục; phần nội dung chính tập trung vào ý nghĩa của kết quả.
''',
'milestone1/introduction.md': '''# Giới thiệu và phạm vi dữ liệu

## Mục tiêu

Nhóm xây dựng corpus để phục vụ phân tích cấu trúc bài báo và đối chiếu tài liệu tham khảo. Với mỗi paper tồn tại, hệ thống tìm toàn bộ lịch sử phiên bản, tải từng source và giữ nguyên nội dung các tệp `.tex`/`.bib`. Tệp hình bị loại khỏi corpus; các lệnh LaTeX định nghĩa hình vẫn được giữ để không phá cấu trúc tài liệu.

## Phân công dữ liệu

| Thành viên chạy dữ liệu | Dải arXiv ID | Số ID được giao |
|---|---|---:|
| TV1 | 2508.12872–2508.17871 | 5.000 |
| TV2 | 2506.15788–2506.20787 | 5.000 |
| TV3 | 2411.08799–2411.13798 | 5.000 |
| TV4 | 2410.18025–2410.23024 | 5.000 |
| TV5 | 2410.03025–2410.08024 | 5.000 |
| **Toàn nhóm** | **Năm dải không giao nhau** | **25.000** |

Nguồn phân công là workbook đăng ký nhóm, sheet Teams. Mỗi thành viên chạy pipeline tích hợp trên dải cá nhân; điều này khác với vai trò phát triển module của thành viên đó.

## Đơn vị thống kê

- **ID đầu vào:** một định danh cần tra cứu, có thể không tồn tại hoặc gặp lỗi tạm thời.
- **Paper:** một bài báo được phát hiện thành công từ ID.
- **Version:** một phiên bản của paper; một paper có thể có nhiều version.
- **Reference:** một mục tài liệu tham khảo mà Semantic Scholar trả về cho paper.

Vì vậy, chạy 5.000 ID không đồng nghĩa thu được 5.000 paper hoặc 5.000 source. ID không tồn tại là một kết quả lookup đã giải quyết, còn lỗi API có thể cần thử lại.

## Đầu ra và phạm vi nộp

Dữ liệu làm việc gồm source thô, corpus TeX/BibTeX, metadata, references và checkpoint. Source/corpus được tách theo paper và version; metadata và references được liên kết theo paper. Dữ liệu được nhóm giữ để dùng cho MS2–MS3, không đưa corpus vào repository mã nguồn.

Hai bảng dữ liệu được chuẩn bị cho lần nộp cuối là bảng paper (định danh, tiêu đề, tác giả, ngày nộp/cập nhật, venue) và bảng references (paper trích dẫn, định danh arXiv của reference và metadata đi kèm). References chưa có arXiv ID vẫn được giữ trong dữ liệu làm việc, nhưng không trở thành dòng của bảng references cuối nếu chưa đáp ứng khóa định danh.
''',
'milestone1/methodology.md': '''# Phương pháp thu thập và xử lý

## Tổng quan hệ thống

Pipeline tích hợp sáu bước: **Discovery → Download → Extract → Metadata/References → Validation → Thống kê và báo cáo**. Metadata sử dụng lại thông tin Discovery; References được lấy từ Semantic Scholar. Checkpoint lưu kết quả từng bước để hỗ trợ chạy tiếp sau gián đoạn.

| Bước | Phương pháp | Đầu ra chính |
|---|---|---|
| Discovery | Chuẩn hóa ID, đọc arXiv Atom API, xác định và kiểm tra các version | Danh sách phiên bản và metadata ban đầu |
| Download | Tải source riêng từng version qua streaming, ghi tạm rồi hoàn tất nguyên tử | Source thô và thông tin tải |
| Extract | Kiểm tra đường dẫn archive, chỉ giữ TeX/BibTeX, không sửa nội dung | Corpus theo paper/version |
| Metadata | Chuẩn hóa dữ liệu Discovery và giữ thông tin riêng từng version | Metadata liên kết theo paper |
| References | Truy vấn Semantic Scholar, phân trang/batch khi phù hợp, chuẩn hóa và loại trùng | References và nguồn truy xuất |
| Validation | Đối chiếu định danh, version, checkpoint, đường dẫn và tệp dữ liệu | Kết quả kiểm định từng paper |

## Discovery và tải source

Hệ thống chấp nhận ID hoặc khoảng ID, chuẩn hóa định danh trước khi truy vấn. Discovery phân biệt ID không hợp lệ, không tìm thấy, lỗi API, lỗi dữ liệu và thành công. Phiên bản mới nhất cho biết số version cần kiểm tra; từng version được xác minh và tải qua endpoint source có hậu tố phiên bản.

Downloader sử dụng HTTP streaming để hạn chế bộ đệm, tính SHA-256 trong lúc tải, ghi vào tệp tạm và chỉ công nhận đầu ra sau khi tải hoàn tất. Phiên bản PDF-only hoặc không có source được ghi nhận riêng. Timeout, pacing và retry/backoff giúp xử lý lỗi mạng và giới hạn tần suất; HTTP 429 được xem là tín hiệu cần giảm tốc hoặc chờ thử lại.

## Tạo corpus và chuẩn hóa metadata

Extractor xử lý các dạng source được hỗ trợ như tar/gzip và TeX thuần. Đường dẫn thành viên archive được kiểm tra để tránh ghi ra ngoài thư mục đích. Chỉ các tệp `.tex` và `.bib` được đưa vào corpus. Việc loại hình không chỉnh sửa các lệnh trong nội dung LaTeX.

Metadata sử dụng lại Discovery để tránh truy vấn arXiv trùng lặp. Thông tin cấp paper và thông tin từng version được phân biệt; các trường tùy chọn thiếu được đánh dấu thay vì suy đoán giá trị.

## Thu thập references

Semantic Scholar cung cấp định danh và metadata tài liệu tham khảo. Client hỗ trợ batch, retry và phân trang để xử lý giới hạn API và danh sách dài. References được loại trùng theo định danh khi có; mục thiếu arXiv ID vẫn được giữ trong dữ liệu làm việc. Không có references, chưa được index và lỗi API là những kết quả khác nhau.

Một thí nghiệm references riêng được TV4 mô tả trong tài liệu bàn giao sử dụng dải tháng 08/2025. Đó là thí nghiệm của module, không phải kết quả assignment tháng 10/2024 của người chạy TV4, và không được cộng vào thống kê toàn nhóm ở phần kết quả này.

## Kiểm định và khả năng chạy tiếp

Validator đối chiếu số version, schema/định danh, đường dẫn tệp, raw source, corpus, metadata và references với checkpoint từng bước. Nó phát hiện dữ liệu thiếu, trạng thái không nhất quán và những tệp bị báo rỗng/nhị phân; một số nội dung trùng giữa các version chỉ là cảnh báo.

Chạy tiếp sử dụng checkpoint để tái dùng kết quả đã có. Vì vậy một lượt cuối chỉ xử lý vài ID không có nghĩa corpus cá nhân chỉ chứa vài paper. Ngược lại, exit code thành công của lượt cuối cũng không chứng minh toàn bộ corpus đã hợp lệ. Tiến độ lookup, kết quả thu thập và validation được đánh giá riêng.

## Công cụ chính

Python được dùng cho pipeline; arXiv API/Atom XML cho Discovery; `requests` và HTTP streaming cho tải nguồn; `tarfile`/`gzip` cho giải nén; Semantic Scholar API cho references; `psutil` và bộ đếm thời gian cho benchmark; pandas, matplotlib và Jupyter Book cho báo cáo. Chi tiết cài đặt và lệnh chạy nằm trong README của hai repository.
''',
'milestone1/experimental-setup.md': '''# Thiết lập thực nghiệm và cách đánh giá

## Thiết kế thực nghiệm

Mỗi thành viên chạy cùng pipeline tích hợp trên dải 5.000 ID cá nhân. Theo thông tin nhóm cung cấp, các thành viên đã chạy hết dải và sử dụng notebook benchmark mới nhất. Tiến độ do nhóm xác nhận được trình bày riêng với mức kiểm chứng từ các tệp kết quả đã nộp.

Bộ bằng chứng hiện đọc được gồm ZIP của TV2, TV3, TV5, bản TV4 đã lưu và hai ZIP phiên TV4 bổ sung ngày 04/11/2026. Các phiên bổ sung có số đo hiệu năng nhưng chưa có thống kê snapshot hoàn tất. Ngày nộp ZIP không nhất thiết là ngày chạy; danh sách nguồn và thời điểm từng phiên được ghi ở phụ lục.

## Ba cấp đánh giá

| Cấp | Câu hỏi | Cách đánh giá |
|---|---|---|
| Tiến độ đầu vào | Đã chạy qua hết 5.000 ID chưa? | Đối chiếu dải, số ID có record, số chưa ghi nhận và lookup còn lỗi |
| Kết quả thu thập | Thu được bao nhiêu paper/version/source/references? | Thống kê dữ liệu trên phạm vi cụ thể, phân biệt thành công, không có source và lỗi |
| Chất lượng | Đầu ra có phù hợp quy tắc kiểm định không? | Số paper đã kiểm định, pass/fail, nhóm lỗi và cảnh báo |

Một ID có record lỗi đã được thử xử lý nhưng chưa có kết quả lookup được giải quyết. Validation fail không làm mất việc ID đã được thử xử lý. Cờ hoàn tất audit trong source còn xét validation/diagnostics, nên không dùng riêng cờ đó để kết luận tiến độ chạy ID.

## Chỉ số và mẫu số

| Chỉ số | Mẫu số/phạm vi |
|---|---|
| Bao phủ đầu vào | Số ID có record / số ID được giao, trên đúng dải |
| Discovery thành công | Số paper phát hiện được / số ID đầu vào của phạm vi xét |
| Tải source thành công | Số version tải thành công / số version đã biết |
| Validation pass | Số paper đạt / số paper đã được kiểm định; báo riêng paper chưa kiểm định |
| Kích thước trước/sau lọc | Cùng tập paper có đủ cặp đo; cộng các version của từng paper |
| References trung bình | Các paper truy vấn được, gồm kết quả rỗng hợp lệ; không gán lỗi API bằng 0 |
| Tỷ lệ metadata references đầy đủ | Số reference đủ trường / tổng số reference đã đọc |

## Đo hiệu năng

Môi trường benchmark cuối theo đề bài là Google Colab CPU-only. Báo cáo giữ thông tin môi trường thực tế do từng run ghi nhận. Thời gian được đo cho pipeline và từng event; RAM được lấy mẫu trên cây tiến trình; disk là logical bytes trong output root, gồm dữ liệu/checkpoint và tệp tạm thuộc phạm vi đo.

Mỗi phép đo phải được đọc cùng phạm vi, chế độ chạy mới/chạy tiếp, dữ liệu cache, số mẫu và trạng thái kết thúc. Không cộng thời gian các run chồng lặp, không lấy số đo phiên resume cuối làm tổng thời gian nhiều phiên. RAM trung bình chỉ diễn giải khi có đủ khoảng lấy mẫu; đỉnh là cực đại quan sát được.

## Quy tắc tổng hợp

Chỉ cộng dữ liệu giữa những dải không giao nhau sau khi xác minh định danh và phạm vi. Audit toàn dải và statistics của một run ngắn là hai góc nhìn của cùng dữ liệu, không phải hai tập paper độc lập. Giá trị thiếu được ghi rõ là chưa đủ bằng chứng; tỷ lệ không có mẫu số được coi là không áp dụng. Các mẫu demo/smoke lịch sử không được cộng vào kết quả thu thập thật.
''',
'milestone1/discussion.md': '''# Thảo luận, hạn chế và kết luận

## Tiến độ và kết quả đạt được

Nhóm đã xây dựng pipeline tích hợp để tìm phiên bản, tải source, tạo corpus TeX/BibTeX, chuẩn hóa metadata, lấy references và kiểm định đầu ra. Theo tổng hợp tiến độ do nhóm cung cấp, năm thành viên đã chạy hết dải 5.000 ID/người. Phần kết quả ghi nhận tiến độ này và tách rõ số liệu đối chiếu được từ artifacts.

Trong bộ bằng chứng hiện có, audit TV2 và TV5 ghi nhận đủ 5.000 ID đúng dải. Điều này xác nhận việc xử lý đầu vào ở hai dải, đồng thời không bảo đảm tất cả lookup và đầu ra đều thành công. TV3/TV4 có thống kê của các lượt resume, nhưng chưa có kết quả audit toàn dải trong các ZIP đã đọc; chưa đủ cơ sở công bố chỉ số cuối cùng cho toàn bộ 25.000 ID.

## Chất lượng và nguyên nhân chưa đạt

Các lỗi kiểm định tập trung vào stage upstream chưa thành công, đường dẫn/tệp đầu ra và sự nhất quán của checkpoint. Các nhóm lỗi có thể cùng xuất hiện ở một paper. Cần phân biệt dữ liệu thực sự thiếu với checkpoint cũ hoặc quy tắc kiểm định chưa phù hợp; không thể kết luận toàn bộ paper validation fail đều không có dữ liệu sử dụng được.

Audit TV2 ghi cờ hoàn tất không khớp số paper fail theo công thức tại commit được benchmark khai báo. Đây là vấn đề cần tái kiểm ở báo cáo audit; không phủ nhận việc file đó liệt kê đủ 5.000 ID. TV5 vẫn có bốn lookup lỗi và các paper validation fail trong snapshot đã nộp. Các con số này mô tả trạng thái tại ngày audit, chưa khẳng định trạng thái của corpus sau những lần sửa/chạy tiếp chưa được xuất artifacts.

## Hiệu năng và giới hạn đo

Các run được nộp có phạm vi khác nhau và đều dùng chạy tiếp. Số đo chịu ảnh hưởng của cache, retry, thời gian chờ dịch vụ và quét file trên Drive. Những yếu tố này giải thích vì sao không dùng bảng benchmark hiện tại để xếp hạng tốc độ giữa thành viên hoặc ngoại suy tổng thời gian toàn nhóm. Các phiên TV4 bổ sung có nhiều mẫu hơn nhưng bị gián đoạn và chồng lặp phạm vi, nên vẫn được trình bày riêng.

Lấy mẫu RAM có thể bỏ lỡ đỉnh ngắn; RSS cộng tiến trình có thể đếm shared pages nhiều lần. Disk chỉ đo trong output root và có thể chứa dữ liệu các phiên trước. Kích thước trước/sau lọc chỉ có ý nghĩa khi đo cùng tập dữ liệu đã giải nén; không suy tỷ lệ loại hình từ package nén.

## Mức sẵn sàng cho MS2

Corpus đã tạo là nền tảng cho parsing, nhưng cần rà soát source/corpus thiếu, version chưa hoàn tất và metadata liên kết trước khi chốt đầu vào MS2. Validator không biên dịch LaTeX và không kiểm chứng toàn bộ ngữ nghĩa; các trường hợp rỗng/nhị phân cần kiểm tra mẫu thực tế. References phụ thuộc độ phủ và giới hạn của Semantic Scholar; thiếu dữ liệu ở đây cần được giữ nhãn khi chuyển sang matching.

## Kết luận và phần cần hoàn thiện

Kết quả hiện tại xác nhận phương pháp thu thập, pipeline tích hợp và khả năng tạo báo cáo từ artifacts. Tiến độ 5.000 ID/người do nhóm cung cấp được ghi nhận; mức thu thập thành công và chất lượng được công bố đúng phạm vi có bằng chứng. Chưa kết luận toàn bộ dữ liệu MS1 đạt yêu cầu chỉ từ việc kết thúc notebook.

Để hoàn thiện nghiệm thu, nhóm cần bổ sung audit/thống kê toàn dải còn thiếu, xử lý hoặc giải thích các lỗi kiểm định, xác minh lại audit không nhất quán và hoàn thiện benchmark CPU-only với biên đo rõ ràng. Sau đó có thể cập nhật tỷ lệ thành công toàn nhóm và chốt snapshot đầu vào cho MS2.
''',
'milestone1/member-contributions.md': '''# Đóng góp thành viên

Nhóm phân chia trách nhiệm phát triển theo module, đồng thời mỗi thành viên chạy pipeline tích hợp trên dải 5.000 ID cá nhân. Hoàn thành module và hoàn thành thu thập/QA của assignment là hai loại kết quả được đánh giá riêng.

| Thành viên | Trách nhiệm phát triển | Sản phẩm chính |
|---|---|---|
| TV1 | Kiến trúc, Discovery và điều phối | Schema/hợp đồng chung, phân giải ID/version, CLI, checkpoint và resume |
| TV2 | Source downloader và raw storage | Tải theo version, streaming, hash, tệp tạm và xử lý lỗi tải |
| TV3 | Xử lý source và tạo corpus | Giải nén an toàn, lọc TeX/BibTeX, tổ chức corpus và sidecar |
| TV4 | Metadata và references | Chuẩn hóa metadata, Semantic Scholar client/batch, phân trang và loại trùng |
| TV5 | QA, thống kê, benchmark và báo cáo | Validator, audit assignment, đo tài nguyên, tổng hợp artifacts và Jupyter Book |

Các kiểm thử module kiểm tra những trường hợp như định danh sai, thiếu version, archive không an toàn, source không có TeX, lỗi API và checkpoint chạy tiếp. Kết quả kiểm thử phần mềm không được dùng thay tỷ lệ thành công thu thập dữ liệu thực tế.

''',
}


from submission_updates import PAGES as UPDATED_PAGES, build
PAGES.update(UPDATED_PAGES)
PAGES['milestone1/methodology.md'] = PAGES['milestone1/methodology.md'].replace(
    '## Tổng quan hệ thống', '## Tổng quan hệ thống\n\n![Luồng dữ liệu MS1](../_static/pipeline.svg)', 1)


def main():
    import runpy
    for name, text in PAGES.items():
        (ROOT / name).write_text(text.rstrip() + '\n', encoding='utf-8')
    build(notebook, SETUP)
    runpy.run_path(str(ROOT / 'scripts/prepare_cumulative_notebook.py'), run_name='__main__')


if __name__ == '__main__':
    main()
