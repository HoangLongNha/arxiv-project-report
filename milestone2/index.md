# Milestone 2 — Hierarchical Parsing & Standardization

Chương này trình bày toàn bộ kết quả phân tích cú pháp phân cấp, chuẩn hóa và khử trùng lặp dữ liệu LaTeX từ Corpus đã thu thập ở Milestone 1.

Các nội dung chính:
- **Mục tiêu & Giới thiệu luồng xử lý:** Kiến trúc 5 trạm xử lý song song từ file TeX gốc đến 3 bảng dữ liệu chuẩn hóa (`elements`, `hierarchy`, `bibtex`).
- **Phương pháp thực hiện:** Thuyết minh chi tiết các kỹ thuật giải quyết bài toán: đệ quy `\input`, phân tách cây phân cấp, chuẩn hóa toán & câu văn, trích xuất BibTeX và thuật toán khử trùng lặp 2 cấp độ.
- **Thống kê phân tích (Notebook thực thi):** Tự động sinh biểu đồ phân tích độ bao phủ và hiệu quả khử trùng lặp (`elements` và `bibtex`) ngay trong quá trình biên dịch sách (`jupyter-book build`).
- **Đo lường hiệu năng (Notebook thực thi):** Báo cáo thời gian chạy end-to-end, Peak RAM, Average RAM và dung lượng lưu trữ trên Google Colab CPU-only.
- **Thảo luận & Phân tích giới hạn:** Đánh giá các trường hợp biên (edge cases) và sự sẵn sàng cho Milestone 3.
