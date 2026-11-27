# Mục tiêu và phạm vi

MS1 chuyển các dải arXiv ID được giao thành corpus có thể dùng cho parsing và matching. Mỗi paper được nhận diện bằng arXiv ID; mọi version phát hiện được được xử lý riêng để giữ lịch sử chỉnh sửa.

Ba nhiệm vụ chính là xác định bài báo và phiên bản, tải source đầy đủ rồi giữ TeX/BibTeX, và lấy metadata tài liệu tham khảo qua Semantic Scholar. Việc lọc bỏ hình thực hiện ở bước giải nén; nội dung LaTeX và các lệnh hình được giữ nguyên.

Toàn bộ nhóm dùng chung schema, CLI và cơ chế checkpoint. Năm dải 5.000 ID được xử lý độc lập rồi tổng hợp theo định danh; một paper không bị đếm thêm chỉ vì đã chạy qua nhiều phiên. Corpus đã chốt được mô tả bằng kết quả thực tế, gồm cả PDF-only và các trường hợp chưa đáp ứng mọi quy tắc kiểm định.

Theo [đề bài MS1](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/crawling/), báo cáo phân tích số paper thu thập, tỷ lệ thành công, kích thước trước/sau lọc, references và hiệu năng. Các bảng và biểu đồ được tính từ artifacts khi biên dịch Jupyter Book.
