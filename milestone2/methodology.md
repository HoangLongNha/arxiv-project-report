# Phương pháp Triển khai & Hợp đồng Kỹ thuật

Chương này trình bày chi tiết cơ sở lý thuyết, thuật toán cốt lõi, và các quyết định kỹ thuật của toàn bộ 5 giai đoạn trong đường ống Milestone 2, kết hợp kết quả đóng góp của cả 5 thành viên (TV1 – TV5).

---

## 1. Trạm 1: Ghép nối Mã nguồn TeX Đa file & Điều phối Đường ống (TV1)

### 1.1. Bóc tách và Khử dòng chú thích (Comment Stripping)
Trong LaTeX, ký tự `%` dùng để bắt đầu dòng chú thích, ngoại trừ trường hợp đã được thoát (escape) bằng dấu gạch chéo ngược `\%`. Resolver sử dụng biểu thức chính quy với kiểm tra chẵn-lẻ dấu gạch chéo ngược để loại bỏ chính xác phần chú thích mà không làm mất các ký hiệu phần trăm toán học hoặc tỷ lệ trong bài báo:
$$\text{regex: } (?<!\\)(?:\\\\)*%$$
Các khối mã trong môi trường nguyên tử như `\begin{verbatim}...\end{verbatim}` được bảo vệ nguyên vẹn nội dung.

### 1.2. Định vị Tệp Gốc & Đệ quy Ghép nối Đường dẫn Biên dịch (Include Resolver)
Các bài báo khoa học thường phân mảnh thành nhiều tệp `.tex` trong các thư mục con. Trạm 1 thực hiện:
- **Định vị tệp TeX chính (Master Document):** Tìm tệp chứa bộ ba chỉ thị `\documentclass`, `\begin{document}` và `\end{document}`. Trường hợp có nhiều tệp ứng viên, thuật toán áp dụng cơ chế chọn lọc xác định (deterministic selection) dựa trên độ sâu thư mục và cảnh báo `ambiguous_root`.
- **Duyệt đệ quy cây tệp (Recursive Inclusion via Call Stack):**
  - Mở rộng các lệnh `\input{path}` và `\include{path}`.
  - Quản lý ngăn xếp đệ quy (Call Stack DFS) theo nhánh đang duyệt để phát hiện và ngăn chặn triệt để vòng lặp bao hàm vô tận (`infinite include loop`), đồng thời vẫn cho phép một tệp được gọi hợp lệ nhiều lần ở các nhánh độc lập.
  - **Bảo mật đường dẫn (`safe_path`):** Chặn đứng mọi nỗ lực tham chiếu tệp thoát khỏi thư mục gốc của phiên bản (`../` hoặc đường dẫn tuyệt đối).
- **Phân tách Preamble và Thân bài:** Trích xuất phần khai báo Preamble (từ đầu tệp đến trước `\begin{document}`) lưu riêng vào ngữ cảnh, bàn giao chuỗi `merged_body_tex` sạch cho Trạm 2.

### 1.3. Tách Tài liệu Tham khảo & Bảo vệ Phụ lục (Bibliography Separation)
- Trích xuất toàn bộ khối môi trường `\begin{thebibliography}...\end{thebibliography}` thành danh sách `raw_bibitems`.
- Định vị các tệp `.bib` được khai báo trong lệnh `\bibliography{...}` cũng như toàn bộ kho tệp `.bib` có sẵn trong thư mục.
- **Bảo vệ Phụ lục và Lời cảm ơn:** Thuật toán cắt bỏ khối References nhưng bảo toàn nguyên vẹn mọi nội dung nằm sau phần tham khảo như `\section*{Appendix}` hay `\section*{Acknowledgements}`.

### 1.4. Bộ Điều phối Đường ống (Pipeline Orchestrator — `pipeline/parse.py`)
- Quản lý luồng thực thi 2 tầng: tầng phiên bản (`Resolver` $\rightarrow$ `Hierarchy` $\rightarrow$ `Normalization` và `Resolver` $\rightarrow$ `Bibliography`) và tầng bài báo (`Deduplication` $\rightarrow$ `Validation`).
- Hỗ trợ CLI chuẩn hóa: `python main.py --stage parse --ms1-input <dir> --output <dir> [--ids ...] [--resume] [--force]`.
- Quản lý checkpoint bằng mã băm SHA-256 (Dependency Fingerprints). Khi chạy với `--resume`, hệ thống kiểm tra sự thay đổi của mã nguồn và dữ liệu để bỏ qua các bước đã hoàn tất, đảm bảo khả năng mở rộng trên tập dữ liệu lớn.

---

## 2. Trạm 2: Phân tích Cấu trúc Phân cấp Ngữ nghĩa (TV2)

```text
merged_body_tex
      │
      ▼
┌──────────────────────────────────────────────┐
│ Quét Tiêu đề có che chắn khối nguyên tử      │
└──────────────┬───────────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌──────────────────────────────────────────────┐
│ Ngăn xếp    │ │ Bóc tách nút lá                              │
│ thứ bậc     │ │ (figure, table, block_formula, prose_block)  │
│ rank 1..7   │ └──────────────────────┬───────────────────────┘
└──────┬──────┘                        │
       │                               │
       └───────────────┬───────────────┘
                       ▼
       ┌───────────────────────────────┐
       │ Cây sơ bộ: raw_tree.json      │
       │ (Envelope Schema 2.0)         │
       └───────────────────────────────┘
```

### 2.1. Quản lý Thứ bậc Tiêu đề bằng Ngăn xếp (Stack-based Heading Hierarchy)
Để xây dựng cây phân cấp từ luồng văn bản tuần tự, TV2 áp dụng thuật toán ngăn xếp động với bảng trọng số thứ bậc LaTeX:
$$\text{part (1)} < \text{chapter (2)} < \text{section (3)} < \text{subsection (4)} < \text{subsubsection (5)} < \text{paragraph (6)} < \text{subparagraph (7)}$$

- **Nguyên lý hoạt động:**
  - Ngăn xếp lưu trữ các bộ ba `(rank, node_id, is_excluded)`. Nút gốc tài liệu `vN_root` có $\text{rank} = 0$.
  - Khi gặp tiêu đề mới có thứ bậc $r_{\text{new}}$: Lùi (pop) ngăn xếp chừng nào đỉnh ngăn xếp có $\text{top.rank} \ge r_{\text{new}}$. Đỉnh ngăn xếp còn lại sau khi lùi chính là **nút cha trực tiếp** (`parent_temp_id`).
  - Đẩy tiêu đề mới vào ngăn xếp.
- **Xử lý nhảy cấp độ (Level Jumping):** Xử lý tự nhiên các trường hợp bài báo nhảy từ `\section` (rank 3) thẳng xuống `\subsubsection` (rank 5) mà không làm gãy cấu trúc cây. Độ phức tạp thuật toán đạt $\mathcal{O}(N)$ tuyến tính theo số lượng phần tử.

### 2.2. Nhận diện Tiêu đề Định dạng có Kiểm soát (Controlled Formatted Headings — PR #17)
- **Vấn đề thực tiễn:** Nhiều bài báo thuộc trường phái *Physical Review Letters (PRL)* (ví dụ bài báo `2411.13795`) không sử dụng lệnh `\section` truyền thống mà định dạng tiêu đề bằng màu sắc và in đậm, ví dụ:
  ```latex
  \textcolor[rgb]{0.00,0.00,1.00}{\textbf{Introduction.---}}
  ```
- **Quy tắc kiểm soát chống nhận diện nhầm:**
  1. Hỗ trợ cấu trúc lồng nhau: `\textcolor` bọc ngoài `\textbf` hoặc ngược lại, kèm tiền tố `\noindent` tùy chọn.
  2. **Ranh giới đoạn văn (Bắt buộc):** Tiêu đề phải bắt đầu ở đầu đoạn văn (ngay sau `\n\n`, `\par`, hoặc `\maketitle`). Mọi cụm từ in đậm/đổi màu nằm giữa câu văn xuôi đều bị loại bỏ.
  3. **Ràng buộc độ dài:** Độ dài tiêu đề $\le 150$ ký tự và không chứa dòng trống ngắt đoạn.
  4. **Quy chuẩn cấp bậc:** Gán `heading_rank = 3` (tương đương `\section`) để thiết lập nút cha cho các đoạn văn xuôi bên dưới.

### 2.3. Bóc tách Nút lá & Bảo vệ Khối Nguyên tử
- **Che chắn tiêu đề giả (Heading Shielding):** Tự động bỏ qua các lệnh tiêu đề nằm trong chú thích hình ảnh, bảng biểu hoặc môi trường mã nguồn (`verbatim`, `lstlisting`, `minted`).
- **Danh sách lồng nhau đa cấp (Nested Lists):** Máy trạng thái theo dõi độ sâu môi trường `env_depth` để phân rã chính xác các mục `\item` ở cấp 0 mà không làm vỡ các danh sách con lồng bên trong.
- **Phân loại nút lá:**
  - `figure`: Bao gồm hình ảnh (`figure`) và bảng biểu (`table`, `tabular`, `longtable`), tự động bóc vỏ các khối căn lề (`center`, `minipage`).
  - `block_formula`: Các phương trình toán khối `$$...$$`, `\[...\]` (sử dụng negative lookbehind `(?<!\\)\\\[` để tránh nhầm với ngắt dòng bảng `\\[2pt]`), `align`, `gather`, `equation`.
  - `prose_block`: Các khối văn xuôi cách nhau bởi dòng trống, chuyển giao cho Trạm 3 phân đoạn thành câu.

---

## 3. Trạm 3: Chuẩn hóa Văn bản & Phân đoạn Câu (TV3)

Trạm 3 đảm nhận vai trò cầu nối chuyển tiếp từ cây cú pháp thô sang cây đối tượng chuẩn hóa ngữ nghĩa (`normalized_tree.json`).

```text
raw_tree.json
      │
      ▼
┌────────────────────────────────────────────────────────┐
│ 1. Masking Toán học tức thời                           │
│    (Private Use Area: 0xE000 - 0xF8FF)                 │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Loại bỏ Layout, Bố cục & Kẻ bảng                    │
│    (\maketitle, \centering, \toprule, \hline, v.v.)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Bóc vỏ Màu sắc & Kiểu chữ Lồng nhau Đa tầng         │
│    (Fixed-point Iteration: \textcolor, \textbf, v.v.)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. Chuẩn hóa Dấu câu & Giải mã Ký tự Thoát             │
│    (LaTeX quotes, ~, \%, \&, \_, \#, \{, \})           │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 5. Khôi phục Biểu thức Toán học theo Thứ tự Ngược      │
│    (Reverse Order Restoration: f''(x) preservation)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 6. Phân đoạn Câu văn lá Bảo vệ Ngữ cảnh                │
│    (Token Masking: URLs, \cite, e.g., i.e., A. Smith)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 7. Sắp xếp Cây theo Thứ tự Duyệt Trước (Preorder)      │
│    (position: 0, 1, 2... liên tục 0..n-1)              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
normalized_tree.json (Envelope Schema 2.0)
```

### 3.1. Quy trình Làm sạch TeX Đa tầng (LaTeX Cleanup Pipeline)
1. **Bảo vệ Toán học Tức thời (Immediate Math Masking):**
   - Trước khi thực hiện bất kỳ phép thay thế nào, toàn bộ công thức toán (inline `$ ... $`, `\( ... \)`, display `$$ ... $$`, `\[ ... \]`, `align`, `gather`) được bóc tách và thay bằng các token marker thuộc vùng ký tự riêng của Unicode (**Private Use Area**: `0xE000 - 0xF8FF`).
   - Việc sinh tiền tố marker động đảm bảo không bao giờ trùng lặp với các ký tự có sẵn trong bài báo gốc.
2. **Loại bỏ Lệnh Dàn trang & Mã Trình bày:**
   - Xóa bỏ tùy chọn căn vị trí: `\begin{figure}[htpb]` $\rightarrow$ `\begin{figure}`.
   - Loại bỏ các lệnh định dạng giao diện: `\centering`, `\raggedright`, `\noindent`, `\newpage`, `\vspace`, `\hspace`.
   - Khử triệt để các khối tiêu đề trang bìa: `\maketitle` (kể cả `\maketitle[...]`), `\tableofcontents`, `\protect`.
3. **Loại bỏ Đường kẻ Bảng & Lệnh Chuyển Font:**
   - Xóa các đường kẻ bảng của booktabs/tabular: `\toprule`, `\midrule`, `\bottomrule`, `\hline`, `\cline`.
   - Xóa các lệnh chuyển kích cỡ và kiểu font: `\small`, `\large`, `\bfseries`, `\itshape`, `\normalfont`.
4. **Bóc vỏ Màu sắc & Kiểu chữ Lồng nhau Đa tầng (Style & Color Unwrapping):**
   - Xây dựng parser cân bằng ngoặc `_extract_balanced_brace` có xử lý chẵn-lẻ dấu escape (phân biệt chính xác giữa `\{` là ký tự ngoặc thường với `\\{` là xuống dòng kèm mở ngoặc).
   - Bóc vỏ `\textcolor[model]{specs}{content}` và `\textcolor{color}{content}`, chỉ giữ lại phần nội dung `content`.
   - Áp dụng thuật toán lặp hội tụ cố định (**Fixed-point Iteration** `while prev != text`) luân phiên giữa bóc màu và bóc font (`\textbf`, `\textit`, `\emph`, `\underline`), giải quyết triệt để các cấu trúc lồng nhau tùy ý (ví dụ: `\textcolor[rgb]{...}{\textbf{Introduction.---}}` $\rightarrow$ `Introduction.---`).
5. **Chuẩn hóa Dấu câu & Ký tự Đặc biệt:**
   - Đổi dấu nháy kép LaTeX: ` `` ` và ` '' ` $\rightarrow$ `"`, ` ` ` và ` ' ` $\rightarrow$ `'`.
   - Dấu ngã liên kết `~` $\rightarrow$ khoảng trắng.
   - Giải mã các ký tự thoát: `\%`, `\&`, `\_`, `\#`, `\{`, `\}` $\rightarrow$ `%`, `&`, `_`, `#`, `{`, `}`.
6. **Khôi phục Toán học theo Thứ tự Ngược (Reverse-order Math Restoration):**
   - Khôi phục các token toán học theo thứ tự đảo ngược, bảo toàn nguyên vẹn các ký hiệu đạo hàm cấp cao như $f''(x)$ hay toán lồng nhau mà không bị ảnh hưởng bởi bước chuyển đổi dấu nháy.

### 3.2. Chuẩn hóa Công thức Toán học
- **Inline Math:** Đồng nhất các dạng `\(...\)` và `\begin{math}` về định dạng `$ ... $`, chuẩn hóa khoảng trắng bên trong.
- **Block Math:** Đồng nhất các dạng `$$...$$`, `\[...\]`, `align`, `gather` về định dạng chuẩn:
  ```latex
  \begin{equation}
  <nội_dung_toán_sạch>
  \end{equation}
  ```

### 3.3. Phân đoạn Câu Bảo vệ Ngữ cảnh (Context-preserving Sentence Segmentation)
Hàm `split_into_sentences` giải quyết bài toán cắt câu trong văn bản khoa học thông qua cơ chế bảo vệ thực thể:
- **Token Masking:** Thay thế tạm thời các cấu trúc chứa dấu chấm nhưng không phải kết thúc câu:
  - Địa chỉ URL và Email.
  - Các lệnh viện dẫn trích dẫn: `\cite{...}`, `\citep{...}`, `\citet{...}`.
  - Số thập phân và số hiệu phiên bản: `3.14`, `v1.0`.
  - Danh mục chữ viết tắt khoa học: `e.g.`, `i.e.`, `et al.`, `cf.`, `vs.`, `Fig.`, `Eq.`, `Sec.`, `Ref.`.
  - Tên tác giả viết tắt: `A. Smith` (có cơ chế phân biệt để không mask nhầm danh từ đếm như `Sentence A.`).
- **Phân tách câu:** Nhận diện ranh giới câu bằng Regex look-behind `[.!?]\s+[A-Z]`, sau đó khôi phục lại các token đã mask.

### 3.4. Chuyển đổi Cây & Sắp xếp Preorder Traversal
- Nút `prose_block` được phân rã thành các nút con có `kind="sentence"`.
- Đánh lại chỉ số `position` liên tục từ $0 \dots n-1$ cho các con trực thuộc cùng một cha.
- Sắp xếp toàn bộ cây theo đúng thứ tự duyệt tiền thứ tự (**Preorder Traversal**: Gốc $\rightarrow$ Section $\rightarrow$ Sentences/Leaves), đảm bảo các nút cha luôn xuất hiện trước nút con, tương thích hoàn toàn với Trạm 4.

---

## 4. Trạm 4: Trích xuất BibTeX & Khử trùng lặp Xuyên phiên bản (TV4)

### 4.1. Stage `bibliography`: Trích xuất Tài liệu Tham khảo
- **Từ `\bibitem` viết tay (`parse_bibitem`):**
  - Trích xuất `citation_key`, `doi`, `url`.
  - `year`: Lấy năm 4 chữ số (18xx–20xx) cuối cùng **sau khi đã loại bỏ chuỗi mã số arXiv** (ví dụ: chuỗi `2010.11929` không bị bắt nhầm thành năm 2010).
  - Tách `title`, `authors`, `journal` theo cấu trúc `\newblock` hoặc chuỗi trong ngoặc kép. Tên tác giả dạng `Last, First` được giữ nguyên cặp.
  - Quy ước: `entry_type` luôn đặt là `misc` cho `\bibitem` viết tay (không tự ý đoán là `article`).
  - Bản ghi gốc được lưu vào `raw_bibtex.provenance.json`.
- **Từ tệp `.bib` đi kèm (`parse_bib_text`):** Sử dụng thư viện `bibtexparser`, chuẩn hóa tên tác giả thành `First Last`, chuẩn hóa DOI và ép kiểu năm xuất bản thành số nguyên.

### 4.2. Stage `deduplicate` — Cấp 1: Khử trùng lặp Tài liệu Tham khảo & Đổi tên Trích dẫn
- **Tiêu chí Hợp nhất (Union-Find trên 3 tín hiệu):**
  1. Cùng `citation_key` giữa các phiên bản.
  2. Cùng mã số `doi` (sau khi chuẩn hóa bỏ tiền tố URL và chuyển về chữ thường).
  3. Cùng tiêu đề chuẩn hóa (loại bỏ lệnh LaTeX, dấu câu, chữ thường) **với điều kiện độ dài $\ge 15$ ký tự** (ngăn chặn gộp nhầm các tiêu đề quá ngắn như "Survey" hay "Introduction").
- **Chọn Khóa Đại diện & Hợp nhất Trường:**
  - Khóa đại diện (`chosen_key`) là khóa xuất hiện sớm nhất theo thứ tự phiên bản tăng dần ($v_1 < v_2$).
  - Bổ khuyết thông tin: trường nào của bản ghi trước bị trống thì được điền từ bản ghi sau. Loại ấn phẩm cụ thể (ví dụ `article`, `book`) được ưu tiên hơn `misc`.
  - Nếu xảy ra xung đột giá trị trường giữa hai phiên bản, hệ thống giữ lại giá trị xuất hiện sớm nhất và ghi nhận cảnh báo `bib_field_conflict` vào manifest.
- **Đổi tên Trích dẫn Đồng bộ (`rename_citations`):**
  - Quét toàn bộ cây văn bản, đổi tên mọi biến thể lệnh `\cite{...}`, `\citep{...}`, `\citet{...}`, `\citeauthor{...}`, `\nocite{...}` về khóa đại diện `chosen_key`.
  - **Thứ tự thực hiện:** Bước đổi tên này **bắt buộc phải thực hiện trước** khi so sánh nội dung văn bản ở Cấp 2, giúp hai câu văn ở hai phiên bản trở nên hoàn toàn giống nhau về mặt chuỗi ký tự.

### 4.3. Stage `deduplicate` — Cấp 2: Khử trùng lặp Nội dung Toàn văn & Xuất Bảng
- **Định danh Phần tử Toàn cục (`element_id`):**
  - Mọi phần tử (ngoại trừ nút gốc `document`) có cùng cặp `(kind, cleaned_content)` trên toàn bộ các phiên bản của bài báo được gán chung một `element_id`.
  - Quy ước cấu trúc mã: `<paper_key>#<tiền_tố><số>` (ví dụ `2310-12345#s1`, `2310-12345#h1`, `2310-12345#eq1`). Nút gốc tài liệu mang mã riêng theo phiên bản: `2310-12345#root1`, `2310-12345#root2`.
- **Bảng `hierarchy.json` & Lưu vết `occurrences.json`:**
  - Bảng `hierarchy` ghi nhận quan hệ cha - con theo đúng 4 cột: `(arxiv_id, version, element_id, parent_id)`.
  - Để giải quyết trường hợp một câu lặp lại nhiều lần dưới cùng một tiêu đề (sinh nhiều hàng có cùng `element_id` và `parent_id`), TV4 xuất bổ sung tệp `parsed/<key>/vN/occurrences.json` lưu trữ cấu trúc cây chính xác theo từng lần xuất hiện (`occurrence_id`, `position`).

---

## 5. Trạm 5: Thẩm định Chất lượng, Đo lường & Báo cáo (TV5)

### 5.1. Động cơ Kiểm định Chất lượng Nghiêm ngặt (QA Validation Engine)
Validator của TV5 đóng vai trò chốt chặn kiểm soát chất lượng độc lập, thực thi các tiêu chuẩn kiểm thử khắt khe:

1. **Toàn vẹn Schema & Khóa Ngoại:**
   - Bảng `elements.json` phải đúng 4 cột, `kind` hợp lệ, cấm tuyệt đối tiêu đề `References`/`Bibliography`.
   - Bảng `hierarchy.json` phải đúng 4 cột, 100% `element_id` và `parent_id` phải tồn tại trong bảng `elements`. Cấm nút gốc `document` làm nút con.
   - Bảng `bibtex.json` phải đúng 9 cột, `title` bắt buộc là chuỗi ký tự, `authors` là mảng chuỗi.
2. **Khớp nối Snapshot Tuyệt đối (Snapshot Alignment):**
   - Bắt buộc `manifest.input_snapshot_id == context.input_snapshot_id` và cả hai phải là chuỗi khác rỗng.
3. **Kiểm định Cây Occurrences & Không Chu trình (DAG Integrity):**
   - Nút gốc duy nhất `parent_occurrence_id = None` có `position = 0`.
   - Thuật toán dò chu trình theo nhánh tổ tiên đảm bảo không có vòng lặp phụ thuộc.
   - Chỉ số `position` phải là số nguyên (`type(pos) is int`, chặn đứng cờ boolean `True/False`) và liên tục liên tiếp $0, 1, \dots, k-1$.
4. **Đối chiếu Đa tập Toàn vẹn (Multiset Equivalence Check):**
   - Đối chiếu số lượng và cặp cạnh chính xác giữa `occurrences` và `hierarchy` qua cấu trúc `Counter(occ_edges) == Counter(hier_edges)` trên từng phiên bản và trên toàn cục, cho phép các phần tử lặp lại xuất hiện hợp lệ mà không bị báo lỗi giả `multiple_parents`.
5. **Đối chiếu Chuyên sâu `references.bib` và `bibtex.json`:**
   - Dùng `parse_bib_text` phân tích cú pháp của `references.bib`, đối chiếu 1-1 từng trường thông tin (`title`, `authors`, `year`, `doi`, `journal`, `url`) với `bibtex.json`. Nếu bảng rỗng thì tệp `.bib` bắt buộc phải rỗng.
6. **Đồng bộ Khóa Trích dẫn:** Kiểm tra toàn bộ khóa được gọi trong `\cite{...}` ở các câu văn phải tồn tại trong danh mục `bibtex.json` hoặc đã được ghi nhận trong danh sách cảnh báo `warnings`.

### 5.2. Khung Đo lường Hiệu năng Thực nghiệm (Performance Profiling Harness)
- **Giám sát Bộ nhớ Nền (`MemorySampler`):** Khởi tạo tiến trình tiểu luồng (Thread) lấy mẫu định kỳ mỗi $0.2\text{ giây}$ ghi nhận lượng RAM thực tế (Resident Set Size - RSS) của tiến trình chính cùng toàn bộ các tiến trình con (`psutil`).
- **Thời gian Thực thi Độ chính xác cao:** Đo lường Wall Time bằng `time.perf_counter()`.
- **Lọc Phạm vi Báo cáo theo Snapshot:** Chỉ tổng hợp số liệu trên các bài báo có trạng thái `complete=True`, khớp mã định danh và snapshot hiện tại, ngăn ngừa việc cộng dồn các tệp rác còn sót lại từ các lần chạy trước.
- **Không sử dụng Số liệu Giả mạo (Zero Synthetic Defaults):** Loại bỏ toàn bộ các hằng số mặc định giả định, xử lý an toàn các trường hợp phép chia cho 0 khi số lượng phân công bằng 0.
