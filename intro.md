# Đồ án Khoa học Dữ liệu — arXiv Data Science Pipeline

**Nhóm 6 — Lớp Khoa học Dữ liệu**  
Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM

Nhóm xây dựng corpus source LaTeX theo phiên bản, metadata bài báo và tài liệu tham khảo để phục vụ parsing, deduplication và citation matching xuyên suốt đồ án.

---

## 1. Giới thiệu Tổng quan Đồ án

Đồ án môn học tập trung vào việc xây dựng đường ống khoa học dữ liệu toàn diện (End-to-End Data Science Pipeline) để thu thập, phân tích cú pháp phân cấp, chuẩn hóa, và khai phá tri thức từ kho lưu trữ ấn phẩm khoa học mở **arXiv**:

- **Milestone 1 — Data Collection, Crawling & Metadata Standardization:**  
  Thu thập mã nguồn TeX đa phiên bản, metadata, và danh mục tài liệu tham khảo từ arXiv API và Semantic Scholar; xây dựng cơ sở hạ tầng lưu trữ sạch (**Clean Corpus**) và cơ chế checkpoint phục hồi. Năm audit xác nhận đủ 25.000 ID và lookup thành công trên các dải được giao. Kiểm định ghi nhận paper chưa đạt; mức bao phủ Discovery được đọc riêng với mức hoàn thiện source và chất lượng. Dữ liệu TV1 đã được đối chiếu trực tiếp trên Drive (đủ 5.000 Discovery và 7.852 version).
- **Milestone 2 — Hierarchical Parsing, Normalization & Cross-version Deduplication:**  
  Phân tích cú pháp TeX đa file, xây dựng cây phân cấp ngữ nghĩa ($\text{Document} \rightarrow \text{Section} \rightarrow \text{Sentences} \mid \text{Formulas} \mid \text{Figures}$), chuẩn hóa biểu diễn toán học và văn bản, trích xuất BibTeX, khử trùng lặp 2 cấp độ xuyên phiên bản, và xuất bản 3 bảng dữ liệu quan hệ (`elements`, `hierarchy`, `bibtex`).
- **Milestone 3 — Citation Matching, Intent Classification & Knowledge Graph:**  
  Đối sánh thực thể trích dẫn, phân loại mục đích trích dẫn trong văn cảnh, và xây dựng đồ thị tri thức khoa học học thuật.

---

## 2. Bảng Phân công Trách nhiệm Thành viên

| Thành viên | MSSV | Vai trò chính trong Dự án | Trọng tâm Milestone 1 | Trọng tâm Milestone 2 |
| :--- | :--- | :--- | :--- | :--- |
| **TV1** | Đang cập nhật | Kiến trúc trưởng, Hợp đồng & Orchestrator | Thiết kế hệ thống, Hợp đồng MS1, Discovery, Crawler Orchestrator | Hợp đồng MS2, TeX Resolver đa file, Pipeline Orchestrator (`pipeline/parse.py`) |
| **TV2** | Đang cập nhật | Phân tích Cú pháp Phân cấp & Kỹ thuật Dữ liệu | Trích xuất Metadata arXiv, Thẩm định nguồn TeX | Bộ phân tích cây phân cấp (`hierarchy.py`), Ngăn xếp thứ bậc tiêu đề, Nhận diện tiêu đề PRL |
| **TV3** | 24120318 | Chuẩn hóa Văn bản, Toán học & Xử lý Ngôn ngữ | Semantic Scholar API Client, Làm sạch dữ liệu tác giả | Chuẩn hóa văn bản TeX đa tầng (`normalization.py`), Masking toán học tức thời, Phân đoạn câu |
| **TV4** | Đang cập nhật | Trích xuất Trích dẫn & Khử trùng lặp Xuyên phiên bản | Trích xuất References thô, Hợp nhất metadata | Bộ trích xuất BibTeX (`bibliography.py`), Khử trùng lặp 2 cấp độ & Đổi tên `\cite{}` (`deduplication.py`) |
| **TV5** | 24120330 | Thẩm định Chất lượng (QA Lead) & Hiệu năng | Thẩm định chất lượng MS1, Giám sát tài nguyên phần cứng | Động cơ kiểm định QA MS2 (`validation.py`), Khung Benchmark (`benchmark.py`), Báo cáo Jupyter Book |

---

## 3. Cấu trúc Tài liệu Báo cáo

Trang web báo cáo được tổ chức thành các chương mục logic:
1. [**Milestone 1 — Thu thập Dữ liệu & Trích xuất Metadata**](milestone1/index.md): Báo cáo chi tiết quá trình thu thập 25.000 bài báo, kiểm tra tính toàn vẹn và đo lường tài nguyên.
2. [**Milestone 2 — Phân tích Cú pháp Phân cấp & Khử trùng lặp**](milestone2/index.md): Báo cáo chi tiết đường ống 5 trạm phân tích cú pháp phân cấp, chuẩn hóa và khử trùng lặp dữ liệu TeX.
   - [Mục tiêu & Luồng xử lý Dữ liệu](milestone2/introduction.md)
   - [Phương pháp Triển khai & Hợp đồng Kỹ thuật](milestone2/methodology.md)
   - [Thống kê Phân tích Thực nghiệm (Notebook)](milestone2/statistics.ipynb)
   - [Đo lường Hiệu năng Thực thi (Notebook)](milestone2/performance.ipynb)
   - [Thảo luận, Phân tích Trường hợp Biên & Sẵn sàng cho MS3](milestone2/discussion.md)
3. [**Nguồn tham khảo**](references.md): Danh mục tài liệu kỹ thuật, API và đặc tả đề tài.

---

## 4. Liên kết Dự án & Mã nguồn

- [Báo cáo Milestone 1](milestone1/index.md)
- [Báo cáo Milestone 2](milestone2/index.md)
- **Mã nguồn pipeline chính (Source Code):** [GitHub: LeoTkiet/arxiv-data-science](https://github.com/LeoTkiet/arxiv-data-science)
- **Repository báo cáo (Report Repository):** [GitHub: HoangLongNha/arxiv-project-report](https://github.com/HoangLongNha/arxiv-project-report)
- **Đề bài & Quy định chính thức:** [HCMUS CS Lab Book — Project Statements](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/)
