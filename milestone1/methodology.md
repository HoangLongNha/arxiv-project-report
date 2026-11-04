# Phương pháp thu thập và xử lý

## Tổng quan hệ thống

Pipeline tích hợp sáu bước: **Discovery → Download → Extract → Metadata/References → Validation → Thống kê và báo cáo**. Metadata sử dụng lại thông tin Discovery; References được lấy từ Semantic Scholar. Checkpoint lưu kết quả từng bước để hỗ trợ chạy tiếp sau gián đoạn.

| Bước | Phương pháp | Đầu ra chính |
|---|---|---|
| Discovery | Chuẩn hóa ID, đọc arXiv Atom API, xác định và kiểm tra các version | Danh sách phiên bản và metadata ban đầu |
| Download | Tải source riêng từng version qua streaming, ghi tạm rồi hoàn tất nguyên tử | Source thô và thông tin tải |
| Extract | Kiểm tra đường dẫn archive, chỉ giữ TeX/BibTeX, không sửa nội dung | Corpus theo paper/version |
| Metadata | Chuẩn hóa dữ liệu Discovery và giữ thông tin riêng từng version | Metadata liên kết theo paper |
| References | Truy vấn Semantic Scholar, phân trang/batch khi phù hợp, chuẩn hóa và loại trùng | References và nguồn truy xuất |
| Validation | Đối chiếu định danh, version, checkpoint, đường dẫn và tệp dữ liệu | Kết quả kiểm định từng paper |

## Discovery và tải source

Hệ thống chấp nhận ID hoặc khoảng ID, chuẩn hóa định danh trước khi truy vấn. Discovery phân biệt ID không hợp lệ, không tìm thấy, lỗi API, lỗi dữ liệu và thành công. Phiên bản mới nhất cho biết số version cần kiểm tra; từng version được xác minh và tải qua endpoint source có hậu tố phiên bản.

Downloader sử dụng HTTP streaming để hạn chế bộ đệm, tính SHA-256 trong lúc tải, ghi vào tệp tạm và chỉ công nhận đầu ra sau khi tải hoàn tất. Phiên bản PDF-only hoặc không có source được ghi nhận riêng. Timeout, pacing và retry/backoff giúp xử lý lỗi mạng và giới hạn tần suất; HTTP 429 được xem là tín hiệu cần giảm tốc hoặc chờ thử lại.

## Tạo corpus và chuẩn hóa metadata

Extractor xử lý các dạng source được hỗ trợ như tar/gzip và TeX thuần. Đường dẫn thành viên archive được kiểm tra để tránh ghi ra ngoài thư mục đích. Chỉ các tệp `.tex` và `.bib` được đưa vào corpus. Việc loại hình không chỉnh sửa các lệnh trong nội dung LaTeX.

Metadata sử dụng lại Discovery để tránh truy vấn arXiv trùng lặp. Thông tin cấp paper và thông tin từng version được phân biệt; các trường tùy chọn thiếu được đánh dấu thay vì suy đoán giá trị.

## Thu thập references

Semantic Scholar cung cấp định danh và metadata tài liệu tham khảo. Client hỗ trợ batch, retry và phân trang để xử lý giới hạn API và danh sách dài. References được loại trùng theo định danh khi có; mục thiếu arXiv ID vẫn được giữ trong dữ liệu làm việc. Không có references, chưa được index và lỗi API là những kết quả khác nhau.

Một thí nghiệm references riêng được TV4 mô tả trong tài liệu bàn giao sử dụng dải tháng 08/2025. Đó là thí nghiệm của module, không phải kết quả assignment tháng 10/2024 của người chạy TV4, và không được cộng vào thống kê toàn nhóm ở phần kết quả này.

## Kiểm định và khả năng chạy tiếp

Validator đối chiếu số version, schema/định danh, đường dẫn tệp, raw source, corpus, metadata và references với checkpoint từng bước. Nó phát hiện dữ liệu thiếu, trạng thái không nhất quán và những tệp bị báo rỗng/nhị phân; một số nội dung trùng giữa các version chỉ là cảnh báo.

Chạy tiếp sử dụng checkpoint để tái dùng kết quả đã có. Vì vậy một lượt cuối chỉ xử lý vài ID không có nghĩa corpus cá nhân chỉ chứa vài paper. Ngược lại, exit code thành công của lượt cuối cũng không chứng minh toàn bộ corpus đã hợp lệ. Tiến độ lookup, kết quả thu thập và validation được đánh giá riêng.

## Công cụ chính

Python được dùng cho pipeline; arXiv API/Atom XML cho Discovery; `requests` và HTTP streaming cho tải nguồn; `tarfile`/`gzip` cho giải nén; Semantic Scholar API cho references; `psutil` và bộ đếm thời gian cho benchmark; pandas, matplotlib và Jupyter Book cho báo cáo. Chi tiết cài đặt và lệnh chạy nằm trong README của hai repository.
