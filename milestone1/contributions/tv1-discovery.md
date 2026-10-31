# BÁO CÁO MILESTONE 1 — THÀNH VIÊN 1 (TV1)
## PHẦN: THIẾT KẾ KIẾN TRÚC, DISCOVERY ARXIV VÀ ĐIỀU PHỐI PIPELINE

> **Lưu ý nguồn tư liệu:** Tư liệu do TV1 cung cấp. Các nhận định về trạng thái hoàn thành module là ảnh chụp tại thời điểm viết báo cáo TV1; không được dùng để suy ra trạng thái toàn bộ pipeline ở ngày nghiệm thu.

> **Mục đích báo cáo:** Trình bày phần việc TV1 thực hiện trong Milestone 1 của dự án `arxiv-data-science`. Báo cáo tập trung vào kiến trúc repository, hợp đồng dữ liệu dùng chung, cơ chế Discovery toàn bộ phiên bản arXiv, CLI, checkpoint/resume, điều phối các stage và kiểm thử được xây dựng. Những nội dung chưa có bằng chứng chạy thực tế được ghi rõ là thiết kế hoặc test đã được viết, không xem là kết quả benchmark đã đo.

---

## 1. MỤC TIÊU VÀ PHẠM VI CÔNG VIỆC

### 1.1. Vai trò của TV1
TV1 phụ trách phần nền tảng để các thành viên có thể phát triển module độc lập nhưng tích hợp được vào cùng một pipeline. Phạm vi gồm:
- Khởi tạo cấu trúc repository cho cả ba milestone.
- Định nghĩa schema và hợp đồng giao tiếp giữa các stage.
- Xây dựng module Discovery để chuẩn hóa ID, truy vấn arXiv API và tìm danh sách phiên bản của mỗi bài báo.
- Xây dựng CLI để nhận danh sách ID, file đầu vào hoặc khoảng ID.
- Điều phối các stage của Milestone 1, lưu checkpoint và hỗ trợ chạy tiếp sau gián đoạn.
- Viết bộ kiểm thử offline cho Discovery, CLI, resume và tích hợp adapter giả lập.
- Viết README hướng dẫn cài đặt, cách chạy và quy ước phối hợp nhóm.
### 1.2. Phạm vi đã triển khai và giới hạn

| Hạng mục                                                                         | Trạng thái                                                   |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Cấu trúc repository và package Python                                            | Đã tạo                                                       |
| Schema dùng chung `DiscoveryRecord`, `VersionRecord`, `StageResult`, `ErrorInfo` | Đã định nghĩa                                                |
| Discovery và phân loại lỗi                                                       | Đã triển khai                                                |
| CLI và mở rộng input ID                                                          | Đã triển khai                                                |
| Checkpoint, manifest, summary, resume                                            | Đã triển khai trong orchestrator                             |
| Hợp đồng tích hợp TV2–TV5                                                        | Đã ghi trong `docs/CONTRACTS.md`                             |
| Downloader, extractor, metadata, references, validation                          | Mới có integration slot; chờ module của thành viên phụ trách |
| Parsing (Milestone 2), matching (Milestone 3), Parquet export                    | Mới có khung, chưa triển khai chức năng                      |

---
## 2. KIẾN TRÚC REPOSITORY VÀ HỢP ĐỒNG DỮ LIỆU

### 2.1. Cấu trúc project

Repository được tổ chức theo package `src/arxiv_pipeline/`, tách phần dùng chung, crawling, parsing, matching, export và điều phối pipeline.

```text
arxiv-data-science/
├── docs/
│   └── CONTRACTS.md
├── scripts/
│   └── run_pipeline.py
├── src/arxiv_pipeline/
│   ├── common/
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── schemas.py
│   │   └── utils.py
│   ├── crawling/
│   │   ├── discovery.py
│   │   ├── downloader.py
│   │   ├── extractor.py
│   │   ├── metadata.py
│   │   └── references.py
│   ├── parsing/
│   ├── matching/
│   ├── export/
│   ├── pipeline/
│   ├── main.py
│   └── __main__.py
├── tests/
│   ├── crawling/
│   └── pipeline/
├── main.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

Các module ở `parsing/`, `matching/` và một số module downstream hiện là khung tích hợp. Việc có sẵn vị trí file giúp thống nhất giao diện và cấu trúc trước khi các thành viên bàn giao implementation; không có nghĩa các chức năng đó đã chạy hoàn chỉnh.
### 2.2. Nguyên tắc hợp đồng dữ liệu
`docs/CONTRACTS.md` và `common/schemas.py` định nghĩa hợp đồng phiên bản `1.0`. Các đường dẫn artifact được lưu tương đối với output root để dữ liệu có thể được di chuyển cùng thư mục output.
Các kiểu dữ liệu chính:
- **`DiscoveryRecord`**: ghi lại ID đầu vào, arXiv ID chuẩn hóa, version được yêu cầu (nếu có), trạng thái, metadata, danh sách phiên bản, lỗi, số lần request và phiên bản schema.
- **`VersionRecord`**: mô tả từng phiên bản, gồm số version, ID có version, URL source, đường dẫn source/corpus, ngày nộp và ngày cập nhật.
- **`StageResult`**: chuẩn hóa kết quả của một stage gồm tên stage, paper ID, version, status, timestamp, artifacts, error, attempts và size.
- **`ErrorInfo`**: mô tả loại lỗi, thông báo, khả năng retry và HTTP status nếu có.
Trạng thái Discovery gồm `success`, `invalid_id`, `not_found`, `api_error`, `data_error`. Trạng thái stage gồm `success`, `no_source`, `not_indexed`, `no_data`, `api_error`, `data_error`, `error`, `not_implemented`, `skipped`.
Việc phân biệt các trạng thái này quan trọng khi thống kê: bài không có source, bài không được index hoặc thiếu dữ liệu không nên bị gộp chung với lỗi mạng; đồng thời cũng không nên tính các trường hợp này là tải source thành công.
### 2.3. Đường đi dữ liệu tổng quát
```text
Danh sách ID / file / khoảng ID
              │
              ▼
     Chuẩn hóa và kiểm tra ID
              │
              ▼
       Discovery qua arXiv API
              │
              ├── invalid_id
              ├── not_found
              ├── api_error
              ├── data_error
              └── success
                     │
                     ▼
        Danh sách version v1 ... vn
                     │
          (khi chạy stage crawl)
                     ▼
             TV2: download
                     │
                     ▼
             TV3: extract
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    TV4: metadata        TV4: references
          │                     │
          └──────────┬──────────┘
                     ▼
             TV5: validation
                     │
                     ▼
         manifests + summary + logs
```

Sơ đồ thể hiện thứ tự điều phối được thiết kế trong orchestrator. Các module downstream cần được thành viên phụ trách triển khai và bàn giao trước khi full crawl có thể hoàn tất thành công.

---
## 3. DISCOVERY: NGUYÊN LÝ HOẠT ĐỘNG VÀ XỬ LÝ LỖI
### 3.1. Chuẩn hóa ID đầu vào
Hàm `normalize_id()` trong `common/utils.py` được sử dụng để chuẩn hóa ID trước khi gọi API. Theo các trường hợp được kiểm thử, đầu vào có thể là:
- ID arXiv dạng mới, ví dụ `2301.00001`.
- ID có version, ví dụ `2301.00001v2`.
- ID dạng cũ, ví dụ `hep-th/9901001v3`.
- Tiền tố `arXiv:`.
- URL trang abstract hoặc PDF của arXiv.
Hàm chuẩn hóa trả về cặp `(base_id, requested_version)`. ID không hợp lệ được chuyển thành trạng thái `invalid_id` và không gọi mạng. Việc chuẩn hóa trước khi truy vấn giúp giảm request không cần thiết và bảo vệ đường dẫn lưu trữ khỏi ID không hợp lệ.
### 3.2. Truy vấn arXiv API và lấy toàn bộ phiên bản
Module `crawling/discovery.py` sử dụng `urllib.request` của Python standard library để gọi endpoint API được cấu hình trong `APIConfig`. Mỗi request truy vấn một ID và yêu cầu tối đa một kết quả.
Quy trình Discovery:
1. Chuẩn hóa ID đầu vào.
2. Truy vấn thông tin phiên bản mới nhất của bài báo.
3. Nếu phản hồi hợp lệ không có entry, trả về `not_found`.
4. Xác định số version mới nhất $v_n$. 
5. Nếu người dùng yêu cầu version lớn hơn version mới nhất, trả về `not_found` với loại lỗi `version_not_found`.
6. Lấy metadata cho các version từ `v1` đến `vn`; version mới nhất được tái sử dụng từ request đầu tiên.
7. Xác minh ID và version trong từng phản hồi khớp với request.
8. Tạo `VersionRecord` cho từng version và trả về `success` nếu quá trình hoàn tất.
Ngay cả khi đầu vào có version cụ thể, Discovery vẫn tìm toàn bộ lịch sử version của paper. Điều này giúp dữ liệu downstream có thể phân biệt từng phiên bản thay vì chỉ lưu trạng thái mới nhất.
### 3.3. Metadata được thu thập
Metadata ở cấp paper được tạo từ entry mới nhất, bao gồm các trường thể hiện trong code:
- `arxiv_id`
- `title`
- `authors`
- `submission_date`
- `latest_version`
- `revised_dates`
- `source`
- `retrieved_at`
- `abstract`
- `categories`
- `venue`
- `doi`
Mỗi `VersionRecord` lưu riêng `version`, `versioned_id`, `source_url`, `source_path`, `corpus_path`, `submission_date` và `updated_date`. Ngày nộp được lấy từ version đầu tiên; các ngày cập nhật của version sau được ghi vào `revised_dates`.
Các trường này là metadata phục vụ những stage tải source, trích xuất corpus và phân tích sau này. Discovery không tải gói LaTeX; nhiệm vụ tải source thuộc stage downloader.
### 3.4. Phân loại lỗi

| Trạng thái   | Ý nghĩa                                                                                   |
| ------------ | ----------------------------------------------------------------------------------------- |
| `invalid_id` | ID không đúng định dạng hoặc không hợp lệ; không gọi API                                  |
| `not_found`  | API trả về Atom feed hợp lệ nhưng không có entry, hoặc version được yêu cầu không tồn tại |
| `api_error`  | HTTP, lỗi mạng, timeout hoặc phản hồi API báo lỗi                                         |
| `data_error` | XML sai định dạng, thiếu metadata bắt buộc, sai ID/version hoặc thiếu version trung gian  |
| `success`    | Tìm thấy và xác minh được danh sách version cùng metadata cần thiết                       |
Phân loại lỗi riêng giúp quá trình chạy batch tiếp tục xử lý các ID khác thay vì dừng ở lỗi của một paper. Số lần request thực tế của từng record được lưu trong trường `attempts`.
### 3.5. Rate limiting, timeout và retry
`ArxivClient` sử dụng các tham số cấu hình:

| Tham số                       | Giá trị mặc định thể hiện trong CLI |
| ----------------------------- | ----------------------------------: |
| Timeout mỗi request           |                             30 giây |
| Số lần retry bổ sung          |                                   3 |
| Khoảng cách request tối thiểu |                              3 giây |
Client duy trì thời điểm request gần nhất và chờ đủ khoảng cách cấu hình trước khi gửi request tiếp theo. Các HTTP status `408`, `429` và nhóm `5xx` được xem là có thể retry. Lỗi mạng/timeout cũng được retry; lỗi HTTP không thuộc nhóm retryable sẽ dừng retry.
Thời gian chờ retry lấy giá trị lớn hơn giữa `Retry-After` (nếu có) và exponential backoff dựa trên `delay * 2**retry`. Cách làm này giúp tránh gửi request dồn dập khi server yêu cầu giảm tốc độ. Các giá trị timeout, retry âm hoặc delay dưới mức tối thiểu bị từ chối khi kiểm tra cấu hình.
### 3.6. Kiểm tra tính hợp lệ của Atom response
Parser sử dụng `xml.etree.ElementTree` và namespace Atom/arXiv để đọc phản hồi. Các kiểm tra chính gồm:
- XML phải parse được và root phải là Atom feed.
- Feed phải có tối đa một entry cho truy vấn một ID.
- Entry không được là phản hồi lỗi API.
- ID và version trả về phải khớp với paper/version đang truy vấn.
- Title, author, published date và updated date phải có giá trị.
- Ngày phải parse được và có timezone.
Nếu dữ liệu không đáp ứng các điều kiện này, Discovery trả về `data_error` thay vì tạo một record thành công nhưng thiếu thông tin.
---
## 4. CLI, CHECKPOINT VÀ KHẢ NĂNG CHẠY LẠI
### 4.1. Các nguồn nhập ID
CLI trong `main.py` hỗ trợ ba cách nhập:
- `--ids`: nhập một hoặc nhiều ID; chấp nhận các ID ngăn cách bằng dấu phẩy.
- `--input`: đọc file UTF-8, mỗi dòng một ID; dòng trống và phần comment bắt đầu bằng `#` được bỏ qua.
- `--range START:END`: mở rộng một khoảng ID bao gồm cả hai đầu mút, trong cùng một tháng và giới hạn tối đa 10.000 ID.
Các ID trùng lặp được loại bỏ trong orchestrator theo thứ tự xuất hiện. CLI yêu cầu output root và hỗ trợ hai chế độ: `discovery` (mặc định) và `crawl`.
Ví dụ chạy Discovery:
```bash
python main.py --ids 2301.00001 2301.00002 --output data --stage discovery
```
Ví dụ đọc file và chạy tiếp từ checkpoint:
```bash
python main.py --input ids.txt --output data --stage discovery --resume
```
Ví dụ yêu cầu full crawl:
```bash
python main.py --input ids.txt --output data --stage crawl --resume
```
### 4.2. Resume và force
- `--resume`: dùng lại checkpoint Discovery nếu record có schema hợp lệ, status `success` và danh sách version đầy đủ; input lỗi hoặc checkpoint không hợp lệ sẽ được truy vấn lại.
- `--force`: làm mới Discovery và chạy lại các adapter cho những input được chọn.
- Hai tùy chọn này loại trừ lẫn nhau.
Ở stage downstream, kết quả terminal như `success`, `no_source`, `not_indexed`, `no_data` có thể được tái sử dụng khi checkpoint hợp lệ và artifact tương ứng còn tồn tại. Kết quả lỗi hoặc module chưa triển khai được thử lại. Nếu artifact thành công bị thiếu, stage đó cần chạy lại.
Checkpoint được ghi sau từng input/stage, nhằm giữ lại tiến độ đã hoàn thành khi tiến trình bị ngắt. Manifest và summary được ghi lại sau vòng chạy. Thiết kế hiện tại không dành cho nhiều process cùng ghi một output root; chỉ nên có một CLI process sử dụng output root tại một thời điểm.
### 4.3. Cấu trúc output
```text
<output>/
├── manifests/
│   ├── discovery.json
│   └── stages.json
├── summary.json
├── state/
│   ├── discovery/
│   └── stages/
├── logs/
│   └── pipeline.log
├── raw/
├── corpus/
├── metadata/
├── references/
└── validation/
```
- `state/discovery/`: checkpoint từng ID đầu vào, tên file dựa trên SHA-256 của chuỗi ID.
- `state/stages/`: checkpoint của từng stage, paper và version.
- `manifests/discovery.json`: snapshot các kết quả Discovery của lần chạy.
- `manifests/stages.json`: snapshot kết quả các stage được yêu cầu.
- `summary.json`: số input, paper, version, phân bố status và cờ `complete`.
- `logs/pipeline.log`: log vận hành.
- `raw/`, `corpus/`, `metadata/`, `references/`, `validation/`: vị trí artifact theo hợp đồng tích hợp.
Các đường dẫn artifact do adapter trả về phải nằm trong output root; orchestrator kiểm tra đường dẫn không thoát khỏi thư mục output và yêu cầu artifact tồn tại.
### 4.4. Cách hiểu `summary.complete` và exit code
`summary.complete` biểu thị các bước được yêu cầu đã kết thúc hợp lệ theo quy tắc trạng thái của pipeline; không có nghĩa mọi paper đều có source LaTeX. Các outcome như `no_source`, `not_indexed` và `no_data` được phân biệt riêng.
CLI trả về:
- `0`: các bước yêu cầu hoàn tất hợp lệ.
- `1`: có input/stage lỗi, stage chưa được bàn giao hoặc lỗi I/O.
- `2`: tham số hoặc cấu hình CLI không hợp lệ.
- `130`: tiến trình bị người dùng ngắt.
Khi chạy `--stage crawl`, các adapter downstream chưa triển khai sẽ trả về `not_implemented` hoặc stage phụ thuộc sẽ là `skipped`. Pipeline không tuyên bố full crawl thành công khi module còn thiếu.
---
## 5. KIỂM THỬ VÀ ĐÁNH GIÁ
### 5.1. Các nhóm kiểm thử được viết
Hai patch bổ sung test cho Discovery và CLI. Các nhóm kiểm thử thể hiện trong mã gồm:

| Nhóm              | Nội dung kiểm tra                                                            |
| ----------------- | ---------------------------------------------------------------------------- |
| Chuẩn hóa ID      | ID hiện đại, ID cũ, version, URL; từ chối ID sai                             |
| Discovery version | Lấy mọi version, ngày cập nhật, version được yêu cầu nhưng không tồn tại     |
| Kiểm tra dữ liệu  | XML lỗi, thiếu entry/metadata, sai ID, sai version, thiếu version trung gian |
| HTTP/retry        | `429` và `Retry-After`, `500`, lỗi mạng, incomplete read, số lần thử         |
| Rate limiting     | Chờ trước request kế tiếp theo cấu hình                                      |
| CLI input         | Kết hợp file, ID trực tiếp, range, loại trùng và summary                     |
| Resume/force      | Tái sử dụng checkpoint, thử lại lỗi, checkpoint hỏng, tiếp tục sau gián đoạn |
| Orchestrator      | Adapter giả lập, xác minh artifact, stage phụ thuộc và kết quả `no_source`   |
Các fixture sử dụng Atom response tổng hợp để test có tính xác định và không phụ thuộc Internet. Vì vậy, test fixture không chứng minh rằng arXiv API đang khả dụng hoặc metadata của các bài báo thật đã được xác minh.
### 5.2. Lệnh kiểm thử
README hướng dẫn chạy test offline bằng:
```bash
python -m unittest discover -s tests -v
```
Hai patch cho thấy test đã được bổ sung vào repository, nhưng bản thân patch không cung cấp log thực thi test trong môi trường cuối cùng. Do đó báo cáo không khẳng định toàn bộ test đã pass nếu chưa chạy lệnh trên và lưu lại kết quả thực tế.
## 6. HƯỚNG DẪN CHẠY VÀ TÍCH HỢP
### 6.1. Môi trường
Project khai báo Python `>=3.10` và runtime TV1 sử dụng Python standard library. Cài package ở chế độ editable theo README:
```bash
python -m venv .venv
python -m pip install -r requirements.txt
```
Trên Windows PowerShell, có thể kích hoạt môi trường bằng:
```powershell
.venv\Scripts\Activate.ps1
```
Có thể gọi `python main.py` từ checkout mà không cần cài package trước, do entry point thêm thư mục `src` vào đường dẫn import.
### 6.2. Hợp đồng dành cho các thành viên

| Thành viên/stage             | Input chính                    | Output theo hợp đồng                                              |
| ---------------------------- | ------------------------------ | ----------------------------------------------------------------- |
| TV1 — Discovery/orchestrator | ID đầu vào                     | `DiscoveryRecord`, danh sách `VersionRecord`, checkpoint/manifest |
| TV2 — Download               | Paper và version từ Discovery  | Source artifact và kết quả download                               |
| TV3 — Extract                | Kết quả download               | Corpus theo từng version                                          |
| TV4 — Metadata               | Paper                          | Metadata đã chuẩn hóa                                             |
| TV4 — References             | Paper                          | Danh sách references và provenance                                |
| TV5 — Validation/export      | Các checkpoint/artifact đã ghi | Validation report; Parquet thuộc phần export                      |
Tên hàm tích hợp downstream trong skeleton là `run(record, output_dir, *, version=None, upstream=None)` và phải trả về `StageResult`. Trường `artifacts` dùng đường dẫn tương đối với output root. Các thành viên cần tuân thủ schema/status và quy ước đường dẫn trong `docs/CONTRACTS.md`, không tự ý thay đổi tên trường hoặc diễn giải sai ID của nguồn dữ liệu.
### 6.3. Quy trình phối hợp nhóm
README đề xuất tạo issue có người phụ trách, input/output và tiêu chí nghiệm thu; phát triển trên nhánh tính năng; mở PR có hướng dẫn test và reviewer; tránh commit trực tiếp vào `main`. Khi một module được bàn giao, nhóm cần kiểm tra hợp đồng, chạy unit test của module và kiểm tra tích hợp với orchestrator.

---
## 7. KẾT LUẬN 
### 7.1. Kết quả TV1
TV1 đã xây dựng nền tảng ban đầu cho dự án: cấu trúc package cho MS1–MS3, hợp đồng dữ liệu v1, Discovery toàn bộ version arXiv, CLI, cơ chế retry/rate limiting, checkpoint/resume, manifest/summary và bộ test offline. Các thành phần này giúp nhóm có một giao diện thống nhất để tích hợp module của các thành viên.