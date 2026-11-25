# Thảo luận, Phân tích Trường hợp Biên & Sẵn sàng cho Milestone 3

Chương này đi sâu đánh giá các bài học kỹ thuật rút ra trong quá trình triển khai Milestone 2, phân tích cách giải quyết 7 nhóm ca biên (Edge Cases) phức tạp trên dữ liệu arXiv thực tế, tổng kết 11 vấn đề kiểm định chất lượng (QA Issues) đã khắc phục, và đánh giá tính sẵn sàng cho Milestone 3.

---

## 1. Phân tích Chi tiết 7 Nhóm Trường hợp Biên (Edge Cases)

Trong quá trình chạy thực tế trên các bài báo thật (như `2411.13795`, `2410.08024`, `2508.17481`, `2508.17871`, `2508.17740`), hệ thống đã phát hiện và xử lý triệt để các trường hợp dị thường:

### 1.1. Ấn phẩm chỉ có tệp PDF (PDF-only Publications)
- **Thực tế:** Trên tập thực nghiệm 25.000 bài báo (40.677 phiên bản), có **1.920 bài (`7,68%`)** ở cấp bài báo và **2.642 phiên bản (`6,50%`)** ở cấp phiên bản không cung cấp mã nguồn LaTeX gốc (chỉ có tệp PDF do tác giả nộp trực tiếp hoặc nguồn TeX không tồn tại trong gói tải arXiv).
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

## 3. Phân tích Thực nghiệm Nguyên nhân Chưa Hoàn chỉnh (6.759 bài — 27,04%) & Vai trò của Kiểm định QA

Kết quả chạy toàn bộ 25.000 bài báo (40.677 phiên bản) của cả 5 thành viên cho thấy đường ống có tính ổn định cao ở các tầng phân tích cây và chuẩn hóa: **Trạm 2 (`hierarchy`) và Trạm 3 (`normalize`) đạt 100% thành công (`30.313 / 30.313` phiên bản, 0 lỗi)** trên toàn bộ phiên bản qua được Trạm 1, và **Trạm 4B (`deduplicate`) đạt 100% thành công (`19.742 / 19.742` bài, 0 lỗi)** trên toàn bộ bài đủ điều kiện.

Toàn bộ **6.759 bài (`27,04%`)** có `complete = false` tập trung vào **3 nguyên nhân định lượng rõ ràng** (cộng thêm 1 ca timeout):

### 3.1. Lỗi tại Trạm 1 `resolve` — Rào cản lớn nhất (`7.482` phiên bản `data_error` + `240` phiên bản `skipped`)
Tổng cộng `7.722 / 40.677` phiên bản (`18,98%`) dừng lại ngay ở Trạm 1, kéo theo phần lớn trong số `5.257` bài bị bỏ qua ở bước `deduplicate`:
- **`missing_root` (`4.059` phiên bản):** Không tìm được tệp TeX gốc hợp lệ chứa `\documentclass` — phần lớn do ứng viên bị bộ kiểm tra cú pháp nghiêm ngặt từ chối (ví dụ điều kiện `\if...\fi` chưa đóng) hoặc gói mã nguồn chỉ chứa tệp mảnh không đầy đủ.
- **`unsupported_tex` (`1.027`), `unsupported_conditional` (`272`), `malformed_conditional` (`270`), `malformed_tex` (`506`):** Bài báo sử dụng lệnh biên dịch có điều kiện động, thay đổi `\catcode`, hoặc cú pháp `\verb` bất thường đòi hỏi trình biên dịch TeX đầy đủ thay vì phân tích tĩnh.
- **`unsupported_include` (`819`), `missing_include` (`311`), `dynamic_include` (`94`), `empty_include` (`22`):** Bài báo dùng `\input`/`\include` trỏ tới tệp không phải `.tex`/`.bib` (ví dụ `.pstex_t`, `.bbl`, `.tikz`), tệp thiếu trong archive hoặc đường dẫn ghép bằng macro động.
- **`ms1_upstream_not_successful` (`240` phiên bản):** Phiên bản có đầu vào từ Milestone 1 chưa đạt trạng thái thành công nên được giữ nguyên trạng thái `skipped` theo đúng nguyên tắc không xử lý dữ liệu thiếu.
- **`unsafe_path` (`4` phiên bản):** Cơ chế bảo mật `safe_path` đã chủ động chặn 4 phiên bản có đường dẫn tham chiếu vượt khỏi thư mục gốc.

### 3.2. Lỗi tại Trạm 4A `bibliography` (`411` phiên bản `data_error` — `1,01%`)
Trong số `30.313` phiên bản TeX đã giải mã thành công, chỉ có `411` phiên bản gặp `invalid_bibliography_input`:
- **Macro `@string` chưa định nghĩa (`295` phiên bản):** Các tệp `.bib` dùng viết tắt tháng hoặc tên tạp chí/hội nghị (như `jma`, `june`, `cvpr`, `lp`) không khai báo `@string` nội bộ, khiến parser nghiêm ngặt báo lỗi.
- **Khối BibTeX không đóng ngoặc (`115` phiên bản) và lỗi kiểu dữ liệu (`1` phiên bản):** Tệp `.bib` gốc của tác giả bị lỗi cú pháp ngoặc nhọn.

### 3.3. Từ chối từ Kiểm định QA Nghiêm ngặt `validate_parse` (`1.501` bài trên `19.742` bài đã deduplicate)
Trong `19.742` bài báo đã chạy xong `deduplicate` (`17.822` bài có TeX + `1.920` bài `no_source`), có **18.241 bài (`92,40%`)** vượt qua kiểm định QA và **1.501 bài (`7,60%`)** bị `validate_parse` từ chối:
- **Điểm sáng quan trọng:** Có **0 lỗi schema**, **0 lỗi khóa ngoại `hierarchy` ↔ `elements`**, **0 lỗi chu trình DAG / thứ tự `occurrences`**, và **0 lỗi khớp nối snapshot** trên toàn bộ 19.742 bài.
- **100% nguyên nhân của 1.501 ca từ chối QA đều nằm ở kiểm tra đối chiếu sâu 1-1 giữa `references.bib` và `bibtex.json`:**
  - Lệch trường `journal` (`644` bài), `url` (`571` bài), `title` (`64` bài), `authors` (`52` bài), `doi` (`6` bài), `year` (`3` bài) — chủ yếu do khác biệt khi thoát ký tự đặc biệt (`%`, `\^`, macro LaTeX hoặc khoảng trắng kép) trong quá trình xuất ra `.bib` rồi đọc ngược lại bằng `parse_bib_text`.
  - Lỗi đọc lại `references.bib` (`161` bài, gồm 159 lỗi `could not be parsed` và 2 lỗi unclosed BibTeX block).
- Việc bộ kiểm định QA chủ động gắn cờ `complete = false` thay vì bỏ qua cho thấy cơ chế kiểm soát chất lượng hoạt động đúng thiết kế; đồng thời chỉ rõ rằng chỉ cần chuẩn hóa nhất quán bộ serializer/escape cho `references.bib` là có thể thu hồi ngay phần lớn trong số **1.501 bài** này (nâng tỷ lệ hoàn chỉnh từ `72,96%` lên xấp xỉ `78,96%`).

### 3.4. Timeout và Các Bất thường Artifact Ghi nhận Minh bạch
- **Timeout 300 giây (`1` bài):** Bài `2506.19089` trong dải TV2 bị ngắt sau 300 giây (`skipped_timeout_papers.json`) để bảo vệ tiến độ batch; vì vậy `expected_versions` của TV2 ghi `7.981` (ít hơn 6 version so với cumulative MS1 là `7.987`) và tổng số bài qua Trạm 4B/5 là `24.999`.
- **Ảnh hưởng của số lượng phiên bản (All-or-Nothing Contract):** Do hợp đồng MS2 yêu cầu *mọi* phiên bản của bài báo đều phải hoàn tất thì bài báo mới đạt `complete = true`, tỷ lệ hoàn chỉnh giảm dần theo số phiên bản: bài 1 phiên bản đạt **76,63%** (`11.098 / 14.482`), 2 phiên bản đạt **69,85%** (`4.924 / 7.049`), 3 phiên bản đạt **65,42%** (`1.559 / 2.383`), và 4 phiên bản đạt **60,53%** (`434 / 717`).
- **Sai lệch siêu dữ liệu trong tệp `ms2_audit_summary.json` của TV3 và TV4:** Khi đối chiếu tệp audit phụ trợ trên Drive, nhóm phát hiện script xuất `audit_report/ms2_audit_summary.json` của TV3 và TV4 giữ nguyên trường nhãn `member = "tv2"` và `assigned_range = "2506.15788:2506.20787"` mặc dù số liệu đếm và mã SHA-256 bên trong đúng là của TV3 và TV4. Báo cáo toàn nhóm lấy nguồn gốc chuẩn từ `acceptance-config.json`, `summaries/parsing_summary.json`, `summaries/parse-run.json`, `manifests/stages.json` và `delivery.json` của từng thành viên, đồng thời ghi nhận rõ bất thường này để đảm bảo tính kiểm chứng.

---

## 4. Tính Sẵn sàng Chuyển tiếp sang Milestone 3 (Citation Matching) & Hạn chế Thực nghiệm

Với bộ kết quả thực nghiệm toàn nhóm đã xuất bản và kiểm chứng bằng SHA-256, Milestone 2 cung cấp nền tảng dữ liệu trực tiếp cho Milestone 3, kèm theo nhận diện rõ ràng các giới hạn hiện tại:

1. **Tập Dữ liệu Đạt chuẩn Sẵn sàng Sử dụng ngay (`18.241` bài báo — `72,96%`):**
   - **16.321 bài báo có mã nguồn TeX** đã được chuẩn hóa thành **6.576.538 phần tử nội dung** (`elements`) và **878.307 mục tài liệu tham khảo** (`bibtex`) không trùng lặp xuyên phiên bản, với **20.568** lượt `\cite{...}` được đồng bộ hóa về `chosen_key` duy nhất.
   - **1.920 bài báo `no_source`** được tách bạch rõ ràng, tránh làm nhiễu mẫu số của bài toán trích xuất ngữ cảnh trích dẫn ở Milestone 3.
2. **Ngữ cảnh Cây Phân cấp Đa tầng (`hierarchy`) & Đối sánh Trích dẫn (`bibtex`):**
   - Toàn bộ 18.241 bài đạt QA đảm bảo tính toàn vẹn khóa ngoại và cấu trúc cây không chu trình, cho phép Milestone 3 truy xuất ngữ cảnh trích dẫn từ cấp câu (`sentence`) mở rộng lên tiểu mục (`subsection`) và chương mục (`section`).
   - Bảng `bibtex` đã hợp nhất thông tin giữa `\bibitem` viết tay và `.bib`, chuẩn hóa các trường khóa (`doi`, `title`, `authors`, `year`) làm cơ sở dữ liệu đích cho bài toán Citation Matching.
3. **Độ Bền vững Hạ tầng & Giới hạn Phép đo Hiệu năng:**
   - **Bộ nhớ RAM ổn định đã được kiểm chứng thực tế trên 25.000 bài báo:** Trên cả 5 phiên chạy Google Colab CPU-only (12,67 GB RAM), Peak RAM nằm trong khoảng **920,60 MB – 3.561,79 MB** (dưới `27,5%` giới hạn hệ thống), không xảy ra tràn bộ nhớ (OOM). Tổng dung lượng 3 bảng đầu ra chưa nén của toàn nhóm là **3,68 GB** (`3.764,52 MB`) và 5 gói `MS2_RESULTS.zip` là **4,31 GB** (`4.412,34 MB`).
   - **Giới hạn đo thời gian chạy:** Do cả 5 thành viên chạy theo cơ chế phục hồi `resume=True` với số bài đã cache (`skipped_completed_papers`) khác nhau (từ `39` bài ở TV5 đến `3.586` bài ở TV3), thời gian chạy giữa các phiên (`3.211 s` đến `31.814 s`) không thể dùng để so sánh tốc độ giữa các thành viên hay thay thế một benchmark chạy mới (cold run) đồng nhất toàn 25.000 bài. Phiên TV5 (chỉ `39` bài cache, `4.961` bài pending, `~8,84 giờ` wall time) là mốc tham chiếu sát thực tế nhất cho chi phí xử lý đầy đủ một dải 5.000 bài trên Colab CPU-only.
4. **Hướng Cải tiến Ưu tiên nếu Thu hồi thêm Dữ liệu trước MS3:**
   - **Ưu tiên 1 (hiệu quả cao, chi phí thấp):** Chuẩn hóa cơ chế escape/serialize trong `references.bib` để khắc phục 1.501 bài bị từ chối round-trip QA.
   - **Ưu tiên 2:** Bổ sung bảng tra `@string` phổ biến cho `bibliography.py` (thu hồi tới 295 phiên bản) và nới lỏng xử lý các lệnh `\input` không phải `.tex` hoặc conditional đơn giản trong `resolver.py`.
