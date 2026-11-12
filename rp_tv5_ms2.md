# Báo cáo Triển khai Module Validation & Benchmark (TV5) — Milestone 2

- **Người thực hiện:** Huỳnh Tuấn Kiệt (MSSV: 24120330)
- **Vai trò:** Thành viên 5 (TV5) — Nhóm 6
- **Module phụ trách:**
  - `src/arxiv_pipeline/reporting/milestone2/validation.py` (QA Validator & Contract Enforcement)
  - `src/arxiv_pipeline/export/benchmark.py` & `src/arxiv_pipeline/reporting/milestone2/benchmark.py` (Performance Profiling & Benchmark Harness)
- **Bộ kiểm thử:**
  - `tests/parsing/test_validation.py` (43 unit tests)
  - `tests/parsing/test_ms2_benchmark.py` (7 unit tests)
- **Các Pull Requests đã merge vào main:**
  - **PR #18:** `feat(parsing): implement TV5 MS2 validator, benchmark harness and unit tests` (commits: `4e480ef`, `4c63f2d`, `63c185b`).
  - **PR #19:** `fix(validation): handle repeated elements, verify occurrence tree, and enforce snapshot match` (commits: `de7adfa`, `a8be45b`, `7fc72e7`, `db949ee`, `b32cd7d`).

---

## 1. Mục tiêu và Vai trò trong Pipeline Milestone 2

Trong kiến trúc xử lý của Milestone 2, module **Validation & Benchmark (TV5)** giữ vai trò là "chốt chặn" kiểm định chất lượng cuối cùng và đo lường tài nguyên toàn hệ thống:
1. **Kiểm định chất lượng đầu ra (Quality Assurance & Contract Enforcement):** Tiếp nhận kết quả cuối từ **Deduplication (TV4)** và đối chiếu với toàn bộ chuỗi checkpoint trung gian (`resolve`, `hierarchy`, `normalize`, `bibliography`). Đảm bảo toàn bộ 3 bảng quan hệ (`elements.json`, `hierarchy.json`, `bibtex.json`), file trích dẫn chuẩn (`references.bib`), cấu trúc cây xuất hiện (`occurrences.json`), cùng manifest bao phủ (`parsing_manifest.json`) tuân thủ nghiêm ngặt đặc tả hợp đồng `MS2_CONTRACTS.md` và schema v2.0 (`PARSING_SCHEMA_VERSION`).
2. **Bảo mật và an toàn dữ liệu:** Xác thực đường dẫn artifact qua cơ chế `safe_path`, ngăn chặn triệt để lỗ hổng Directory Traversal (`..`), đường dẫn tuyệt đối, và các liên kết tượng trưng / NTFS Directory Junctions thoát khỏi thư mục gốc `output_dir`.
3. **Đối chiếu chéo Snapshot đầu vào (Snapshot Alignment):** Đảm bảo `input_snapshot_id` từ upstream context và manifest của paper khớp tuyệt đối, phát hiện kịp thời các trường hợp dữ liệu MS1 bị tráo đổi hoặc cache sai lệch giữa các lần chạy.
4. **Kiểm định toàn vẹn cấu trúc cây (Tree Integrity & Cycle Detection):** Xác thực cây phân cấp không chu trình, có duy nhất một Document Root, chỉ số `position` liên tục từ $0 \dots k-1$, và thỏa mãn quy tắc tương đương đa tập (Multiset Equivalence) chính xác 1-1 giữa các cạnh trong `occurrences.json` và bảng `hierarchy.json`.
5. **Đồng bộ trích dẫn học thuật (Citation & BibTeX Deep Verification):** Phân tích sâu nội dung file `references.bib` bằng parser thực tế (`parse_bib_text`) và đối chiếu 1-1 từng trường với bảng `bibtex.json`. Kiểm tra tính đồng bộ giữa các citation key được gọi trong văn bản (`\cite{...}`) với kho trích dẫn.
6. **Đo lường hiệu năng và kiểm chứng bằng chứng thực nghiệm (Empirical Benchmark Harness):** Đo lường trực tiếp thời gian thực thi (Wall Time), giám sát bộ nhớ tiến trình nền định kỳ (RSS Memory Sampling qua `psutil`), tính toán dung lượng đĩa thực tế của các artifact đã xuất, và xác thực bằng chứng qua mã băm SHA-256 (`_verified_stage`, `_verified_export`), loại bỏ hoàn toàn các giả định hay hằng số giả mạo (Zero Synthetic Defaults).

---

## 2. Các tính năng kỹ thuật cốt lõi đã triển khai

### 2.1. Kiểm định Hợp đồng và Toàn vẹn Dữ liệu (QA Validation Engine)
- **Kiểm định 3 bảng xuất khẩu (`elements`, `hierarchy`, `bibtex`):**
  - `elements.json`: Bắt buộc đúng 4 trường `element_id`, `arxiv_id`, `kind`, `content`. Khóa phần tử có tiền tố chuẩn hóa `{paper_id}#`. `kind` thuộc danh mục hợp lệ (`document`, `heading`, `itemize`, `item`, `sentence`, `block_formula`, `figure`). Nghiêm cấm tiêu đề cấm `References` / `Bibliography`. Đảm bảo tính duy nhất của cặp `(kind, content)` trên toàn bộ phần tử phi-document (Business Rule Deduplication).
  - `hierarchy.json`: Bắt buộc đúng 4 cột `arxiv_id`, `version`, `element_id`, `parent_id`. Kiểm tra toàn vẹn khóa ngoại (Foreign Key) trỏ về `elements.json`. Không bao giờ chứa cạnh có `parent_id = null`. Document root không được phép làm nút con.
  - `bibtex.json`: Bắt buộc đúng 9 cột theo schema. Bắt buộc `title` phải là chuỗi (loại bỏ trường hợp `null`), `authors` là danh sách chuỗi, `year` là số nguyên hợp lệ hoặc `None`.
- **Kiểm tra khai báo Artifact nghiêm ngặt (Strict Artifact Declarations):**
  - TV5 tuyệt đối không dùng đường dẫn fallback mặc định trên đĩa. Toàn bộ artifact (`elements`, `hierarchy`, `bibtex`, `bibtex_file`, `parsing_manifest`) bắt buộc phải được khai báo tường minh trong checkpoint `deduplicate` của TV4. Bất kỳ sự thiếu hụt khai báo nào đều bị xử lý là vi phạm bảo mật/hợp đồng (`missing_artifact_declaration`).

### 2.2. Kiểm định Cây Xuất hiện & Tương đương Đa tập (Occurrences Tree & Multiset Equivalence)
- **Tính hợp lệ của cây Occurrences theo từng version (`parsed/<paper_key>/vN/occurrences.json`):**
  - `occurrence_id` là duy nhất trong từng phiên bản.
  - Mỗi version thành công phải có duy nhất một nút gốc (`parent_occurrence_id = None`) với `position = 0` và trỏ đúng vào phần tử Document Root tương ứng (`{prefix}root{v_num}`).
  - Thuật toán dò chu trình (Cycle Detection) dựa trên tập duyệt tổ tiên đảm bảo cây là đồ thị có hướng không chu trình (DAG).
  - Vị trí các con thuộc cùng một cha phải bắt đầu từ `0` và liên tục liên tiếp: $0, 1, \dots, k-1$. Nghiêm cấm các kiểu dữ liệu sai lệch (ví dụ cờ boolean `True/False`).
- **Xác thực Đa tập (Multiset Equivalence Check):**
  - Khác với kiểm tra tập hợp (`set`), cơ chế kiểm tra `Counter(occ_edges) == Counter(hier_edges)` cho phép một phần tử trùng lặp (ví dụ hai câu giống hệt nhau hoặc heading lặp lại xuất hiện nhiều lần dưới cùng một cha) có nhiều cạnh tương ứng trong `hierarchy.json` mà không bị báo lỗi giả `multiple_parents`.
  - Thực hiện kiểm tra đối chiếu kép: theo từng version độc lập và trên toàn cục (Global Multiset Equivalence across all versions).

### 2.3. Đối chiếu chuyên sâu Trích dẫn & BibTeX (Citation Verification)
- **Kiểm tra 1-1 giữa `references.bib` và `bibtex.json`:**
  - Không chỉ kiểm tra sự tồn tại file, TV5 gọi trực tiếp parser `parse_bib_text` phân tích toàn bộ cú pháp của `references.bib`.
  - Đối chiếu số lượng bản ghi và khớp nối từng trường: `entry_type`, `year`, `authors` (chuẩn hóa chữ thường), `title` (qua `normalize_title`), và `doi` (qua `normalize_doi`).
  - Nếu `bibtex.json` rỗng, `references.bib` bắt buộc phải rỗng (ngăn chặn rác trích dẫn).
- **Đồng bộ khóa trích dẫn văn bản (`\cite{...}`):**
  - Trích xuất toàn bộ citation key được viện dẫn trong các node văn bản `kind="sentence"` thông qua regex `_CITE_RE`.
  - Đối chiếu với tập khóa trong `bibtex.json`. Nếu có khóa trích dẫn không tồn tại trong BibTeX, hệ thống kiểm tra danh sách `warnings` của manifest (`citation_key_unknown`). Bất kỳ khóa trích dẫn nào chưa được giải trình đều được cảnh báo vi phạm nghiệp vụ (`unresolved_citations`).

### 2.4. Khung Benchmark và Đo lường Hiệu năng Thực nghiệm (Performance Profiling Harness)
- **Giám sát tài nguyên phần cứng nền (`MemorySampler`):**
  - Khởi tạo tiến trình tiểu luồng (Thread) định kỳ 0.2 giây đo lượng bộ nhớ thực tế (RSS) của tiến trình chính cùng toàn bộ các tiến trình con (`psutil.Process.children`) để ghi nhận `peak_ram_mb` và `avg_ram_mb`.
- **Đo lường thời gian chính xác cao:**
  - Sử dụng `time.perf_counter()` đo lường thời gian chạy End-to-end Wall Time.
- **Tính toán tỷ lệ nén Deduplication & Số trích dẫn được đổi tên:**
  - `element_dedup_reduction_pct` và `bibtex_dedup_reduction_pct` được tính trực tiếp từ số lượng thực tế trước và sau deduplication.
  - `count_renamed_citations_for_paper`: Tái hiện đúng thứ tự phiên bản tăng dần theo số nguyên của TV4, kết hợp `unionize_bibtex` để đếm chính xác số lượt trích dẫn được viết lại trong cây `normalized_tree.json`.
- **Xác thực bằng chứng thực tế (`_verified_stage`, `_verified_export`):**
  - Đọc trực tiếp các checkpoint và file `.dependencies.json` tại `state/stages/`.
  - Kiểm tra mã băm SHA-256 của toàn bộ artifact và fingerprint phụ thuộc. Ngăn chặn việc chạy benchmark trên dữ liệu đã bị sửa đổi, thiếu sót hoặc sai lệch snapshot.
  - Tính toán dung lượng lưu trữ `final_output_storage_mb` dựa trên kích thước thực tế của tập hợp các artifact được export hợp lệ (`exported_paths`).

### 2.5. Adapter Tích hợp Pipeline v2.0 (`run`) & Xử lý Dị thường An toàn
- Đóng gói adapter theo chữ ký chuẩn `run(record, output_dir, *, version=None, upstream=None) -> StageResult`.
- Đảm bảo tính bất biến và nguyên tử (Atomic Write) qua hàm `atomic_json` ghi `validation/parsing/<paper_key>.json`.
- **Cơ chế phòng thủ dị thường (Fault-Tolerant Reporting):**
  - Khi nhận đầu vào hỏng (record không hợp lệ, thiếu discovery versions, thiếu upstream deduplicate checkpoint, hoặc checkpoint bị sai lệch định danh), module không bao giờ bị crash mà tự động xuất báo cáo lỗi chi tiết (`valid=False`, status `data_error` / `skipped`) kèm mã lỗi có cấu trúc (`ErrorInfo`).
  - Tự động thay thế báo cáo `success` trước đó thành `skipped` / `data_error` nếu phát hiện upstream stage bị chuyển trạng thái lỗi ở lần chạy sau.

---

## 3. Quá trình gỡ lỗi và hoàn thiện qua các đợt Review

Dựa trên quá trình kiểm tra chéo và mã nguồn trong các commit hoàn thiện (đặc biệt là đợt review khắc phục các issue kỹ thuật #1 đến #11 và cập nhật bằng chứng thực nghiệm trong `diff.patch` / PR #19), TV5 đã giải quyết triệt để các vấn đề sau:

| Vấn đề phát hiện | Nguyên nhân gốc rễ | Giải pháp kỹ thuật đã áp dụng | Commit / PR |
| :--- | :--- | :--- | :--- |
| **Bảo mật đường dẫn artifact (`safe_path`)** | Chỉ kiểm tra `candidate.is_absolute()`, có thể bị vượt rào bởi `\\`, `..` hoặc symlink/junctions | Bổ sung cấm `\\`, cấm `..` trong parts, quét toàn bộ cây tổ tiên phát hiện symlink hoặc NTFS Junction (`is_junction`) | `b32cd7d` (PR #19) |
| **Xử lý dị thường đầu vào (`run` wrapper)** | Module ném unhandled exception khi nhận `record` hoặc `upstream` bị `None`/rỗng | Xây dựng hàm bọc `run` an toàn: bắt lỗi và sinh `validation/<key>.json` với `valid=False` cùng `StageResult.status="data_error"` | `b32cd7d` (PR #19) |
| **Tiêu đề BibTeX nhận giá trị `null`** | Bảng `bibtex.json` có dòng có `title = None` nhưng validator chỉ kiểm tra `entry_type` | Bổ sung kiểm tra nghiêm ngặt `isinstance(title, str)` (Issue 10); từ chối tiêu đề không phải string | `7fc72e7`, `b32cd7d` (PR #19) |
| **Vị trí và phiên bản bị ép kiểu ngầm từ `bool`** | Trong Python, `isinstance(True, int)` trả về `True`, khiến giá trị boolean lọt qua kiểm tra số nguyên | Sử dụng kiểm tra kiểu định danh chặt chẽ: `type(pos) is not int` và `type(version) is not int` | `7fc72e7`, `b32cd7d` (PR #19) |
| **Bằng chứng Benchmark chưa được chứng thực** | Benchmark tính toán trên file rác cũ hoặc file bị chỉnh sửa mà không đối chiếu với checkpoint Orchestrator | Bổ sung `_verified_stage` và `_verified_export`: kiểm tra mã băm SHA-256 của checkpoint và artifacts; đối chiếu snapshot validation | `b32cd7d` (PR #19) |
| **Phần tử trùng lặp hợp lệ bị báo lỗi nhiều cha** | Validator cũ dùng cấu trúc cây giả định mỗi element chỉ xuất hiện 1 lần, báo lỗi khi một câu lặp lại nhiều lần | Nâng cấp mô hình kiểm tra sang quan hệ Đa tập (Multiset Correspondence): đối chiếu `Counter(occ_edges) == Counter(hier_edges)` | `de7adfa` (PR #19) |
| **Lệch snapshot giữa context và manifest** | Manifest lưu snapshot cũ trong khi Orchestrator chạy trên snapshot mới | Bắt buộc đối chiếu `manifest.input_snapshot_id == context.input_snapshot_id` (cả 2 phải khác rỗng) | `de7adfa`, `7fc72e7` (PR #19) |
| **Cạnh hierarchy mồ côi từ version lỗi** | Bảng `hierarchy.json` còn sót lại các dòng của version có trạng thái `no_source` hoặc chưa xử lý | Kiểm tra chéo phiên bản trong hierarchy bắt buộc phải thuộc danh sách `manifest_versions` có trạng thái `success` (Issue 7) | `7fc72e7` (PR #19) |
| **Quy tắc phần tử gốc Document Root** | Document element xuất hiện sai ở các version không tồn tại hoặc bị gán làm nút con | Kiểm tra tập hợp Document elements khớp chính xác 1-1 với các version `success`; cấm document element làm nút con (Issue 8) | `7fc72e7` (PR #19) |
| **Không nhất quán số lượng Dedup Counts** | `elements_before` nhỏ hơn `elements_after` hoặc không khớp với tổng số lượng occurrences | Kiểm tra chặt chẽ điều kiện: `elements_before >= elements_after` và `elements_before == total_occurrences` (Issue 9) | `7fc72e7` (PR #19) |
| **Cú pháp BibTeX file không đồng bộ** | File `references.bib` bị sinh rác khi `bibtex.json` rỗng hoặc sai lệch thông tin trường | Dùng `parse_bib_text` phân tích cú pháp sâu; cấm nội dung rác trong file `.bib` khi bảng rỗng (Issue 6) | `7fc72e7` (PR #19) |
| **Lỗi chia cho 0 trong Benchmark Summary** | Lượt chạy benchmark với tập phân công rỗng (`total_assigned = 0`) gây lỗi `ZeroDivisionError` | Xử lý an toàn mẫu số: trả về 0.0% khi `assigned_count == 0` (Issue 11) | `7fc72e7` (PR #19) |

---

## 4. Kết quả Kiểm thử và Nghiệm thu

Bộ kiểm thử của TV5 tại `tests/parsing/test_validation.py` và `tests/parsing/test_ms2_benchmark.py` đã đạt độ bao phủ toàn diện:
- **Tổng số ca kiểm thử nội bộ TV5:** **50 / 50 tests passed** (thời gian chạy ~2.9s).
- **Phân loại các nhóm bài kiểm thử:**
  1. *Validation Chuẩn & Cây Occurrences:* 5 tests (dataset hợp lệ, nhiều lần xuất hiện hợp lệ của element lặp, chu trình cây, vị trí không liên tục, no_source hợp lệ).
  2. *Toàn vẹn Schema & Khóa ngoại:* 6 tests (sai lệch kind, tiêu đề cấm References, trùng lặp cặp kind-content, khóa ngoại mồ côi, thừa cột hierarchy, an toàn đường dẫn `safe_path`).
  3. *Bộ kiểm thử các Issue Review (#1 đến #11):* 7 tests (thiếu khai báo bibtex_file, thừa cạnh hierarchy mồ côi, quy tắc document root, tính đúng đắn counts trước/sau dedup, chặt chẽ kiểu dữ liệu schema, xử lý số 0 benchmark).
  4. *Khả năng chịu lỗi & Dị thường đầu vào (Malformed Inputs & Security):* 14 tests (shape artifact hỏng, occurrences hỏng, manifest version hỏng, checkpoint deduplicate sai định danh, ghi đè trạng thái skipped khi upstream bị chặn, title không phải string, version boolean bị từ chối, record malformed không crash).
  5. *Deep BibTeX Parsing & Snapshot Alignment:* 4 tests (phân tích sâu cú pháp `references.bib`, phát hiện sai lệch trường trích dẫn, kiểm tra lệch/thiếu snapshot ID).
  6. *Benchmark & Performance Profiling Harness:* 7 tests trong `test_ms2_benchmark.py` (lọc phạm vi benchmark theo snapshot, từ chối checkpoint bị tráo snapshot, từ chối artifact chuẩn hóa bị sửa đổi, tính ánh xạ citation theo đúng thứ tự phiên bản số học, từ chối manifest chạy rỗng, đối chiếu chéo snapshot giữa validation và export, chạy pipeline thật với giám sát bộ nhớ/thời gian sống).

- **Tích hợp liên module toàn hệ thống:**
  - Vượt qua toàn bộ **425 passed, 1 skipped, 65 subtests passed** trên toàn bộ test suite của dự án (thời gian chạy ~19.2s).
  - Hoàn toàn tương thích và đồng bộ với các module: Resolver (TV1), Hierarchy (TV2), Normalization (TV3), Deduplication (TV4).
  - Kiểm tra cú pháp và định dạng: `git diff --check` đạt **0 errors**.

---

## 5. Kết luận

Phần công việc của **TV5 (Huỳnh Tuấn Kiệt)** trong Milestone 2 đã hoàn thành 100% khối lượng và chất lượng theo đúng cam kết trong hợp đồng phân công (`docs/MS2_CONTRACTS.md` và `docs/MS2_HANDOFF.md`):
- Xây dựng thành công động cơ kiểm định chất lượng nghiêm ngặt, bảo vệ an toàn toàn diện các bảng dữ liệu đầu ra và cấu trúc cây phân cấp.
- Giải quyết triệt để toàn bộ 11 vấn đề phản biện kỹ thuật trong các đợt Review và củng cố cơ chế bằng chứng thực nghiệm qua SHA-256.
- Cung cấp công cụ benchmark chuẩn xác, phục vụ trực tiếp cho việc đánh giá hiệu năng và xuất báo cáo khoa học nghiệm thu Milestone 2 trên toàn corpus.

