# Mục tiêu & Luồng xử lý dữ liệu

## 1. Bối cảnh và Mục tiêu

Tiếp nối kho dữ liệu sạch (**Clean Corpus**) từ Milestone 1, mục tiêu của Milestone 2 là xây dựng hệ thống phân tích cú pháp phân cấp và chuẩn hóa tự động (**Automated Hierarchical Parser & Standardizer**):
1. **Phân tích cú pháp phân cấp:** Chuyển đổi mã nguồn LaTeX thành cây phân cấp ngữ nghĩa (`Document` $\rightarrow$ `Section` $\rightarrow$ `Subsection` $\rightarrow$ `Paragraph` $\rightarrow$ `Sentence` / `Block Formula` / `Figure` / `Itemize`).
2. **Chuẩn hóa công thức và văn bản:** Đồng bộ công thức toán học nội dòng về `$...$` và toán khối về `\begin{equation}...\end{equation}`, loại bỏ định dạng hình thức thừa (`\centering`, `\small`, v.v.).
3. **Chuẩn hóa tài liệu tham khảo:** Trích xuất các khối `\bibitem` hoặc tệp `.bib` thành cấu trúc BibTeX chuẩn.
4. **Khử trùng lặp 2 cấp độ xuyên phiên bản (Cross-version Deduplication):**
   - *Cấp độ 1 (References):* Khử trùng lặp tài liệu tham khảo theo DOI/tiêu đề chuẩn hóa, hợp nhất trường thông tin và đổi tên đồng bộ các lệnh `\cite{}` trong toàn văn bài báo.
   - *Cấp độ 2 (Full-text Content):* Khử trùng lặp các phần tử có cùng loại (`kind`) và cùng nội dung văn bản (`content`) giữa các version, tái sử dụng `element_id` duy nhất trong bảng `elements`.
5. **Xuất bản 3 bảng dữ liệu chuẩn:** `elements`, `hierarchy`, và `bibtex` phục vụ cho bài toán Citation Matching ở Milestone 3.

## 2. Kiến trúc Luồng Dữ liệu 5 Trạm

Hệ thống được thiết kế theo mô hình luồng 5 trạm độc lập, giao tiếp thông qua hợp đồng dữ liệu bền vững (durable execution contract):

1. **Trạm 1 (TV1 — `resolver.py`):** Đệ quy lần theo `\documentclass`, `\input` và `\include` để ghép nối thân bài báo thành chuỗi TeX duy nhất; tách riêng khối `\begin{thebibliography}`.
2. **Trạm 2 (TV2 — `hierarchy.py`):** Xây dựng cây cú pháp phân cấp, trích xuất các khối cấu trúc, giữ lại `Acknowledgements` và `Appendices`, loại bỏ phần `References`.
3. **Trạm 3 (TV3 — `normalization.py`):** Làm sạch các lệnh định dạng thừa, chuẩn hóa công thức toán nội dòng/khối, phân tách các đoạn văn xuôi thành các câu văn lá (`Sentence`).
4. **Trạm 4 (TV4 — `bibliography.py` & `deduplication.py`):** Chuyển đổi `\bibitem` sang BibTeX chuẩn, thực hiện khử trùng lặp 2 cấp độ (References và Full-text) xuyên phiên bản, đồng bộ hóa khóa trích dẫn `\cite{}`.
5. **Trạm 5 (TV5 — `validation.py`, `benchmark.py` & Jupyter Book):** Kiểm định 100% tính toàn vẹn 3 bảng dữ liệu, đo lường hiệu năng trên môi trường Google Colab CPU-only và xuất bản báo cáo tương tác.
