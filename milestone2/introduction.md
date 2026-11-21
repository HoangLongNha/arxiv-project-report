# Mục tiêu & Kiến trúc Luồng Xử lý Dữ liệu

## 1. Bối cảnh Học thuật và Bài toán Đặt ra

Mã nguồn LaTeX của các bài báo khoa học trên arXiv là nguồn tài nguyên vô giá phục vụ việc khai phá tri thức học thuật (Scholarly Knowledge Graph). Tuy nhiên, việc trích xuất và chuẩn hóa dữ liệu từ kho lưu trữ này đối mặt với các thách thức kỹ thuật lớn:
- **Cấu trúc phân tán và phi tuyến tính:** Một công trình nghiên cứu thường gồm hàng chục tệp `.tex` phân mảnh, lồng ghép qua các lệnh `\input`, `\include` đệ quy, trộn lẫn các khối văn bản nháp không tham gia vào luồng biên dịch chính.
- **Sự đa dạng về cú pháp biểu diễn:** Cùng một khái niệm ngữ nghĩa có thể được trình bày bằng nhiều cách khác nhau (toán nội dòng `$...$` hoặc `\(...\)`; toán khối `$$...$$`, `\[...\]`, `align`, `gather`; danh sách lồng ghép nhiều tầng).
- **Rác định dạng giao diện trực quan:** Các tác giả sử dụng dày đặc các lệnh dàn trang, kẻ bảng, đổi màu (`\centering`, `\small`, `\textcolor`, `\maketitle`) làm biến dạng câu văn nếu chỉ bóc tách văn bản thô sơ.
- **Tiến hóa xuyên phiên bản (Cross-version Evolution):** Bài báo trên arXiv trải qua nhiều lần cập nhật ($v_1, v_2, \dots, v_n$). Các phiên bản chia sẻ phần lớn nội dung câu văn và tài liệu tham khảo nhưng các khóa trích dẫn (`citation_key`) có thể bị thay đổi cách viết giữa các lần nộp bài.

Mục tiêu của **Milestone 2** là giải quyết triệt để các vấn đề trên:
1. Chuyển đổi toàn bộ mã nguồn TeX thành **Cây phân cấp đối tượng ngữ nghĩa (Hierarchical Semantic Tree)**: $\text{Document} \rightarrow \text{Heading} \rightarrow \text{Sentence} \mid \text{Formula} \mid \text{Figure} \mid \text{List}$.
2. Chuẩn hóa hình thức biểu diễn toán học và văn bản, loại bỏ triệt để mã trình bày thừa mà không làm suy hao ngữ nghĩa.
3. Trích xuất tài liệu tham khảo từ cả hai nguồn (`\bibitem` viết tay và tệp `.bib` đi kèm) sang chuẩn BibTeX.
4. Thực hiện thuật toán **Khử trùng lặp 2 cấp độ (Two-level Deduplication)** xuyên các phiên bản, hợp nhất thông tin trích dẫn và đồng bộ hóa toàn bộ các lệnh `\cite{}` trong văn bản bài báo.
5. Xuất bản 3 bảng dữ liệu chuẩn hóa (`elements`, `hierarchy`, `bibtex`) đáp ứng bộ kiểm định chất lượng (QA Verification — kết quả chạy toàn corpus đang chờ kiểm chứng).

---

## 2. Kiến trúc Luồng Xử lý 5 Trạm (5-Stage Pipeline)

Hệ thống được thiết kế theo kiến trúc chia tách trách nhiệm (Separation of Concerns) gồm 5 trạm xử lý liên hoàn:

```text
ĐẦU VÀO MILESTONE 1:
  corpus/<key>/vN/*.tex, *.bib  &  DiscoveryRecord (metadata.json)
                  │
                  ▼
XỬ LÝ THEO TỪNG PHIÊN BẢN (Per-Version Stages):
  ┌─────────────────────────────────────────────────────────────┐
  │ Trạm 1: TeX Resolver (TV1) - parsing/resolver.py            │
  │   - Master document detection & include DFS stack           │
  │   - Comment stripping, Preamble & Bibliography separation   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ gathered.json
                 ┌───────────────┴───────────────┐
                 │ merged_body_tex               │ raw_bibitems & .bib
                 ▼                               ▼
  ┌─────────────────────────────┐ ┌─────────────────────────────┐
  │ Trạm 2: Hierarchy (TV2)     │ │ Trạm 4A: Bibliography (TV4) │
  │   - Stack heading rank 1..7 │ │   - Parse \bibitem regex    │
  │   - Formatted PRL headings  │ │   - Parse .bib files        │
  │   - Leaf node categorization│ └──────────────┬──────────────┘
  └──────────────┬──────────────┘                │ raw_bibtex.json
                 │ raw_tree.json                 │ (mọi version)
                 ▼                               │
  ┌─────────────────────────────┐                │
  │ Trạm 3: Normalization (TV3) │                │
  │   - Immediate Math Masking  │                │
  │   - Color & Style unwrapping│                │
  │   - Sentence segmentation   │                │
  │   - Preorder traversal      │                │
  └──────────────┬──────────────┘                │
                 │ normalized_tree.json          │
                 │ (mọi version)                 │
                 └───────────────┬───────────────┘
                                 ▼
XỬ LÝ CẤP TOÀN BỘ BÀI BÁO (Per-Paper Stages):
  ┌─────────────────────────────────────────────────────────────┐
  │ Trạm 4B: Deduplication (TV4) - parsing/deduplication.py     │
  │   - Cấp 1: Deduplicate BibTeX, union fields, rename \cite   │
  │   - Cấp 2: Deduplicate content (kind, content) -> element_id│
  │   - Xuất bảng tables/<key>/ và parsed/<key>/vN/occurrences  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Trạm 5: QA Validation & Benchmark (TV5)                     │
  │   - Schema & FK verification, Multiset Equivalence check    │
  │   - DAG cycle detection, Deep BibTeX 1-to-1 verification    │
  │   - Memory sampling (psutil RSS), Wall time, Scope filter   │
  └──────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
SẢN PHẨM XUẤT BẢN:
  tables/{elements.json, hierarchy.json, bibtex.json, references.bib}
  parsed/vN/occurrences.json  &  manifests/parsing.json  &  Jupyter Book
```

### 2.1. Phân định ranh giới Xử lý theo Version và theo Paper
- **Nhánh theo từng phiên bản (Per-Version Execution):**
  - **Trạm 1 (`resolver.py`):** Ghép nối đa file thành luồng TeX liên tục; bóc tách `\begin{thebibliography}` và định vị các tệp `.bib`. Đầu ra: `gathered.json`.
  - **Trạm 2 (`hierarchy.py`):** Nhận `merged_body_tex`, duyệt cây tiêu đề bằng ngăn xếp động, bóc tách các khối nguyên tử và nút lá thô. Đầu ra: `raw_tree.json`.
  - **Trạm 3 (`normalization.py`):** Làm sạch mã lệnh trình bày TeX, chuẩn hóa công thức toán, phân đoạn câu văn lá (`sentence`) bằng token masking. Đầu ra: `normalized_tree.json`.
  - **Trạm 4A (`bibliography.py`):** Chuyển đổi danh mục tham khảo của phiên bản đó thành các bản ghi BibTeX thô. Đầu ra: `raw_bibtex.json`.
- **Nhánh cấp toàn bộ bài báo (Per-Paper Execution):**
  - **Trạm 4B (`deduplication.py`):** Thu thập toàn bộ `normalized_tree.json` và `raw_bibtex.json` của mọi phiên bản thuộc bài báo:
    - *Cấp 1:* Khử trùng lặp tài liệu tham khảo theo DOI/tiêu đề chuẩn hóa, hợp nhất trường dữ liệu về một khóa duy nhất, và đổi tên mọi lệnh `\cite{}` trong toàn văn cây bài báo.
    - *Cấp 2:* Khử trùng lặp nội dung câu văn và phần tử cùng `(kind, cleaned_content)`, gán mã định danh duy nhất `element_id`.
    - Xuất bản 3 bảng dữ liệu cùng `references.bib`, `parsing_manifest.json` và `occurrences.json`.
  - **Trạm 5 (`validation.py` & `benchmark.py`):** Thẩm định độc lập tính hợp lệ của toàn bộ các bảng đầu ra, cấu trúc cây phân cấp không chu trình, tương đương đa tập (Multiset Equivalence), đo đạc thời gian và bộ nhớ nền (`psutil`).

---

## 3. Hợp đồng Thực thi Bền vững (Durable Execution Contract — Schema 2.0)

Nhằm đảm bảo tính độc lập và an toàn khi phối hợp giữa 5 thành viên, hệ thống áp dụng cơ chế hợp đồng chuẩn hóa:

### 3.1. Chữ ký Adapter Thống nhất
Mọi module từ Trạm 1 đến Trạm 5 đều tuân thủ chữ ký hàm adapter tiêu chuẩn:
```python
def run(record: DiscoveryRecord, output_dir: Path | str, *, version: int | None = None, upstream: dict | None = None) -> StageResult:
    ...
```

### 3.2. Cấu trúc Phong bì Kết quả `StageResult`
Mỗi giai đoạn sau khi hoàn tất đều trả về đối tượng `StageResult` chứa thông tin định danh và dấu vết thực thi:
- `stage` (str): Tên giai đoạn (`resolve`, `hierarchy`, `normalize`, `bibliography`, `deduplicate`, `validate_parse`).
- `status` (str): Trạng thái thực thi, gồm:
  - `success`: Xử lý thành công có dữ liệu.
  - `no_source`: Phiên bản không có mã nguồn TeX (PDF-only) nhưng được ghi nhận rỗng an toàn.
  - `skipped`: Phiên bản bị bỏ qua do giai đoạn upstream chưa sẵn sàng hoặc thiếu dữ liệu.
  - `data_error`: Lỗi định dạng dữ liệu đầu vào hoặc vi phạm ràng buộc hợp đồng.
  - `error`: Lỗi ngoại lệ hệ thống I/O hoặc hệ điều hành.
- `artifacts` (dict[str, str]): Ánh xạ tên artifact sang đường dẫn tương đối tính từ `output_dir`.
- `schema_version` (str): Cố định `"2.0"` cho toàn bộ giai đoạn Milestone 2.

### 3.3. Cơ chế Khôi phục Thông minh (Checkpoint & Resume via SHA-256)
- Pipeline tự động lưu vết trạng thái của từng giai đoạn tại `state/stages/<stage_name>/<paper_key>/v<version>.json` (hoặc `paper.json`).
- Mỗi checkpoint lưu trữ mã băm SHA-256 của toàn bộ tệp đầu vào, mã nguồn module phụ trách, và các artifact đã sinh.
- Khi thực thi với cờ `--resume`, Orchestrator so sánh mã băm phụ thuộc. Nếu không có bất kỳ thay đổi nào từ mã nguồn hoặc dữ liệu đầu vào, giai đoạn đó được tái sử dụng tức thì mà không cần tính toán lại, rút ngắn thời gian chạy kiểm thử tích hợp xuống dưới 1 giây.

---

## 4. Đặc tả Sản phẩm Dữ liệu Đầu ra

Kết quả của Milestone 2 được ghi tại thư mục `tables/<paper_key>/` với quy chuẩn định dạng:

| Tên tệp / Bảng | Vai trò | Đặc tả cấu trúc |
| :--- | :--- | :--- |
| **`elements.json`** | Bảng phần tử nội dung | Mảng các bản ghi `ElementRow` gồm 4 trường bắt buộc: `element_id`, `arxiv_id`, `kind`, `content`. |
| **`hierarchy.json`** | Bảng quan hệ cây phân cấp | Mảng các bản ghi `HierarchyRow` gồm đúng 4 cột: `arxiv_id`, `version`, `element_id`, `parent_id`. |
| **`bibtex.json`** | Bảng tài liệu tham khảo | Mảng các bản ghi `BibtexRow` gồm 9 cột: `arxiv_id`, `citation_key`, `entry_type`, `title`, `authors`, `year`, `doi`, `journal`, `url`. |
| **`references.bib`** | Tệp BibTeX tiêu chuẩn | Dữ liệu bảng `bibtex.json` được kết xuất dưới cú pháp BibTeX hợp lệ phục vụ công cụ tra cứu học thuật. |
| **`occurrences.json`** | Nguồn sự thật cây từng version | Lưu vết từng lần xuất hiện của phần tử trong từng version (`occurrence_id`, `parent_occurrence_id`, `position`, `element_id`), bảo toàn cấu trúc cây trước khi gộp nội dung. |
| **`parsing_manifest.json`** | Bản kê tổng hợp cấp bài báo | Ghi nhận `expected_versions`, `complete`, thống kê số lượng trước/sau khử trùng lặp (`counts`), và danh mục cảnh báo (`warnings`). |
| **`validation/<key>.json`** | Báo cáo kiểm định chất lượng | Chứng nhận kiểm định của TV5: `valid` (bool), chi tiết các kiểm tra schema, referential integrity, tree validity, và business rules. |
