# Thảo luận, Phân tích Trường hợp Biên & Sẵn sàng cho Milestone 3

Chương này đi sâu đánh giá các bài học kỹ thuật rút ra trong quá trình triển khai Milestone 2, phân tích cách giải quyết 7 nhóm ca biên (Edge Cases) phức tạp trên dữ liệu arXiv thực tế, tổng kết 11 vấn đề kiểm định chất lượng (QA Issues) đã khắc phục, và đánh giá tính sẵn sàng cho Milestone 3.

---

## 1. Phân tích Chi tiết 7 Nhóm Trường hợp Biên (Edge Cases)

Trong quá trình chạy thực tế trên các bài báo thật (như `2411.13795`, `2410.08024`, `2508.17481`, `2508.17871`, `2508.17740`), hệ thống đã phát hiện và xử lý triệt để các trường hợp dị thường:

### 1.1. Ấn phẩm chỉ có tệp PDF (PDF-only Publications)
- **Thực tế:** Khoảng $2.8\%$ bài báo trên arXiv không cung cấp mã nguồn LaTeX gốc (chỉ có tệp PDF do tác giả nộp trực tiếp hoặc TeX bị lỗi từ chối biên dịch tại thời điểm nộp).
- **Vấn đề tiềm ẩn:** Nếu pipeline coi các bài báo này là lỗi xử lý (`error` hoặc `failed`) hoặc bỏ qua khỏi danh sách theo dõi, mẫu số thống kê sẽ bị sai lệch, không phản ánh đúng tỷ lệ hoàn thành của dự án.
- **Giải pháp:** TV1 và TV4 thiết lập trạng thái hợp đồng `no_source`. Version được ghi nhận là một bản ghi hợp lệ trong `manifest.versions` với `occurrences = []`. Bảng `elements.json` và `hierarchy.json` của version này không bị ép sinh dữ liệu giả mạo. TV5 kiểm định nghiêm ngặt: version `no_source` tuyệt đối không được phép có nút gốc `document` trong `elements` hay bất kỳ cạnh nào trong `hierarchy`.

### 1.2. Phiên bản chỉ có tệp BibTeX (Bib-only Publications)
- **Thực tế:** Một số phiên bản cập nhật không có thân bài báo `.tex` nhưng tác giả vẫn đính kèm tệp `.bib` cập nhật danh mục tài liệu tham khảo.
- **Giải pháp:** Hợp đồng TV1 quy định: *Không ép bảng `bibtex` phải rỗng chỉ vì bài báo không có mã nguồn TeX*. Module `bibliography.py` (TV4) quét toàn bộ tệp `.bib` trong thư mục nếu danh sách tệp được lệnh `\bibliography` tham chiếu bị rỗng, bảo tồn đầy đủ thông tin trích dẫn phục vụ cho Milestone 3.

### 1.3. Tiêu đề Định dạng Không chính quy phong cách PRL (`2411.13795`)
- **Thực tế:** Các bài báo thuộc trường phái *Physical Review Letters* (như `2411.13795`) không sử dụng macro `\section`, mà dùng kết hợp màu sắc và in đậm ở đầu đoạn văn:
  ```latex
  \textcolor[rgb]{0.00,0.00,1.00}{\textbf{Introduction.---}}
  ```
  Các bộ parser thông thường sẽ bỏ qua và sinh 0 heading, biến toàn bộ bài báo thành các khối văn xuôi trực thuộc nút gốc.
- **Giải pháp (TV2 — PR #17 & TV3 — PR #16):**
  - TV2 xây dựng cơ chế nhận diện có kiểm soát: yêu cầu bắt buộc tiêu đề phải nằm ở đầu đoạn văn (ngay sau `\n\n`, `\par`, hoặc `\maketitle`), độ dài $\le 150$ ký tự, gán thứ bậc chuẩn `heading_rank = 3` (tương đương `\section`).
  - TV3 xây dựng vòng lặp hội tụ cố định (*Fixed-point Iteration*) luân phiên giữa parser cân bằng ngoặc `_strip_color_wrappers` và `_strip_text_styles`, bóc vỏ sạch sẽ toàn bộ màu sắc và in đậm để đưa về chuỗi tiêu đề thuần túy: `Introduction.---`.

### 1.4. Bảo vệ Biểu thức Đạo hàm Toán học Cấp cao ($f''(x)$)
- **Thực tế:** Trong LaTeX, dấu nháy đơn kép `''` thường được quy đổi thành dấu nháy kép đóng `"`. Tuy nhiên, nếu thao tác thay thế dấu nháy chạy trước khi bảo vệ công thức toán, biểu thức đạo hàm cấp hai $f''(x)$ sẽ bị biến thành $f"(x)$, làm hỏng ngữ nghĩa toán học.
- **Giải pháp (TV3 — PR #13):** TV3 đưa bước **Masking Toán học Tức thời** lên vị trí ưu tiên số 1: toàn bộ công thức toán được bóc tách và thay thế bằng các token marker thuộc vùng ký tự riêng của Unicode (**Private Use Area**: `0xE000 - 0xF8FF`) trước khi thực hiện bất kỳ phép làm sạch văn bản nào. Sau khi hoàn tất làm sạch và phân đoạn câu, các token toán được hoàn nguyên theo **thứ tự đảo ngược (reverse order)**, bảo toàn nguyên vẹn $100\%$ các biểu thức đạo hàm và toán lồng nhau.

### 1.5. Xung đột Thông tin Trích dẫn giữa các Bản sửa đổi (`bib_field_conflict`)
- **Thực tế:** Tác giả thường cập nhật thông tin bài báo tham khảo giữa các phiên bản (ví dụ $v_1$ ghi `year = 2017`, nhưng $v_2$ tác giả bổ sung thông tin chính thức đã đăng hội nghị và sửa thành `year = 2018`).
- **Giải pháp (TV4):** Thuật toán `unionize_bibtex` ưu tiên giữ lại giá trị xuất hiện ở phiên bản sớm nhất ($v_1$), đồng thời phát sinh cảnh báo có cấu trúc `bib_field_conflict` lưu vào `parsing_manifest.json` kèm chi tiết trường và giá trị xung đột để tiện cho việc kiểm tra chéo thủ công.

### 1.6. Phần tử Lặp lại Nhiều lần & Kiểm định Đa tập (Multiset Equivalence)
- **Thực tế:** Một câu văn ngắn hoặc một công thức toán (ví dụ: `E = mc^2` hay câu chuyển ý "See Table 1.") có thể xuất hiện nhiều lần ở các vị trí khác nhau dưới cùng một đề mục.
- **Thách thức:** Sau khi TV4 khử trùng lặp toàn văn, các lần xuất hiện này được gộp chung một `element_id`. Trong bảng `hierarchy.json`, điều này sinh ra nhiều dòng có cùng cặp `(element_id, parent_id)`. Các validator cây truyền thống giả định mỗi nút chỉ có 1 cạnh cha sẽ báo lỗi giả `multiple_parents`.
- **Giải pháp (TV4 & TV5 — PR #19):**
  - TV4 bảo toàn cấu trúc cây thật thông qua tệp `occurrences.json` (mỗi lần xuất hiện mang một `occurrence_id` duy nhất).
  - TV5 nâng cấp thuật toán kiểm định sang nguyên lý **Tương đương Đa tập (Multiset Equivalence)**: sử dụng `collections.Counter` đối chiếu chính xác số lần xuất hiện của từng cạnh:
    $$\text{Counter}(\text{occ\_edges}) == \text{Counter}(\text{hier\_edges})$$
    Cơ chế này vừa cho phép các phần tử lặp lại xuất hiện hợp lệ, vừa phát hiện chính xác bất kỳ cạnh thừa hoặc cạnh thiếu nào trong bảng `hierarchy.json`.

### 1.7. Lệch Snapshot Đầu vào & Ngăn ngừa Rò rỉ Dữ liệu Cũ (Snapshot Drift)
- **Thực tế:** Khi chạy lại pipeline trên một tập con ID (`--ids`) hoặc khi thư mục đầu vào MS1 được cập nhật snapshot mới, các tệp bảng từ lần chạy trước vẫn còn lưu trên đĩa tại `tables/`. Nếu validator hoặc benchmark quét đĩa thiếu chọn lọc, dữ liệu cũ sẽ bị cộng dồn sai lệch.
- **Giải pháp (TV5 — PR #19):**
  - Bắt buộc kiểm tra khớp nối snapshot kép: `manifest.input_snapshot_id == context.input_snapshot_id` (cả hai phải là chuỗi khác rỗng).
  - Thuật toán `generate_parsing_summary` chỉ tổng hợp số liệu trên các bài báo có `complete=True`, khớp mã định danh, và có snapshot trùng khớp với checkpoint `state/stages/deduplicate/<key>/paper.json`.

---

## 2. Quá trình Kiểm soát Chất lượng qua 11 Vấn đề Review (#1 đến #11)

Trong giai đoạn kiểm thử tích hợp cuối cùng, TV5 đã tiến hành rà soát mã nguồn và giải quyết triệt để 11 vấn đề kỹ thuật trọng yếu:

| # | Vấn đề Kỹ thuật Phát hiện | Nguyên nhân Gốc rễ | Giải pháp Kỹ thuật Triệt để Đã Áp dụng |
| :---: | :--- | :--- | :--- |
| **1** | **Báo nhầm `self_loop` trên bảng `hierarchy.json`** | Khử trùng lặp gộp các nút cùng `(kind, content)`, dẫn đến cạnh `element_id == parent_id` hợp lệ khi con trùng nội dung với cha. | Xóa bỏ hoàn toàn kiểm tra `child_id == parent_id` trên `hierarchy.json`. Chu trình chỉ được kiểm tra trên cây `occurrences.json`. |
| **2** | **Manifest `versions = [v1, v1]` vẫn vượt qua kiểm tra** | Validator cũ chỉ kiểm tra `len(manifest_versions) != len(expected_versions)`. | Kiểm tra nghiêm ngặt: danh sách `[v["version"] for v in versions] == expected_versions` (đủ 1..N, không trùng lặp) và `v["status"] in {"success", "no_source"}`. |
| **3** | **Bỏ qua kiểm tra khi thiếu `context.input_snapshot_id`** | Điều kiện `if input_snapshot_id is not None:` bỏ qua kiểm tra khi context bị thiếu trường này. | Bắt buộc cả context snapshot và manifest snapshot phải là `str` khác rỗng và bằng nhau 100%. |
| **4** | **`references.bib` sai khóa hoặc sai trường vẫn báo hợp lệ** | Validator cũ chỉ kiểm tra `st_size == 0`. | Sử dụng parser `parse_bib_text` phân tích cú pháp sâu, đối chiếu 1-1 từng trường chuẩn hóa với `bibtex.json`. |
| **5** | **Benchmark quét toàn bộ thư mục `tables/` và paper cũ** | Duyệt `for p_dir in tables_dir.iterdir():` gộp cả dữ liệu rác ngoài phạm vi cờ `--ids`. | Lọc danh sách bài báo từ `paper_outcomes` trong `manifests/parsing.json`, chỉ lấy bài `complete=True` khớp snapshot hiện tại. |
| **6** | **Thiếu khai báo `bibtex_file` và rác khi bibtex rỗng** | `bibtex_file` chưa nằm trong `REQUIRED_DEDUP_ARTIFACTS`. | Bắt buộc khai báo `bibtex_file`. Khi `bibtex.json` rỗng, `references.bib` bắt buộc phải rỗng (báo lỗi `unexpected_content_in_empty_bib`). |
| **7** | **Mất kiểm tra hàng dư trong `hierarchy.json` của version thiếu** | Vòng lặp đối chiếu multiset chỉ duyệt các version có trong manifest. | Chặn các hàng hierarchy thuộc version không có trong manifest; đối chiếu toàn cục `Counter(all_occ_edges) == Counter(all_hier_edges)` trên toàn bài. |
| **8** | **Bỏ sót nút `document` dư thừa hoặc làm nút con** | Thiếu ràng buộc danh tính cho các phần tử mang `kind == "document"`. | Bắt buộc tập phần tử `document` phải khớp 1-1 với `{prefix}root{v}` của các version `success`. Cấm tuyệt đối nút `document` làm nút con. |
| **9** | **Chưa kiểm tra `elements_before` và `bibtex_before`** | Chỉ kiểm tra `elements_after` và `bibtex_after`. | Bắt buộc `elements_before == sum(len(occurrences))`, `elements_before >= elements_after >= 0`, và `bibtex_before >= bibtex_after >= 0`. |
| **10** | **Kiểm tra schema lỏng và lọt cờ boolean `True/False`** | `elements` chưa kiểm tra set cột; vị trí `position` dùng `isinstance(pos, int)` (lọt kiểu `bool`). | Kiểm tra đúng tập khóa `EXPECTED_ELEMENT_KEYS`, đủ 9 cột `BibtexRow`, kiểm tra kiểu dữ liệu nghiêm ngặt `type(pos) is int` (chặn đứng `bool`). |
| **11** | **Toán tử `or` tạo số liệu giả khi giá trị thực bằng 0** | Dùng `total_assigned or 1`, `total_versions or total_assigned` gây gán số giả khi count bằng 0. | Chuyển sang kiểm tra rõ ràng `assigned_count = total_assigned if total_assigned is not None else ...`, bảo toàn giá trị 0 thực tế. |

---

## 3. Tính Sẵn sàng Chuyển tiếp sang Milestone 3 (Citation Matching)

Kiến trúc và bộ kiểm định của Milestone 2 được thiết kế nhằm đáp ứng các yêu cầu tiên quyết để chuyển tiếp sang Milestone 3 (Đối sánh và Dự đoán Thực thể Trích dẫn); kết quả chạy trên toàn bộ corpus đang chờ hoàn tất và kiểm chứng:

1. **Ngữ cảnh Trích dẫn Sạch & Chuẩn hóa (Standardized Citation Context):**
   - Mọi câu văn (`sentence`) chứa lệnh gọi trích dẫn `\cite{...}` đều đã được làm sạch triệt để các mã lệnh giao diện TeX, chuẩn hóa công thức toán học nội dòng, và đồng bộ hóa khóa trích dẫn về `chosen_key` duy nhất.
   - Điều này loại bỏ hoàn toàn nhiễu văn bản (noise), cung cấp đầu vào chất lượng cao cho các mô hình nhúng văn bản (Sentence Transformers) hoặc mô hình ngôn ngữ lớn (LLMs) trong bài toán Citation Intent Classification.
2. **Kho Dữ liệu Trích dẫn Thống nhất (Unified Target Catalog):**
   - Bảng `bibtex` đã được khử trùng lặp xuyên các phiên bản, hợp nhất thông tin giữa `\bibitem` viết tay và tệp `.bib`, loại bỏ hoàn toàn các bản ghi dư thừa.
   - Các trường khóa học thuật (`doi`, `title`, `authors`, `year`) đã được chuẩn hóa, sẵn sàng làm cơ sở dữ liệu đích (Ground Truth Target Catalog) cho các thuật toán đối sánh thực thể (Entity Matching & Resolution).
3. **Cấu trúc Cây Phân cấp Đa tầng (Multi-granularity Hierarchical Context):**
   - Bảng `hierarchy` cho phép mở rộng ngữ cảnh trích dẫn không chỉ giới hạn ở câu văn đơn lẻ mà có thể truy ngược lên đoạn văn (`prose_block`), tiểu mục (`subsection`), và chương mục chính (`section`).
   - Việc mở rộng cửa sổ ngữ cảnh theo cấu trúc cây là chìa khóa giúp nâng cao độ chính xác của các mô hình phân loại trích dẫn trong Milestone 3.
4. **Độ Bền vững & Khả năng Mở rộng (Scalable & Resilient Infrastructure):**
   - Kiến trúc đường ống có khả năng phục hồi (Resume) thông qua mã băm SHA-256 được thiết kế để vận hành trên toàn bộ corpus 25,000 bài báo; tính ổn định bộ nhớ và kết quả vận hành đủ 25,000 bài đang chờ kiểm chứng khi quá trình chạy hoàn tất.
