# Báo cáo Triển khai Module Normalization (TV3) — Milestone 2

- **Người thực hiện:** Trịnh Văn Hợp (MSSV: 24120318)
- **Vai trò:** Thành viên 3 (TV3) — Nhóm 6
- **Module phụ trách:** `src/arxiv_pipeline/parsing/normalization.py`
- **Bộ kiểm thử:** `tests/parsing/test_normalization.py`
- **Các Pull Requests đã merge vào main:**
  - **PR #13:** `feat(ms2): implement text normalization and sentence splitting module (TV3)` (commits: `3c50dc8`, `0184274`, `8ee411e`, `5c49458`, `27fc109`).
  - **PR #16:** `fix(ms2): unwrap color wrappers and strip maketitle in normalization (TV3)` (commit: `bbadda2`).

---

## 1. Mục tiêu và Vai trò trong Pipeline Milestone 2

Trong kiến trúc xử lý của Milestone 2, module **Normalization (TV3)** đóng vai trò làm cầu nối chuyển tiếp giữa **Hierarchy Construction (TV2)** và **Deduplication / Tabular Export (TV4)**:
1. Tiếp nhận cây phân cấp sơ bộ (`raw_tree.json`) từ checkpoint của TV2 (`stage="hierarchy"`).
2. Chuẩn hóa hình thức các công thức toán học (inline & block math).
3. Loại bỏ toàn bộ các mã lệnh trình bày, định dạng giao diện LaTeX (`\maketitle`, `\centering`, `\textcolor`, v.v.) mà không làm biến dạng nội dung ngữ nghĩa hay mất trích dẫn / công thức toán.
4. Phân đoạn các khối văn xuôi (`prose_block`) thành các câu đơn lẻ (`sentence`) thông qua cơ chế Token Masking bảo vệ ngữ cảnh.
5. Chuyển đổi và tái lập chỉ mục vị trí (`position: 0, 1, 2...`) của các node con, sắp xếp toàn bộ cây theo đúng thứ tự duyệt tiền thứ tự (**Preorder Traversal**).
6. Đóng gói kết quả đầu ra theo phong bì chuẩn `StageResult` schema v2.0 tại `parsed/<paper_key>/vN/normalized_tree.json`.

---

## 2. Các tính năng kỹ thuật cốt lõi đã triển khai

### 2.1. Chuẩn hóa công thức toán (Math Normalization)
- **Inline Math (`normalize_inline_math`):**
  - Đồng nhất các cú pháp toán nội dòng `\(...\)` và `\begin{math}...\end{math}` về định dạng tiêu chuẩn `$ ... $`.
  - Chuẩn hóa khoảng trắng bên trong dấu đô-la (ví dụ: `$  x + y  $` $\rightarrow$ `$x + y$`).
- **Block Math (`normalize_block_math`):**
  - Đồng nhất các dạng khối toán độc lập (`$$...$$`, `\[...\]`, `\begin{align*}`, `\begin{gather}`, `\begin{multline}`, v.v.) về khối chuẩn:
    ```latex
    \begin{equation}
    <nội_dung_toán_sạch>
    \end{equation}
    ```
  - Làm sạch các dòng trống và khoảng trắng thừa bên trong khối phương trình.

### 2.2. Làm sạch mã trình bày LaTeX (LaTeX Cleanup Pipeline)
Quy trình làm sạch được thiết kế nhiều tầng nghiêm ngặt nhằm tránh làm hỏng công thức toán:
1. **Bảo vệ toán học tức thời (Immediate Math Masking):**
   - Trước khi thực hiện bất kỳ thao tác thay thế văn bản nào, toàn bộ công thức toán (khối `\begin{equation}...`, display math `$$...$$`, `\[...\]`, inline math `$ ... $`) được bóc tách và thay thế bằng các token marker thuộc vùng ký tự riêng (*Private Use Area*: `0xE000 - 0xF8FF`).
   - Việc dùng tiền tố marker động đảm bảo không bao giờ xảy ra xung đột với chuỗi ký tự có sẵn trong bài báo gốc.
2. **Loại bỏ tham số vị trí & lệnh dàn trang (Layout & Placement):**
   - Loại bỏ placement options: `\begin{figure}[htpb]` $\rightarrow$ `\begin{figure}`.
   - Loại bỏ lệnh bố cục: `\centering`, `\raggedright`, `\noindent`, `\newpage`, `\clearpage`, `\vspace`, `\hspace`, `\setlength`.
   - Bổ sung khử triệt để: `\maketitle` (kể cả `\maketitle{}`, `\maketitle[...]`), `\tableofcontents`, `\protect`.
3. **Loại bỏ quy tắc kẻ bảng & chuyển đổi kích thước chữ:**
   - Xóa các đường kẻ bảng: `\toprule`, `\midrule`, `\bottomrule`, `\hline`, `\cline`, `\cmidrule`.
   - Xóa các lệnh chỉnh kích cỡ và kiểu font switch: `\small`, `\large`, `\bfseries`, `\itshape`, `\normalfont`, v.v.
4. **Bóc vỏ wrapper màu & định dạng chữ đa tầng (Color & Style Unwrapping):**
   - Xây dựng parser cân bằng ngoặc nhọn `_extract_balanced_brace` có xử lý escape parity (phân biệt chính xác giữa `\{` là ký tự ngoặc thường với `\\{` là dấu xuống dòng đi kèm mở ngoặc).
   - Triển khai `_strip_color_wrappers`: Bóc tách màu sắc của `\textcolor[model]{specs}{content}`, `\textcolor{color}{content}`, `\colorbox`, `\fcolorbox`, chỉ giữ lại phần `content`.
   - Loại bỏ các lệnh đổi màu dạng khai báo: `\color{...}`, `\pagecolor{...}`, `\normalcolor`.
   - Áp dụng vòng lặp hội tụ cố định (*Fixed-point Iteration* `while prev != text`) luân phiên giữa `_strip_color_wrappers` và `_strip_text_styles` (`\textbf`, `\textit`, `\emph`, `\underline`, `\texttt`, `\textsf`, `\textrm`, `\textnormal`, v.v.), giải quyết triệt để các cấu trúc lồng nhau tùy ý (ví dụ: `\textcolor[rgb]{...}{\textbf{Introduction.---}}` $\rightarrow$ `Introduction.---`).
5. **Chuẩn hóa dấu câu & ký tự đặc biệt:**
   - Thay thế dấu nháy trích dẫn LaTeX bên ngoài toán học: ` `` ` và ` '' ` thành `"`, ` ` ` và ` ' ` thành `'`.
   - Chuyển đổi dấu ngã liên kết không ngắt dòng `~` thành khoảng trắng thường.
   - Giải mã unescape các ký tự thoát: `\%`, `\&`, `\_`, `\#`, `\{`, `\}` $\rightarrow$ `%`, `&`, `_`, `#`, `{`, `}`.
6. **Khôi phục biểu thức toán học (Math Restoration):**
   - Khôi phục các token toán học theo thứ tự đảo ngược (*reverse order*), bảo toàn nguyên vẹn mọi ký hiệu đạo hàm cấp cao như $f''(x)$ hay toán lồng nhau.

### 2.3. Phân đoạn câu bảo vệ ngữ cảnh (Sentence Segmentation)
Hàm `split_into_sentences` giải quyết bài toán phân chia câu trong tài liệu khoa học mà không làm gãy câu sai vị trí:
- **Bảo vệ các thực thể bằng Token Masking:**
  - URL (http, https, ftp) và địa chỉ Email.
  - Các lệnh trích dẫn học thuật: `\cite{...}`, `\citep{...}`, `\citet{...}`, `\citeauthor{...}`, `\nocite{...}`, v.v.
  - Số thập phân và số phiên bản: `3.14`, `v1.0`, `1.2.3`.
  - Danh mục chữ viết tắt khoa học thông dụng: `e.g.`, `i.e.`, `et al.`, `cf.`, `vs.`, `Fig.`, `Eq.`, `Ref.`, `Sec.`, `Dr.`, `Prof.`, v.v.
  - Tên tác giả viết tắt: `A. Smith` (có cơ chế phân biệt để không mask nhầm các danh từ đếm như `Sentence A.`, `Theorem 1.`).
- **Phân tách câu chính xác:**
  - Nhận diện ranh giới kết thúc câu bằng Regex look-behind: `[.!?]` theo sau bởi khoảng trắng và một ký tự viết hoa hoặc token hợp lệ.
  - Hoàn nguyên các token và loại bỏ khoảng trắng rỗng.

### 2.4. Chuyển đổi cây và đảm bảo cấu trúc Preorder (Tree Transformation)
- Hàm `transform_tree_to_normalized`:
  - Kiểm tra tính duy nhất của Document Root, ngăn chặn cây có chu trình hoặc đa gốc.
  - Node `prose_block` được phân rã thành các node con có `kind="sentence"` gắn vào cùng `parent_temp_id`, sinh mã định danh duy nhất (`s1`, `s2`,...).
  - Các node khác (`heading`, `figure`, `block_formula`, `itemize`, `item`) được chuẩn hóa `raw_content` $\rightarrow$ `cleaned_content`.
  - Đánh lại chỉ số `position` của các con trực thuộc cùng một cha từ `0` đến `n-1` liên tục.
  - Thực hiện thuật toán duyệt cây theo thứ tự trước (Preorder Traversal: Document $\rightarrow$ Section $\rightarrow$ Sentences/Leaves), đảm bảo tương thích 100% với yêu cầu của TV4 Deduplication.

### 2.5. Adapter tích hợp Pipeline v2.0 (`run`)
- Kiểm tra nghiêm ngặt tính toàn vẹn danh tính của checkpoint `hierarchy` (đúng `paper_id`, `version`, `schema_version="2.0"`, `nodes` là một mảng hợp lệ).
- Xử lý nhất quán trường hợp `no_source` (bảo đảm phiên bản không có mã nguồn TeX không bị ép thành cây có dữ liệu giả mạo).
- Sử dụng hàm `atomic_json` ghi an toàn file `normalized_tree.json`.
- Trả về đối tượng `StageResult` hoàn chỉnh, cung cấp fingerprint phục vụ cơ chế `--resume` của Orchestrator.

---

## 3. Quá trình gỡ lỗi và hoàn thiện qua các đợt Review

Trong quá trình thực nghiệm và kiểm tra chéo với dữ liệu bài báo thực tế (`2411.13795` và `2410.08024`), TV3 đã chủ động phát hiện và khắc phục các vấn đề sau:

| Vấn đề phát hiện | Nguyên nhân gốc rễ | Giải pháp kỹ thuật đã áp dụng | Commit / PR |
| :--- | :--- | :--- | :--- |
| Mất ký hiệu đạo hàm toán học: `$f''(x)$` biến thành `$f"(x)$` | Lệnh replace quote `''` $\rightarrow$ `"` chạy trước khi mask công thức toán | Đưa bước Masking toán học lên vị trí ưu tiên số 1 ngay sau khi chuẩn hóa inline math | `0184274` (PR #13) |
| Lọt công thức toán nằm trong figure (`\begin{equation}` trong `figure`) | Bộ lọc chỉ mask `$...$` và `$$...$$`, bỏ sót môi trường block math lồng | Xây dựng `_BLOCK_MATH_ENV_RE` bao quát toàn bộ môi trường toán học amsmath | `8ee411e` (PR #13) |
| Checkpoint Hierarchy sai version vẫn được chấp nhận | Adapter chỉ kiểm tra sự tồn tại của key `hierarchy` mà chưa đối chiếu bộ định danh | Bổ sung kiểm tra tuple định danh đầy đủ: `(stage, paper_id, version, schema_version)` | `0184274` (PR #13) |
| Va chạm placeholder khi văn bản có sẵn `__MATH_0__` | Dùng tiền tố cố định dễ trùng với chuỗi literal trong bài báo về LaTeX | Chuyển sang sinh tiền tố động bằng dải ký tự Private Use Area `_token_prefix` | `27fc109` (PR #13) |
| Khôi phục lỗi khi toán lồng nhau | Khôi phục token theo thứ tự xuôi làm hỏng các token con | Khôi phục token theo thứ tự ngược (*reverse order*) | `5c49458` (PR #13) |
| Bài báo `2411.13795` còn sót `\maketitle` và `\textcolor[rgb]` trong bảng `elements.json` | Bộ lọc chưa hỗ trợ lệnh `\maketitle` và wrapper màu với tham số `[rgb]` | Bổ sung `_LAYOUT_COMMANDS_RE`, xây dựng parser `_extract_balanced_brace` bóc vỏ `\textcolor` | `bbadda2` (PR #16) |
| Heading định dạng `textcolor + textbf` bị rác | Chưa phối hợp bóc vỏ sạch sẽ giữa style chữ và màu | Tạo vòng lặp lặp lại hội tụ khử triệt để mọi tầng lồng nhau giữa color và text style | `bbadda2` (PR #16) |

---

## 4. Kết quả Kiểm thử và Nghiệm thu

Bộ test của TV3 tại `tests/parsing/test_normalization.py` đã đạt độ bao phủ toàn diện:
- **Tổng số ca kiểm thử:** **48 / 48 tests passed** (thời gian chạy ~0.7s).
- **Các nhóm bài test chính:**
  1. *Math Normalization:* 5 tests (inline dollar, cleanup spaces, double dollar, bracket `\[ \]`, align/gather environments).
  2. *LaTeX Cleanup:* 6 tests (layout/tables, text styles, preservation of math/citations, unescaping, quotes, deeply nested styles).
  3. *Sentence Splitting:* 3 tests (basic punctuation, abbreviations/numbers, citations/URLs).
  4. *Tree Transformation:* 6 tests (prose replacement, re-indexing, duplicate root detection, cycle detection, empty prose blocks, figure math preservation).
  5. *Adapter & Checkpoint Contract:* 8 tests (success execution, no_source handling, missing hierarchy, identity mismatch, missing nodes, contradiction handling).
  6. *Placeholder Collision & Subprocess Security:* 6 tests (literal markers survival, subprocess execution timeout boundaries).
  7. *TV3 Regression Suite (PR #16):* 7 tests (stripping `\maketitle`, unwrapping `\textcolor[rgb]`, multi-level nesting, math/citations inside color, colorbox/declarations, heading & prose cleanup).
  8. *End-to-end Integration Test:* 1 test tích hợp trực tiếp **TV2 $\rightarrow$ TV3 $\rightarrow$ TV4**, xác nhận bảng `elements.json` và `hierarchy.json` hoàn toàn sạch mã trình bày và đạt kiểm định `_preorder`.

- **Tích hợp liên module:**
  - Vượt qua toàn bộ **9/9 tests** của `tests/parsing/test_ms2_contracts.py`.
  - Vượt qua toàn bộ **32/32 tests** của `tests/pipeline/test_parse.py`.
  - Toàn bộ suite liên module (Resolver + Hierarchy + Normalization + Contracts + Pipeline) đạt **169 passed, 1 skipped**.
  - Kiểm tra cú pháp và định dạng: `git diff --check` đạt **0 errors**.

---

## 5. Kết luận

Phần công việc của **TV3 (Trịnh Văn Hợp)** trong Milestone 2 đã hoàn thành 100% khối lượng theo hợp đồng phân công nhóm (`docs/MS2_CONTRACTS.md` và `docs/MS2_HANDOFF.md`), khắc phục triệt để các tồn đọng kỹ thuật trên dữ liệu thực tế, sẵn sàng cho việc nghiệm thu toàn bộ pipeline trên toàn corpus.

