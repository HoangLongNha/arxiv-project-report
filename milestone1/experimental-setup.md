# Thiết lập thực nghiệm và cách đánh giá

## Thiết kế thực nghiệm

Mỗi thành viên chạy cùng pipeline tích hợp trên dải 5.000 ID cá nhân. Theo thông tin nhóm cung cấp, các thành viên đã chạy hết dải và sử dụng notebook benchmark mới nhất. Tiến độ do nhóm xác nhận được trình bày riêng với mức kiểm chứng từ các tệp kết quả đã nộp.

Bộ bằng chứng hiện đọc được gồm ZIP của TV2, TV3, TV5, bản TV4 đã lưu và hai ZIP phiên TV4 bổ sung ngày 04/11/2026. Các phiên bổ sung có số đo hiệu năng nhưng chưa có thống kê snapshot hoàn tất. Ngày nộp ZIP không nhất thiết là ngày chạy; danh sách nguồn và thời điểm từng phiên được ghi ở phụ lục.

## Ba cấp đánh giá

| Cấp | Câu hỏi | Cách đánh giá |
|---|---|---|
| Tiến độ đầu vào | Đã chạy qua hết 5.000 ID chưa? | Đối chiếu dải, số ID có record, số chưa ghi nhận và lookup còn lỗi |
| Kết quả thu thập | Thu được bao nhiêu paper/version/source/references? | Thống kê dữ liệu trên phạm vi cụ thể, phân biệt thành công, không có source và lỗi |
| Chất lượng | Đầu ra có phù hợp quy tắc kiểm định không? | Số paper đã kiểm định, pass/fail, nhóm lỗi và cảnh báo |

Một ID có record lỗi đã được thử xử lý nhưng chưa có kết quả lookup được giải quyết. Validation fail không làm mất việc ID đã được thử xử lý. Cờ hoàn tất audit trong source còn xét validation/diagnostics, nên không dùng riêng cờ đó để kết luận tiến độ chạy ID.

## Chỉ số và mẫu số

| Chỉ số | Mẫu số/phạm vi |
|---|---|
| Bao phủ đầu vào | Số ID có record / số ID được giao, trên đúng dải |
| Discovery thành công | Số paper phát hiện được / số ID đầu vào của phạm vi xét |
| Tải source thành công | Số version tải thành công / số version đã biết |
| Validation pass | Số paper đạt / số paper đã được kiểm định; báo riêng paper chưa kiểm định |
| Kích thước trước/sau lọc | Cùng tập paper có đủ cặp đo; cộng các version của từng paper |
| References trung bình | Các paper truy vấn được, gồm kết quả rỗng hợp lệ; không gán lỗi API bằng 0 |
| Tỷ lệ metadata references đầy đủ | Số reference đủ trường / tổng số reference đã đọc |

## Đo hiệu năng

Môi trường benchmark cuối theo đề bài là Google Colab CPU-only. Báo cáo giữ thông tin môi trường thực tế do từng run ghi nhận. Thời gian được đo cho pipeline và từng event; RAM được lấy mẫu trên cây tiến trình; disk là logical bytes trong output root, gồm dữ liệu/checkpoint và tệp tạm thuộc phạm vi đo.

Mỗi phép đo phải được đọc cùng phạm vi, chế độ chạy mới/chạy tiếp, dữ liệu cache, số mẫu và trạng thái kết thúc. Không cộng thời gian các run chồng lặp, không lấy số đo phiên resume cuối làm tổng thời gian nhiều phiên. RAM trung bình chỉ diễn giải khi có đủ khoảng lấy mẫu; đỉnh là cực đại quan sát được.

## Quy tắc tổng hợp

Chỉ cộng dữ liệu giữa những dải không giao nhau sau khi xác minh định danh và phạm vi. Audit toàn dải và statistics của một run ngắn là hai góc nhìn của cùng dữ liệu, không phải hai tập paper độc lập. Giá trị thiếu được ghi rõ là chưa đủ bằng chứng; tỷ lệ không có mẫu số được coi là không áp dụng. Các mẫu demo/smoke lịch sử không được cộng vào kết quả thu thập thật.
