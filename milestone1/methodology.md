# Phương pháp triển khai

> **Cơ sở biên tập:** Các mục TV1–TV4 dưới đây được tổng hợp từ bốn tài liệu do thành viên gửi cho TV5, không phải nội dung tự tạo trước đó. Mô tả và số liệu do từng thành viên báo cáo cần được đối chiếu mã nguồn, commit, log và artifact trước khi nộp. Phần TV5 dựa trên code và phương pháp QA/benchmark đã chuẩn bị trong dự án.

## Tổng quan pipeline Milestone 1

Dữ liệu bắt đầu từ danh sách arXiv ID được phân công. TV1 chuẩn hóa ID, tra cứu arXiv API để xác định các phiên bản `v1...vn`, sau đó điều phối các stage trên cơ sở hợp đồng `StageResult`. TV2 tải source riêng cho mỗi phiên bản; TV3 giải nén và lọc thành corpus chỉ còn `.tex`/`.bib`. TV4 chuẩn hóa metadata từ Discovery và lấy references từ Semantic Scholar; TV5 kiểm định đầu ra, đo tài nguyên và sinh báo cáo có thể tái lập.

```text
arXiv ID list / range
        |
        v
TV1 Discovery + Orchestrator
        |
        +----> TV2 Download per version ----> TV3 Extract per version
        |
        +----> TV4 Metadata (reuse Discovery data)
        |
        +----> TV4 References (Semantic Scholar; optional batch prefetch)
        |
        v
TV5 Validation -> statistics / benchmark -> Jupyter Book
```

Không đồng nhất các trạng thái `no_source`, `no_data`, `not_indexed`, `api_error` và `data_error`. Một paper có phiên bản chỉ chứa PDF được ghi nhận hợp lệ theo trạng thái, nhưng không được tính thành công ở tiêu chí tải mã nguồn LaTeX.

## TV1 — Thiết kế hệ thống, Discovery và Orchestrator

Theo [tài liệu TV1](contributions/tv1-discovery.md), code được tổ chức trong package `src/arxiv_pipeline/` với bốn schema chung: `DiscoveryRecord`, `VersionRecord`, `StageResult` và `ErrorInfo`; các artifact lưu bằng đường dẫn tương đối với output root. Module `crawling/discovery.py` chuẩn hóa ID dạng mới/cũ, ID có version và URL, gọi API trả Atom XML, tìm version mới nhất và xác minh từng version từ `v1` đến `vn`.

Discovery phân biệt `invalid_id`, `not_found`, `api_error`, `data_error`, `success`; kiểm tra XML, ID/version trả về, metadata và ngày tháng. Client sử dụng timeout, giới hạn tần suất request và retry với backoff, có xét `Retry-After` cho lỗi tạm thời. CLI nhận `--ids`, `--input`, `--range`, hỗ trợ `--resume`/`--force`. Checkpoint được ghi theo ID/stage để tránh mất toàn bộ tiến độ sau gián đoạn; manifest và summary mô tả snapshot của lượt chạy. Không suy ra pipeline toàn nhóm đã hoàn thiện chỉ từ trạng thái riêng của TV1.

## TV2 — Tải mã nguồn LaTeX theo phiên bản

Theo [tư liệu kỹ thuật TV2](contributions/tv2-downloader.md), Downloader dùng `requests.Session()` và HTTP streaming để tải từ endpoint source theo arXiv ID/version. Mã nguồn được ghi theo chunk vào file tạm `.part`, tính SHA-256 trong lúc tải và đổi tên bằng `os.replace` sau khi hoàn tất. Thiết kế này tránh coi file bị tải dở là artifact hoàn chỉnh.

Downloader áp dụng giãn cách request, retry/backoff, kiểm tra PDF-only/`no_source`, xử lý HTTP và lỗi mạng. File nguồn và sidecar `download_metadata.json` được lưu theo paper/version để TV3 truy xuất và để TV5 kiểm định. Tài liệu TV2 có một số con số ước lượng về RAM, tiết kiệm thời gian và băng thông; chúng **không được xem là kết quả đo** trong chương thống kê hoặc kết luận nếu chưa có log benchmark tương ứng.

## TV3 — Giải nén, lọc và tạo corpus sạch

Theo [báo cáo TV3](contributions/tv3-extractor.md), module `crawling/extractor.py` hỗ trợ các nguồn `tar.gz`, `tar`, `.gz` và plain TeX. Mọi archive member được kiểm tra đường dẫn trước khi giải nén nhằm ngăn path traversal. Bộ lọc giữ `.tex` và `.bib`, xóa file ảnh/nhị phân/phụ trợ và giữ nguyên nội dung LaTeX, kể cả lệnh `\includegraphics`.

Kết quả được lưu trong `corpus/<paper_key>/vN/`, dùng vùng staging trước khi chuyển vào đích để hạn chế dữ liệu dở dang. Sidecar `extract_metadata.json` cung cấp danh sách file, số lượng và kích thước trước/sau lọc. TV3 báo cáo 11 ca unit test và một kiểm thử tích hợp trên fixture; đây là bằng chứng ở phạm vi module, không phải tỷ lệ thành công trên toàn bộ arXiv ID được giao.

## TV4 — Metadata theo phiên bản và References từ Semantic Scholar

Theo [báo cáo TV4](contributions/tv4-metadata-references.md), stage `metadata` sử dụng lại DiscoveryRecord, không cần request arXiv lần hai. Metadata cấp paper lấy theo quy ước phiên bản mới nhất; từng version giữ `title`, `authors`, `venue` để không mất thông tin thay đổi xuyên phiên bản. Bản ghi thiếu trường tùy chọn được đánh dấu thay vì suy đoán dữ liệu.

Stage `references` đọc Semantic Scholar qua `S2Source`, chuẩn hóa theo schema chung và sử dụng `POST /paper/batch` để giảm số request; khi response lớn gặp HTTP 400, client có thể chia batch; khi danh sách reference bị cắt ngắn, chuyển sang endpoint phân trang. Dữ liệu được khử trùng lặp theo định danh Semantic Scholar hoặc arXiv khi có, ghi `missing_fields`, giữ references thiếu arXiv ID và tách `success`, `no_data`, `not_indexed`, `api_error`. Cơ chế checkpoint cho phép batch prefetch và pipeline dùng chung kết quả khi resume.

TV4 cung cấp kết quả của **một lượt chạy riêng 5.000 ID** cho stage references, gồm 4.717 `success`, 266 `no_data`, 17 `not_indexed`, không có `api_error` cuối lượt, thu được 203.066 references sau loại trùng. Đây là số liệu do TV4 báo cáo, chưa phải thống kê hoặc benchmark end-to-end của toàn assignment; chi tiết và điều kiện chạy xem trang TV4.

## TV5 — Kiểm định chất lượng dữ liệu

Validator đọc checkpoint đã ghi của từng stage và đối chiếu Discovery, metadata, reference records, raw source và corpus của từng version. Các kiểm tra gồm tính liên tục của version, định danh và schema, sự tồn tại/giới hạn đường dẫn artifact, hash dữ liệu nếu có, dấu hiệu corpus rỗng/binary và dữ liệu reference trùng hoặc thiếu. File nguồn trùng nội dung giữa các version được xử lý theo quy tắc cảnh báo, vì bản thân sự trùng nhau chưa chắc là lỗi.

`validate=success` cho biết dữ liệu phù hợp các quy tắc QA đã kiểm tra, không đồng nghĩa toàn bộ các version đều có source LaTeX. Validator không thay thế trình biên dịch LaTeX hay kiểm định ngữ nghĩa nội dung bài báo.

## Thống kê và benchmark có thể tái lập

Các chỉ số được tính từ dữ liệu của đúng **một run có phạm vi xác định** và luôn gắn với tử số, mẫu số, trạng thái và thời điểm thu thập. Một số tỷ lệ chính:

| Chỉ số | Định nghĩa |
|---|---|
| Discovery success | Số paper Discovery thành công / số paper input duy nhất |
| Download success | Số paper-version download success / số version đã xác định từ Discovery thành công |
| Extract success | Số paper-version extract success / số version đã xác định |
| Version record coverage | Số version có checkpoint download đúng identity / số version đã biết |
| Source-complete paper | Số paper có tất cả version download/extract success / số paper input duy nhất |
| Validation pass | Số paper hợp lệ theo QA / số paper Discovery thành công |
| Reference query success | Số paper có JSON references đọc được ở trạng thái success/no_data / số paper Discovery thành công |
| Reference nonempty success | Số paper có kết quả reference `success` và danh sách không rỗng / số paper Discovery thành công |
| Reference completeness | Số reference đủ các trường yêu cầu / tổng số reference đã đọc |

Khi chưa có mẫu số thì giá trị tỷ lệ để `null`, không tự thay bằng 0%. Paper không được Semantic Scholar index không bị tính như paper có danh sách tài liệu tham khảo rỗng. Dung lượng corpus trước/sau lọc phải đo trên cùng tập paper/version có dữ liệu tương ứng.

Version count của Discovery lỗi là **chưa biết**, không tự đặt bằng 0 để tính version coverage toàn assignment. Trung bình số references chỉ tính các paper truy vấn được (gồm `no_data=0`), không gán `not_indexed` bằng 0. Kích thước package nén được báo riêng với kích thước corpus đã giải nén; không dùng hai đại lượng này để suy ra tỷ lệ loại bỏ hình ảnh.

Benchmark sử dụng `time.perf_counter()` để ghi thời gian tổng và theo stage/paper. Trình đo tài nguyên chạy song song với tiến trình pipeline, dùng `psutil` lấy mẫu tổng RSS của tiến trình và con, đồng thời quét dung lượng output. Peak RAM/disk là cực đại **quan sát được theo chu kỳ lấy mẫu**, không phải đỉnh tuyệt đối bảo đảm. Report lưu môi trường, mã commit, nhãn run và raw samples/timings để kiểm chứng. **Số đo nghiệm thu toàn corpus cần chạy trên Google Colab CPU-only;** số liệu demo/smoke/đo stage riêng không thay thế kết quả này.

Wall time bao gồm startup/import, retry, thời gian chờ mạng, QA và ghi dữ liệu, không gồm cài môi trường. Observer chỉ ghi timing đầy đủ cho các event đã hoàn tất và lưu cờ cached; fresh benchmark cần output mới, không suy từ một lượt resume. Sau gián đoạn, paper đang dở chưa có full duration.

Mean RSS được tính theo trọng số thời gian, dùng giá trị của mẫu trước cho khoảng thời gian kế tiếp. Shared pages có thể được đếm nhiều lần khi cộng RSS tiến trình; tiến trình hoặc đỉnh tài nguyên ngắn hơn chu kỳ lấy mẫu có thể bị bỏ lỡ. Disk đo logical bytes của output, gồm staging, sidecars, state và logs, loại thư mục results của sampler. Việc quét disk có overhead và không đo hệ điều hành hay cache pip.

Các notebook `statistics.ipynb` và `performance.ipynb` đọc JSON của cùng run được chọn, dùng `pandas`/`matplotlib` để tạo bảng và biểu đồ tại thời điểm Jupyter Book build, không dán ảnh tĩnh.

## Nguồn đóng góp kỹ thuật của thành viên

- [TV1 — Discovery, kiến trúc và điều phối pipeline](contributions/tv1-discovery.md)
- [TV2 — Source Downloader và Raw Storage](contributions/tv2-downloader.md)
- [TV3 — File Processing và Corpus Builder](contributions/tv3-extractor.md)
- [TV4 — Metadata và References](contributions/tv4-metadata-references.md)

Các trang thành viên giữ chi tiết kỹ thuật từ tài liệu được bàn giao. Riêng mọi tuyên bố hiệu năng cần kiểm tra provenance và log trước khi hợp nhất vào kết luận nghiệm thu.
