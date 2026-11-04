# Phương pháp triển khai & Hợp đồng Dữ liệu

## 1. Phương pháp Kỹ thuật 5 Trạm

### Trạm 1: Ghép nối mã nguồn TeX đa file (`resolver.py`)
Mã nguồn của một bài báo trên arXiv thường được chia nhỏ thành nhiều file `.tex`. Trạm 1 thực hiện:
- Định vị file `.tex` chính chứa lệnh `\documentclass`.
- Đệ quy lần theo các lệnh `\input{...}` và `\include{...}` để ghép nối thành một luồng văn bản duy nhất. Bỏ qua các dòng chú thích `%` và các tệp nháp không nằm trong luồng biên dịch chính.
- Tách riêng môi trường `\begin{thebibliography}...\end{thebibliography}` và định vị các tệp `.bib` đi kèm.

### Trạm 2: Xây dựng Cây phân cấp Ngữ nghĩa (`hierarchy.py`)
Trạm 2 phân tích cú pháp TeX theo cấu trúc ngữ nghĩa phân cấp:
- Phân cấp tiêu đề: `\section` (rank 1) $\rightarrow$ `\subsection` (rank 2) $\rightarrow$ `\subsubsection` (rank 3) $\rightarrow$ `\paragraph`.
- Giữ lại phần `Acknowledgements` và các phần phụ lục `Appendices` (`\section*`), loại bỏ phần `References` hoặc `Bibliography`.
- Nhận diện và tách các khối đặc biệt: `figure`, `table`, `itemize/enumerate`, và các công thức toán khối (`equation`, `align`, `gather`, `$$...$$`).

### Trạm 3: Làm sạch, Chuẩn hóa Toán & Tách Câu (`normalization.py`)
- **Làm sạch định dạng:** Loại bỏ các lệnh định dạng trực quan không mang ý nghĩa ngữ nghĩa (như `\centering`, `\small`, `\vspace`, `[htpb]`, `\midrule`, v.v.).
- **Chuẩn hóa công thức:**
  - Toán nội dòng: Đồng bộ các dạng `\(...\)` về dạng chuẩn `$...$`.
  - Toán khối: Đồng bộ các dạng `\[...\]`, `$$...$$`, `align`, `gather` về dạng chuẩn `\begin{equation}...\end{equation}`.
- **Tách câu văn (`Sentence`):** Phân chia các đoạn văn xuôi thành các câu văn lá dựa trên dấu chấm kết câu, bảo vệ các ngoại lệ không cắt nhầm:
  - Công thức toán nội dòng `$...$`.
  - Từ viết tắt phổ biến: `e.g.`, `i.e.`, `et al.`, `Fig.`, `Tab.`, `vs.`, `Ref.`.
  - Số thập phân (e.g., `3.14`) và đường dẫn URL.

### Trạm 4: Trích xuất BibTeX & Khử trùng lặp Xuyên phiên bản (`deduplication.py`)
- **Cấp độ 1 (Khử trùng lặp Tài liệu tham khảo):**
  - Chuyển đổi các mục `\bibitem` thành cấu trúc BibTeX chuẩn.
  - So khớp các mục trích dẫn xuyên các phiên bản dựa trên DOI chuẩn hóa, tiêu đề chuẩn hóa (loại bỏ dấu câu và khoảng trắng thừa), hoặc citation key.
  - Hợp nhất (union) các trường thông tin về một `chosen_key` duy nhất (chọn key xuất hiện sớm nhất).
  - Đổi tên đồng bộ toàn bộ các lệnh trích dẫn trong văn bản (ví dụ: `\cite{old_key}` $\rightarrow$ `\cite{chosen_key}`).
- **Cấp độ 2 (Khử trùng lặp Toàn văn):**
  - Sau khi các lệnh `\cite{}` đã được đồng bộ, các phần tử có cùng loại (`kind`) và cùng nội dung (`content`) chính xác giữa các version sẽ được gán cùng một `element_id` duy nhất trong bảng `elements`.
  - Mối quan hệ phân cấp cha-con theo từng phiên bản được ghi nhận trong bảng `hierarchy`.

### Trạm 5: Thẩm định Chất lượng, Đo lường & Báo cáo (`validation.py` & `benchmark.py`)
- **Validator (`validation.py`):** Kiểm tra tính toàn vẹn schema, ràng buộc khóa ngoại giữa 3 bảng, cấu trúc cây phân cấp (không chu trình, mỗi version có duy nhất 1 nút root `#root{version}` làm tổ tiên), loại bỏ hoàn toàn tiêu đề References, và không trùng lặp `(kind, content)`.
- **Benchmark Harness (`benchmark.py`):** Đo đạc runtime, Peak RAM thông qua luồng nền lấy mẫu `psutil` mỗi 0.2 giây, dung lượng ổ đĩa 3 bảng đầu ra, và xuất tệp `summaries/parsing_summary.json`.

---

## 2. Hợp đồng 3 Bảng Dữ liệu Đầu ra

Theo đặc tả của môn học, kết quả xử lý được tổ chức thành 3 bảng:

### Bảng `elements`
Lưu trữ các phần tử nội dung độc nhất xuyên suốt các version của bài báo:
- `element_id` (str): Khóa chính duy nhất (ví dụ: `2310-12345#root1`, `2310-12345#s1`).
- `arxiv_id` (str): Mã định danh bài báo gốc (ví dụ: `2310.12345`).
- `kind` (str): Loại phần tử, thuộc tập: `{"document", "heading", "itemize", "item", "sentence", "block_formula", "figure"}`.
- `content` (str): Nội dung đã làm sạch, chuẩn hóa toán và đồng bộ khóa `\cite{}`.

### Bảng `hierarchy`
Lưu trữ các cạnh quan hệ cha - con theo từng phiên bản (đúng 4 cột theo quy định):
- `arxiv_id` (str): Mã định danh bài báo.
- `version` (int): Số thứ tự phiên bản ($\ge 1$).
- `element_id` (str): Khóa ngoại tham chiếu `elements.element_id`.
- `parent_id` (str): Khóa ngoại tham chiếu `elements.element_id` của nút cha.

### Bảng `bibtex`
Danh mục tài liệu tham khảo sau khi khử trùng lặp và hợp nhất thông tin:
- `arxiv_id` (str): Mã bài báo gốc.
- `citation_key` (str): Khóa trích dẫn đại diện duy nhất (`chosen_key`).
- `entry_type` (str): Loại ấn phẩm (`article`, `inproceedings`, `book`, `misc`, v.v.).
- `title` (str): Tiêu đề tài liệu tham khảo.
- `authors` (list[str]): Danh sách tên các tác giả.
- `year` (int | None): Năm xuất bản.
- `doi`, `journal`, `url` (str | None): Các trường tùy chọn nếu có.
