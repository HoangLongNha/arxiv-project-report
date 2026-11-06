# Thiết lập thực nghiệm và cách đánh giá

## Dữ liệu và môi trường

Mỗi thành viên xử lý dải 5.000 ID được phân công. Các phiên có thể bị gián đoạn rồi chạy tiếp từ checkpoint. Audit TV3 và TV4 được bổ sung ngày 04/11; báo cáo cập nhật các tệp này ngày 06/11/2026. Audit TV2 và TV5 vẫn là các bản đã nộp trước đó.

Môi trường benchmark theo đề bài là Google Colab CPU-only. Cấu hình, commit source, mốc thời gian và xác nhận CPU-only do từng run ghi lại được trình bày ở phụ lục. Các run có chế độ cache và phạm vi khác nhau, nên chưa dùng để xếp hạng tốc độ giữa thành viên.

## Tiến độ, kết quả và chất lượng

| Cấp đánh giá | Đơn vị và cách xác định |
|---|---|
| Tiến độ đầu vào | ID có record, ID chưa ghi nhận và lookup chưa giải quyết trên đúng dải 5.000 ID |
| Kết quả thu thập | Paper phát hiện được, version đã biết, source/corpus và metadata/references đã lưu |
| Chất lượng | Paper được kiểm định, số đạt/chưa đạt, loại lỗi và cảnh báo |

Một record lỗi cho biết ID đã được thử xử lý. Lookup chỉ được xem là giải quyết khi có kết quả thành công hoặc không tìm thấy hợp lệ. Cờ hoàn tất audit còn xét validation và diagnostics, nên được đọc riêng với tiến độ chạy ID.

## Thống kê corpus tích lũy

Thống kê toàn dải phải đọc checkpoint Discovery của mọi ID được giao, dùng manifest làm dữ liệu dự phòng khi không có checkpoint, rồi đối chiếu các stage và tệp hiện có. Mỗi paper được nhận diện bằng arXiv ID; source/corpus dùng cặp ID và version. References lấy từ tệp hiện hành của từng paper để tránh đếm lại qua các phiên.

Công cụ thống kê cũ chỉ chọn paper trong manifest của một lượt hoàn tất. Vì vậy một lượt resume sáu ID có thể tạo statistics sáu ID dù thư mục dữ liệu đã tích lũy gần đủ assignment. Bản thống kê mới có phạm vi riêng cho toàn dải và không mang nhãn benchmark của lượt cuối.

| Chỉ số | Mẫu số/phạm vi |
|---|---|
| Bao phủ đầu vào | ID có record / ID được giao |
| Discovery thành công | Paper phát hiện được / ID được giao của dải xét |
| Tải source | Version download thành công theo checkpoint; số có tệp thực tế được ghi riêng |
| Paper đủ source | Mọi version đã biết có source và corpus, theo quy tắc kiểm tra |
| Validation pass | Paper đạt / paper đã kiểm định; báo riêng paper chưa được kiểm định |
| Kích thước trước/sau lọc | Cùng tập paper có đủ cặp đo, cộng các version của từng paper |
| References trung bình | Tổng references / paper có kết quả truy vấn đọc được, gồm danh sách rỗng hợp lệ |
| Metadata references đầy đủ | References đủ trường / references đã đọc |

Giá trị thiếu không được thay bằng 0. Kích thước trước lọc lấy từ sidecar trích xuất; nếu sidecar không còn thì chưa tính được cặp đo. Thống kê đọc các báo cáo validation đã lưu; muốn kết luận về chất lượng hiện tại phải audit lại.

## Thời gian, RAM và dung lượng

Thời gian và RAM mô tả các phiên được đo. Khi tổng hợp, chỉ đếm mỗi run ID một lần; chi phí xử lý lại ID vẫn là thời gian đã sử dụng. Tổng thời gian hoạt động của các phiên khác với thời gian lịch có cả lúc nghỉ/ngắt máy. Số liệu từ một phần phiên chạy được ghi rõ là một phần lịch sử.

RAM gộp được tính từ các phiên có đủ mẫu, theo trọng số thời gian quan sát; peak là cực đại đã quan sát. Không thể khôi phục RAM hoặc runtime của phiên không có log từ corpus cuối. Final disk đo cả output root tại mốc kết thúc, có thể gồm dữ liệu tích lũy, raw source, corpus, checkpoint và sidecar. Nó không phải riêng kích thước corpus TeX/BibTeX.
