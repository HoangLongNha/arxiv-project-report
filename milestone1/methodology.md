# Phương pháp triển khai

## Pipeline

Danh sách ID → discovery → download từng version → extract từng version → metadata → references → validate. TV1 điều phối/discovery; TV2 download; TV3 extract; TV4 metadata/references; TV5 QA, đo đạc và báo cáo.

Discovery dùng API arXiv trả Atom XML, đọc latest version và truy vấn các version trước để có đủ v1…vn. ID sai, không tồn tại, lỗi API và lỗi dữ liệu có trạng thái riêng. Pacing và retry có thể chiếm phần lớn wall time; chúng được tính vào runtime thực tế.

Downloader dùng requests session, endpoint `export.arxiv.org/src/<ID>vN`, stream theo chunk, SHA-256 và tệp tạm trước atomic rename. Phân biệt PDF-only, HTTP/network lỗi và source thành công. Retry/backoff giảm tác động lỗi tạm thời nhưng không bảo đảm không gặp 429. Cache nội bộ có thể được tái sử dụng ngay cả khi orchestrator chạy lại; fresh benchmark cần output mới.

Extractor nhận đường dẫn từ download artifact, xử lý tar/gzip/plain TeX, kiểm tra đường dẫn khi giải nén, giữ `.tex`/`.bib`. Sidecar `extract_metadata.json` lưu kích thước trước/sau lọc. Vì có fallback plain text và heuristic định dạng, kết quả success của module vẫn phải được QA; validator không phải trình biên dịch LaTeX.

Metadata được chuẩn hóa từ discovery mà không gọi mạng thêm. References từ Semantic Scholar, giữ reference thiếu arXiv ID trong dữ liệu nội bộ, kèm `missing_fields` và provenance. Lỗi API, chưa được index và không có references được tách riêng.

## Validator

Validator đọc checkpoint đã ghi của từng stage, không đọc manifest đang chờ tổng hợp ở cuối pipeline. Nó kiểm tra version liên tục, metadata khớp discovery, file/đường dẫn/artifact, checksum nếu có, dấu hiệu corpus rỗng/binary, schema và định danh references. File trùng nội dung được cảnh báo vì có thể hợp lệ giữa version. Không sửa corpus.

`validate=success` nghĩa dữ liệu và trạng thái nhất quán, có thể bao gồm PDF-only; không được dùng thay source success rate.

## Định nghĩa thống kê

Mỗi tỷ lệ lưu cả tử số, mẫu số, giá trị. Không có mẫu số → null. Paper được đếm theo ID duy nhất trong manifest lượt chạy đã hoàn tất; không đếm lẫn corpus cache ngoài manifest.

| Chỉ số | Tử số / mẫu số |
|---|---|
| Discovery success | Paper discovery thành công / paper đầu vào duy nhất |
| Download success | Version download success / version đã biết từ discovery thành công |
| Extract success | Version extract success / version đã biết |
| Version record coverage | Version có checkpoint download đúng identity / version đã biết |
| Source-complete paper | Paper có mọi version download/extract success / paper đầu vào duy nhất |
| Validation pass | Paper có report valid / paper discovery thành công |
| Reference query success | Paper có JSON references đọc được ở success/no_data / paper discovery thành công |
| Reference nonempty success | Paper success có JSON references / paper discovery thành công |
| Reference metadata completeness | Reference đủ ID/title/authors/date/S2 ID / tổng reference đọc được |

Version count của discovery lỗi là **chưa biết**, không tự đặt bằng 0 cho tỷ lệ version coverage toàn bộ assignment. Trung bình số references chỉ tính paper truy vấn được (gồm no_data=0), không gán not_indexed bằng 0. Kích thước trước/sau lọc lấy cùng tập paper có đủ số đo đã giải nén trên mọi version; kích thước package nén báo riêng.

## Đo hiệu năng

Wrapper chạy pipeline ở tiến trình riêng; observer dùng `time.perf_counter()` ghi thời gian discovery, stage và paper, kể cả cached flag. Wall time bao gồm toàn pipeline, startup/import, retries, chờ mạng, QA và ghi dữ liệu, không gồm cài môi trường. Chỉ event hoàn tất mới có timing; nếu ngắt, paper đang dở chưa có full duration.

psutil lấy mẫu tổng RSS của pipeline và tiến trình con. Mean dùng giá trị giữ từ mẫu trước và trọng số thời gian. Shared pages có thể bị đếm nhiều lần; tiến trình ngắn hơn chu kỳ lấy mẫu có thể không được thấy. Disk đo logical bytes của output gồm staging, sidecars, state và logs, loại trừ thư mục results của sampler. Peak RAM/disk là cực đại **quan sát được**, không phải cực đại tức thời bảo đảm.

Lượt nghiệm thu cuối phải trên Colab CPU-only. Notebook lưu versions, commit/dirty flag, môi trường và số đo thô; không ghi giá trị API key. Source dirty phải được chốt commit hoặc lưu diff nội bộ để tái lập. Theo [đề chính thức](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/crawling/), báo cáo dùng số đo kiểm chứng được và bảng/biểu đồ phát sinh khi biên dịch book.
