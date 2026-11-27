# Thảo luận và kết luận

## Kết quả của nhóm

Nhóm đã hoàn tất việc xử lý phạm vi 25.000 ID và chốt bộ corpus MS1. Kết quả gồm nguồn đa phiên bản, metadata, references và thông tin kiểm định để các bước tiếp theo nhận biết được chất lượng đầu vào. Tỷ lệ đạt validator của bộ đã chốt là 98,56%; các trạng thái còn lại được thống kê như đặc tính của corpus bàn giao.

Bao phủ Discovery phản ánh khả năng xác định bài báo và version. Mức hiện diện source và kết quả kiểm định đánh giá các tầng khác nhau: một bài có thể có nhiều version, một version có thể chỉ có PDF, và một paper có TeX vẫn có thể không đạt quy tắc metadata/references. Vì vậy không dùng một tỷ lệ duy nhất để thay tất cả mức độ thành công.

## Dung lượng và tài liệu tham khảo

Lọc ở bước giải nén giúp hình và tệp ngoài TeX/BibTeX không đi vào working corpus, trong khi lệnh LaTeX được giữ cho parsing. Thực nghiệm dung lượng dùng cùng tập ghép cặp trước/sau lọc để tránh so sánh sai gói nén với nội dung giải nén. Các giá trị trung bình là số đo trên tập được nêu, không ngoại suy cho các paper không có cặp đo.

References được lưu theo quan hệ bài trích dẫn và tài liệu được trích dẫn. Một tài liệu xuất hiện ở nhiều paper vẫn tạo nhiều quan hệ. Thiếu arXiv ID hoặc ngày công bố không tự chứng minh truy vấn thất bại; tiêu chí đủ năm trường là đánh giá mức đầy đủ metadata, không phải độ chính xác ngữ nghĩa. Số references đã ghi nhận không bao gồm phần chưa lấy được từ dịch vụ bên ngoài.

## Diễn giải hiệu năng

Checkpoint giúp sử dụng lại kết quả khi phiên Colab bị ngắt. Các số đo resume thể hiện chi phí kiểm tra cache và thực thi những bước cần xử lý trong phiên, không phải chi phí tải mới toàn bộ assignment. RAM có thể bỏ lỡ đỉnh ngắn giữa các lần lấy mẫu; quét thư mục trên Drive cũng tạo overhead. Do đó hiệu năng được đọc cùng phạm vi, số mẫu và chế độ chạy.

## Giá trị bàn giao

Corpus chốt giữ liên kết paper/version cùng trạng thái source, metadata và references. Các bản kiểm định giúp giai đoạn sau phân biệt paper có TeX, record không có source và đầu vào không đáp ứng đầy đủ hợp đồng. Validator kiểm tra cấu trúc, trạng thái và tính nhất quán tệp; không biên dịch LaTeX hay xác minh toàn bộ ngữ nghĩa khoa học.

MS1 cung cấp một nền dữ liệu có nguồn gốc và phạm vi kiểm chứng rõ ràng. Các giới hạn của dịch vụ ngoài, dạng submission và phép đo được trình bày ở cấp hệ thống, không quy thành mức hoàn thành của riêng một thành viên.
