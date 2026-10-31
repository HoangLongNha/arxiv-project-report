# BÁO CÁO MILESTONE 1 — THÀNH VIÊN 4 (TV4)
## PHẦN: CRAWL REFERENCES (SEMANTIC SCHOLAR) VÀ METADATA THEO TỪNG PHIÊN BẢN

> **Lưu ý nguồn tư liệu:** Số liệu 5.000 paper ở phần benchmark do TV4 cung cấp cho riêng stage `references`. Đó **không phải** số liệu end-to-end của toàn bộ 25.000 ID. Chưa có bằng chứng xác nhận môi trường Google Colab CPU-only trong tài liệu bàn giao, nên không dùng lượt này thay cho benchmark nghiệm thu trên Colab. Các số liệu dưới đây chờ đối chiếu log/artifact gốc.

> **Mục đích báo cáo:** Trình bày phần việc TV4 thực hiện trong Milestone 1 của dự án `arxiv-data-science`. Báo cáo mô tả cách nhóm xây dựng stage `references` (lấy danh sách tài liệu tham khảo từ Semantic Scholar) và stage `metadata` (chuẩn hóa metadata arXiv cho từng phiên bản), các vấn đề gặp phải và cách xử lý, cùng số liệu đo được từ một lần crawl thực tế 5.000 paper. Những gì chưa có bằng chứng chạy thực tế được ghi rõ là đã kiểm thử offline, không xem là kết quả benchmark.

---

## 1. MỤC TIÊU VÀ PHẠM VI CÔNG VIỆC

### 1.1. Vai trò của TV4
Theo hợp đồng trong `docs/CONTRACTS.md`, TV4 phụ trách hai stage cấp paper trong pipeline Milestone 1:
- **`references`**: với mỗi paper arXiv, lấy danh sách tài liệu tham khảo kèm tiêu đề, tác giả, ngày công bố và arXiv ID (nếu có) của từng tài liệu.
- **`metadata`**: chuẩn hóa metadata của paper (tiêu đề, tác giả, ngày nộp, ngày sửa đổi, venue…) và metadata riêng của từng phiên bản `v1 … vn`, ghi thành file theo schema chung.

Cả hai stage đều tích hợp vào orchestrator của TV1 qua hàm adapter `run(record, output_dir, *, version=None, upstream=None)` và trả về `StageResult`.

### 1.2. Phạm vi đã triển khai và giới hạn

| Hạng mục                                                           | Trạng thái                                              |
| ------------------------------------------------------------------ | ------------------------------------------------------- |
| Client Semantic Scholar (throttle, retry, chia batch, phân trang)  | Đã triển khai (`crawling/s2/s2_source.py`)              |
| Chuẩn hóa, loại trùng reference và ghi theo layout pipeline        | Đã triển khai (`crawling/s2/store.py`)                  |
| Adapter stage `references` cho orchestrator                         | Đã triển khai (`crawling/references.py`)                |
| Công cụ crawl theo batch, chạy tiếp được                            | Đã triển khai (`crawling/s2/batch.py`)                  |
| Stage `metadata` với metadata theo từng version                    | Đã triển khai (`crawling/metadata.py`)                  |
| Bổ sung `title`, `authors`, `venue` vào `VersionRecord` / Discovery | Đã triển khai, tương thích ngược với schema `1.0`       |
| Unit test offline                                                   | 43 test (25 references + 18 metadata)                   |
| Chạy thực tế stage `references`                                     | Đã chạy 5.000 paper (mục 6)                             |

---

## 2. KIẾN TRÚC MODULE

### 2.1. Cấu trúc file

```text
src/arxiv_pipeline/crawling/
├── references.py          # adapter stage `references` cho orchestrator
├── metadata.py            # stage `metadata` (không gọi mạng)
└── s2/
    ├── __init__.py
    ├── config.py          # hằng số: API key, khoảng cách request, retry, batch size, fields
    ├── s2_source.py       # client Semantic Scholar: S2Source.fetch(ids) -> Outcome
    ├── store.py           # Outcome -> file references + provenance + checkpoint
    └── batch.py           # CLI crawl theo batch 100 paper, chạy tiếp được
tests/crawling/
├── test_s2_references.py
└── test_metadata.py
```

### 2.2. Nguyên tắc thiết kế
Module references được chia thành ba lớp có trách nhiệm tách biệt:

1. **Nguồn dữ liệu (`S2Source`)**: chỉ có một hàm public `fetch(arxiv_ids)`, trả về lần lượt một `Outcome` cho mỗi ID. Toàn bộ chi tiết khó (giới hạn tốc độ, retry, tách batch khi lỗi 400, phân trang khi danh sách bị cắt, chuẩn hóa và loại trùng) được giấu bên trong.
2. **Lưu trữ (`store_outcome`)**: chuyển `Outcome` thành file đúng vị trí orchestrator đọc khi resume, và trả về `StageResult`.
3. **Hai cách gọi**: adapter `references.run()` (orchestrator gọi từng paper) và `batch.py` (gọi trực tiếp, 100 paper mỗi request). Cả hai dùng chung `S2Source` và `store_outcome`, nên kết quả ghi ra giống hệt nhau.

Nhờ cách chia này, công cụ batch có thể "điền trước" stage `references`, sau đó `main.py --stage crawl --resume` thấy checkpoint hợp lệ và bỏ qua, không gọi lại Semantic Scholar.

### 2.3. Đường đi dữ liệu

```text
arXiv ID (đã chuẩn hóa bởi Discovery / normalize_id)
        │
        ▼
S2Source.fetch()  ── POST /paper/batch (100 ID mỗi request)
        │               ├── HTTP 400 → chia đôi batch, gọi lại
        │               ├── 429 / 5xx / timeout → backoff, retry tối đa 6 lần
        │               └── 404 hoặc phần tử null → not_found
        │
        ├── số reference trả về < referenceCount
        │         └── GET /paper/arXiv:{id}/references (phân trang, 1000/trang)
        ▼
clean_refs(): chuẩn hóa + bỏ mục rỗng + loại trùng
        │
        ▼
store_outcome()
        ├── references/<paper_key>.json
        ├── references/<paper_key>.provenance.json
        ├── state/stages/references/<paper_key>/paper.json   (StageResult, dùng để resume)
        └── state/s2_progress.jsonl                           (log mỗi lần thử)
```

---

## 3. STAGE `references`: CÁC VẤN ĐỀ VÀ CÁCH XỬ LÝ

### 3.1. Chọn nguồn dữ liệu: Semantic Scholar thay vì tự parse bibliography
arXiv API không cung cấp danh sách tài liệu tham khảo. Hai lựa chọn là (a) tự trích từ file `.bbl`/`.bib` trong source LaTeX, hoặc (b) dùng Semantic Scholar Graph API. Nhóm chọn Semantic Scholar cho Milestone 1 vì:
- Trả về reference đã có cấu trúc (tiêu đề, tác giả, năm/ngày, `externalIds` gồm arXiv ID, DOI…), không phải xử lý nhiều định dạng BibTeX.
- Không phụ thuộc stage download/extract của TV2–TV3, nên stage `references` chạy được độc lập.
- Có endpoint batch, giảm mạnh số request.

Đổi lại, dữ liệu phụ thuộc vào việc Semantic Scholar có index paper hay không. Trường hợp này được tách thành trạng thái riêng (`not_indexed`), không gộp vào lỗi.

### 3.2. Giới hạn tốc độ của API
**Vấn đề.** Key Semantic Scholar cho phép khoảng 1 request/giây tính chung cho mọi endpoint; không có key thì dùng pool chung, rất dễ bị HTTP 429. Gọi từng paper một với 5.000 paper sẽ tốn hàng nghìn request.

**Cách xử lý.**
- **Gọi theo batch**: dùng `POST /paper/batch` với 100 ID mỗi request (API cho phép 500, nhóm chọn 100 để response nhẹ và ít bị lỗi 400). 5.000 paper chỉ cần khoảng 50 request chính.
- **Throttle toàn cục**: mọi request đều đi qua `_wait()`, đảm bảo khoảng cách tối thiểu tính từ lúc request trước *kết thúc*: 2 giây khi có key, 5 giây khi không có key (an toàn hơn mức 1 request/giây).
- **Throttle giữ qua các lần chạy**: thời điểm request cuối được ghi vào `state/s2_last_call`. Khi chạy lại ngay sau khi tiến trình trước dừng (hoặc chạy batch tool rồi chạy pipeline), client vẫn chờ đủ khoảng cách, tránh dồn request.
- **Dùng chung một client trong tiến trình**: adapter `references.py` giữ một `S2Source` cho mỗi output root, nên các lần orchestrator gọi từng paper vẫn chia sẻ cùng một bộ đếm throttle.
- **API key**: đọc từ biến môi trường `S2_API_KEY` hoặc file `.env` (đã gitignore, có `.env.example`). Biến đã export trong shell được ưu tiên. Log in 4 ký tự cuối của key để kiểm tra mà không lộ key.

### 3.3. Retry khi lỗi tạm thời

| Tình huống                         | Xử lý                                                                                          |
| ---------------------------------- | ---------------------------------------------------------------------------------------------- |
| HTTP 429, HTTP 5xx                 | Chờ theo `Retry-After` nếu có, ngược lại backoff `2^(attempt+1)` giây, tối đa 60 giây, cộng jitter ngẫu nhiên 0–1 giây |
| Timeout, lỗi kết nối               | Backoff như trên                                                                               |
| Hết 6 lần thử                       | Cả batch được đánh dấu `error`, không ghi file dữ liệu                                           |
| HTTP 404                            | `not_found` (paper không có trên Semantic Scholar)                                              |
| Mã lỗi khác                          | Dừng, báo lỗi                                                                                   |

Jitter giúp tránh trường hợp nhiều lần retry rơi đúng cùng một thời điểm. Sau mỗi 429, client bật chế độ "phạt" trong 50 request kế tiếp; với cấu hình hiện tại khoảng cách phạt (1,5 giây) không lớn hơn khoảng cách mặc định (2 giây) nên thực tế khoảng cách vẫn là 2 giây.

Ở cấp batch tool, sau lượt chạy đầu, những paper còn `error` được chạy lại tối đa 3 lượt, mỗi lượt chờ 120 giây trước. Paper vẫn lỗi sẽ được thử lại ở lần chạy sau vì `api_error` không phải trạng thái kết thúc.

### 3.4. Response quá lớn: tự chia nhỏ batch
**Vấn đề.** Endpoint batch có thể trả về HTTP 400 khi response quá lớn (ví dụ batch chứa nhiều paper có hàng trăm reference), hoặc khi trong batch có một ID gây lỗi.

**Cách xử lý.** `_batch_split()` chia đôi batch và gọi lại từng nửa, đệ quy cho tới khi còn 1 ID. Nếu ID đơn lẻ vẫn bị 400 thì chỉ ID đó bị đánh dấu `error`; các paper còn lại trong batch vẫn lấy được bình thường. Test `test_bad_request_splits_batch_down_to_the_bad_id` kiểm tra đúng hành vi này.

### 3.5. Danh sách reference bị cắt ngắn: chuyển sang endpoint phân trang
**Vấn đề.** Trong response batch, danh sách `references` có thể ít hơn `referenceCount` của paper (bị giới hạn số phần tử lồng nhau).

**Cách xử lý.** Nếu số reference nhận được nhỏ hơn `referenceCount`, client gọi `GET /paper/arXiv:{id}/references` với `limit=1000` và lặp theo `next` cho tới hết. Provenance ghi `paginated: true` để biết paper nào đi theo đường này. Nếu endpoint phân trang lỗi sau retry, paper được ghi `error` thay vì lưu danh sách thiếu. Trong lần chạy thật 5.000 paper có 13 paper đi theo nhánh này.

### 3.6. Chuẩn hóa và loại trùng reference
Mỗi reference từ Semantic Scholar được chuẩn hóa (`normalize_ref`) rồi làm sạch (`clean_refs`):
- **Ngày**: lấy `publicationDate` (`YYYY-MM-DD`); nếu không có thì dùng năm (`YYYY`).
- **Tác giả**: chỉ giữ tên, bỏ phần tử không có tên.
- **arXiv ID**: chỉ lấy từ trường `externalIds.ArXiv`. Nhóm **không** suy ra arXiv ID từ DOI (kể cả DOI dạng `10.48550/arXiv.…`) để tránh tạo dữ liệu không do nguồn cung cấp; có test riêng cho trường hợp này.
- **Bỏ mục rỗng**: reference không có S2 ID, tiêu đề lẫn external ID bị loại.
- **Loại trùng**: theo S2 paper ID; nếu không có S2 ID thì theo arXiv ID. Các mục chỉ có tiêu đề không bị gộp, vì tiêu đề giống nhau chưa chắc là cùng một tài liệu.

Mỗi dòng ghi ra theo hợp đồng:

```json
{
  "arxiv_id": "2508.12872",
  "ref_arxiv_id": null,
  "ref_title": "Bias and Ethics of AI Systems Applied in Auditing - A Systematic Review",
  "ref_authors": ["Wilberforce Murikah", "Jeff Kimanga Nthenge", "F. Musyoka"],
  "ref_submission_date": "2024-06-01",
  "ref_s2_id": "bd460d9cdcec7507df94aa65d3425a55e6c82b8d",
  "missing_fields": ["ref_arxiv_id"]
}
```

Giá trị thiếu là `null` (trường đơn) hoặc `[]` (danh sách) và tên trường được liệt kê trong `missing_fields`, giúp thống kê độ đầy đủ dữ liệu mà không phải đoán.

### 3.7. Phân loại trạng thái theo hợp đồng pipeline

| Kết quả từ Semantic Scholar           | Status pipeline | Ghi file dữ liệu | Kết thúc (không thử lại)? |
| ------------------------------------- | --------------- | ---------------- | ------------------------- |
| Có paper, có ≥ 1 reference             | `success`       | Có               | Có                        |
| Có paper nhưng không có reference       | `no_data`       | Có (mảng rỗng)   | Có                        |
| Không tìm thấy paper (404 / null)       | `not_indexed`   | Có (mảng rỗng)   | Có                        |
| Hết retry hoặc HTTP 400 ở mức 1 ID       | `api_error`     | Không            | Không, thử lại lần sau    |

Việc tách `no_data` và `not_indexed` khỏi `api_error` giúp khi thống kê không tính nhầm paper Semantic Scholar không biết là lỗi mạng, và ngược lại. Khi lỗi, `ErrorInfo` có loại `s2_unavailable`, `retryable=True`.

### 3.8. Resume và ghi file an toàn
- Mọi file JSON được ghi bằng `atomic_json` (ghi file tạm rồi đổi tên), nên tiến trình bị ngắt giữa chừng không để lại file hỏng.
- Checkpoint `state/stages/references/<paper_key>/paper.json` được ghi đúng vị trí orchestrator đọc. Hàm `is_done()` của batch tool dùng cùng quy tắc với orchestrator: đúng `schema_version`, đúng stage, đúng paper, status là trạng thái kết thúc, và mọi artifact tồn tại và nằm trong output root.
- `state/s2_progress.jsonl` ghi thêm một dòng mỗi lần thử (`arxiv_id`, `status`, `n_refs`, `paginated`, `seconds`); dòng cuối cùng của một ID là trạng thái hiện tại.
- Chạy lại cùng lệnh: paper đã xong được bỏ qua, chỉ paper lỗi được gọi lại. Không chạy batch tool và pipeline song song trên cùng một output root.

---

## 4. STAGE `metadata`: CÁC VẤN ĐỀ VÀ CÁCH XỬ LÝ

### 4.1. Không gọi mạng lần nữa
**Vấn đề.** Discovery (TV1) đã truy vấn arXiv API cho mọi version của paper. Nếu stage `metadata` gọi lại API thì gấp đôi số request vào arXiv (giới hạn 3 giây/request) mà không thêm thông tin.

**Cách xử lý.** Stage `metadata` dùng lại `DiscoveryRecord` mà orchestrator truyền vào, chỉ kiểm tra, chuẩn hóa và ghi ra `metadata/<paper_key>.json`. Stage này không phát sinh request nào.

### 4.2. Metadata có thể thay đổi giữa các version
**Vấn đề.** Tiêu đề, danh sách tác giả và `journal_ref` có thể khác nhau giữa `v1` và `vn`. Bản Discovery ban đầu chỉ lưu metadata cấp paper (lấy từ version mới nhất), nên mất thông tin của các version cũ.

**Cách xử lý.**
- Bổ sung ba trường `title`, `authors`, `venue` vào `VersionRecord` (`common/schemas.py`) và để Discovery điền chúng từ response của chính version đó.
- Ba trường có giá trị mặc định (`None`, `[]`), nên `schema_version` vẫn là `1.0` và checkpoint Discovery cũ vẫn đọc được. Với checkpoint cũ, stage `metadata` ghi các trường này là thiếu trong `missing_fields` của từng version, không báo lỗi.
- Cập nhật `docs/CONTRACTS.md` để mô tả các trường mới.

Kết quả: trường cấp paper lấy từ version mới nhất, `submission_date` lấy từ `v1`, `revised_dates` lấy ngày `updated` của `v2 … vn`, và mỗi phần tử `versions[]` giữ metadata riêng của version đó.

### 4.3. Kiểm tra tính nhất quán trước khi ghi
Hàm `build_metadata()` từ chối record và trả về `data_error` (không ghi file) nếu:
- Discovery không ở trạng thái `success`, hoặc thiếu `metadata`/`versions`.
- `metadata.arxiv_id` không khớp với record.
- Tiêu đề rỗng, hoặc danh sách tác giả rỗng/có tên rỗng.
- Danh sách version không đúng `1 … latest_version` (thiếu version giữa chừng), hoặc `versioned_id` không khớp `{arxiv_id}v{n}`.
- Số phần tử `revised_dates` khác `latest_version − 1`.
- Ngày không phải ISO 8601 hoặc không có timezone.
- Tiêu đề/tác giả cấp paper khác với version mới nhất.

Việc kiểm tra chặt giúp phát hiện lỗi ngay ở stage này thay vì để dữ liệu sai đi xuống Milestone 2–3.

### 4.4. Không suy đoán giá trị thiếu
- `venue` chỉ lấy từ `journal_ref` của arXiv; không có thì `null`, không suy ra từ nguồn khác.
- Các trường có thể thiếu hợp lệ (`venue`, `doi`, `abstract`, `categories`) nếu không có thì là `null`/`[]` và được liệt kê trong `missing_fields` cấp paper.
- Mỗi version có `missing_fields` riêng cho `title`, `authors`, `venue`.

---

## 5. HƯỚNG DẪN CHẠY

### 5.1. Cấu hình
Dependency thêm: `requests>=2.31`, `python-dotenv>=1.0` (khai báo trong `pyproject.toml`). Tạo file `.env` ở thư mục gốc theo `.env.example`:

```text
S2_API_KEY=your_semantic_scholar_key
```

Không có key vẫn chạy được nhưng chậm (5 giây/request) và dễ bị 429.

### 5.2. Chạy trong pipeline

```bash
python main.py --input ids.txt --output data --stage crawl --resume
```

Stage `references` khi chạy qua orchestrator gọi Semantic Scholar mỗi paper một request.

### 5.3. Chạy theo batch (khuyến nghị khi có nhiều paper)

```bash
python -m arxiv_pipeline.crawling.s2.batch --input ids.txt --output data
python main.py --input ids.txt --output data --stage crawl --resume
```

Lệnh đầu lấy references theo batch 100 paper và in tóm tắt `requested / skipped / ok / ok_empty / not_found / error`; exit code `1` nếu còn paper lỗi. Lệnh sau dùng lại kết quả nhờ `--resume`.

### 5.4. Cấu trúc output của TV4

```text
<output>/
├── references/
│   ├── <paper_key>.json              # mảng reference
│   └── <paper_key>.provenance.json   # source, retrieved_at, status, s2_paper_id, venue, reference_count, paginated
├── metadata/
│   └── <paper_key>.json              # metadata cấp paper + versions[]
└── state/
    ├── s2_last_call                  # thời điểm request S2 cuối (throttle giữa các lần chạy)
    ├── s2_progress.jsonl             # log mỗi lần thử
    └── stages/references/<paper_key>/paper.json
```

ID dạng cũ như `hep-th/9901001` dùng khóa thư mục `hep-th_9901001`.

---

## 6. BENCHMARK: CRAWL REFERENCES 5.000 PAPER

### 6.1. Điều kiện chạy
- **Ngày chạy:** 25/10/2026, dùng batch tool có API key (khoảng cách 2 giây/request).
- **Tập ID:** 5.000 arXiv ID liên tiếp từ `2508.12872` đến `2508.17871` (tháng 08/2025).
- **Nguồn số liệu:** `state/s2_progress.jsonl`, các file trong `references/` và `state/stages/references/`, log `s2_batch.log`.
- Cấu hình máy và đường truyền mạng không được ghi lại trong lần chạy này.

### 6.2. Kết quả theo trạng thái

| Trạng thái     | Số paper | Tỉ lệ  |
| -------------- | -------: | -----: |
| `success`      |    4.717 | 94,34% |
| `no_data`      |      266 |  5,32% |
| `not_indexed`  |       17 |  0,34% |
| `api_error`    |        0 |  0,00% |
| **Tổng**       | **5.000** | 100%  |

Toàn bộ 5.000 paper kết thúc ở trạng thái terminal ngay ở lượt đầu, không cần lượt retry bổ sung.

### 6.3. Hiệu năng và độ ổn định

| Chỉ số                                                   | Giá trị                      |
| -------------------------------------------------------- | ---------------------------: |
| Tổng thời gian xử lý (cộng cột `seconds`)                 | 806 giây (~13,4 phút)        |
| Thời gian trung bình / paper                              | 0,161 giây                   |
| Trung vị / tối đa mỗi paper                               | 0,109 giây / 6,26 giây       |
| Thông lượng                                              | ~6,2 paper/giây (~372 paper/phút) |
| Số lần gặp HTTP 429                                       | 57, đều được retry thành công |
| Số lần tách batch do HTTP 400                              | 0                            |
| Paper phải dùng endpoint phân trang                        | 13                           |
| Dung lượng output `references/` (dữ liệu + provenance)     | 95,8 MB (~19 KB/paper)        |

Ghi chú: `seconds` của mỗi paper là thời gian của cả batch chia đều cho số paper trong batch, cộng thời gian xử lý riêng; con số đã gồm thời gian chờ throttle và retry. Log bắt đầu lúc 15:46:26 và dòng retry cuối lúc 15:59:51, khớp với tổng khoảng 13,4 phút.

### 6.4. Đặc điểm dữ liệu reference thu được

| Chỉ số                                         | Giá trị             |
| ---------------------------------------------- | ------------------: |
| Tổng số reference (sau loại trùng)              | 203.066             |
| Trung bình reference / paper (tất cả paper)     | 40,6                |
| Trung bình reference / paper (paper có reference) | 43,0             |
| Trung vị / tối đa                               | 36 / 365            |
| Reference có arXiv ID                            | 93.355 (45,97%)     |

Tỉ lệ thiếu từng trường trên 203.066 reference:

| Trường thiếu            | Số reference | Tỉ lệ  |
| ----------------------- | -----------: | -----: |
| `ref_arxiv_id`          |      109.711 | 54,03% |
| `ref_authors`           |       25.173 | 12,40% |
| `ref_s2_id`             |       24.245 | 11,94% |
| `ref_submission_date`   |       15.969 |  7,86% |

Hơn một nửa reference không có arXiv ID. Đây là đặc điểm của dữ liệu (nhiều tài liệu tham khảo là bài báo hội nghị/tạp chí không đăng arXiv), không phải lỗi crawl; nhóm giữ lại các reference này để phục vụ bước matching ở Milestone 3.

### 6.5. Stage `metadata`
Chưa có lần chạy thật được lưu lại cho stage `metadata`. Vì stage này không gọi mạng và chỉ xử lý record Discovery trong bộ nhớ, chi phí thời gian chủ yếu nằm ở Discovery (TV1). Tính đúng đắn được kiểm chứng bằng test offline (mục 7).

---

## 7. KIỂM THỬ

### 7.1. Các nhóm test

| File / nhóm                    | Nội dung kiểm tra                                                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| References – layout & hợp đồng | Đúng vị trí file, đủ trường theo hợp đồng, log progress mỗi lần thử, khóa thư mục cho ID dạng cũ                        |
| References – arXiv ID          | Chỉ lấy từ trường `ArXiv` của S2; DOI arXiv không bị chuyển thành ID; ID thiếu được đánh dấu                             |
| References – resume            | Orchestrator dùng lại kết quả batch; chạy lại chỉ thử paper lỗi; `api_error` không phải trạng thái kết thúc               |
| References – chuẩn hóa         | Đủ trường; ngày rơi về năm; giá trị thiếu là `null`/`[]`; loại trùng theo S2 ID / arXiv ID; không gộp mục chỉ có tiêu đề; bỏ mục rỗng |
| References – trạng thái        | `no_data`, `not_indexed`, lỗi API không ghi file dữ liệu                                                               |
| References – HTTP              | Trạng thái từ response batch; loại trùng; danh sách bị cắt dùng endpoint phân trang; HTTP 400 chia batch tới đúng ID lỗi; hết retry đánh dấu cả batch lỗi |
| Metadata – cấu trúc            | Đủ cột bảng `papers`; paper 1 version không có `revised_dates`; trường tùy chọn thiếu được liệt kê                      |
| Metadata – theo version        | Mỗi version giữ metadata riêng; thay đổi tiêu đề không lẫn sang version khác; checkpoint cũ thiếu trường vẫn hợp lệ      |
| Metadata – dữ liệu sai         | Discovery không thành công, tiêu đề rỗng, không có tác giả, ngày không timezone/sai định dạng, sai số `revised_dates`, thiếu version, sai paper, tiêu đề cấp paper khác version mới nhất |
| Metadata – adapter             | Ghi artifact và `StageResult`, khóa thư mục ID dạng cũ, thay thế stub cũ                                               |

Toàn bộ test dùng response giả lập, không cần Internet và không gọi Semantic Scholar thật.

### 7.2. Kết quả chạy test
Lệnh:

```bash
python -m unittest discover -s tests -v
```

Kết quả chạy ngày 29/10/2026 trên Python 3.14: **76 test, tất cả OK**, trong đó 43 test thuộc phần TV4 (25 references + 18 metadata).

---

## 8. KẾT LUẬN

### 8.1. Kết quả TV4
TV4 đã hoàn thành hai stage `references` và `metadata` theo hợp đồng của pipeline:
- Stage `references` lấy dữ liệu từ Semantic Scholar theo batch, có throttle giữ qua các lần chạy, retry có backoff, tự chia batch khi lỗi 400, tự chuyển sang phân trang khi danh sách bị cắt, chuẩn hóa và loại trùng mà không suy đoán dữ liệu. Lần chạy thật 5.000 paper hoàn tất trong khoảng 13,4 phút, 0 lỗi, thu được 203.066 reference.
- Stage `metadata` không gọi mạng, giữ metadata riêng của từng version, kiểm tra chặt tính nhất quán và tương thích ngược với schema `1.0`.

### 8.2. Hạn chế và hướng tiếp theo
- Dữ liệu reference phụ thuộc vào độ phủ của Semantic Scholar (0,34% paper chưa được index, 5,32% không có reference). Có thể bổ sung nguồn dự phòng là bibliography trong source LaTeX sau khi stage extract của TV3 hoàn tất.
- 54% reference không có arXiv ID; việc ghép với paper arXiv sẽ cần matching theo tiêu đề/tác giả ở Milestone 3.
- Chế độ "phạt" sau 429 hiện không làm chậm thêm khi có key (1,5 giây < 2 giây); cần tăng giá trị nếu muốn giảm số lần 429.
- Chưa benchmark stage `metadata` trên dữ liệu thật.
