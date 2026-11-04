# Thảo luận, hạn chế và kết luận

## Tiến độ và kết quả đạt được

Nhóm đã xây dựng pipeline tích hợp để tìm phiên bản, tải source, tạo corpus TeX/BibTeX, chuẩn hóa metadata, lấy references và kiểm định đầu ra. Theo tổng hợp tiến độ do nhóm cung cấp, năm thành viên đã chạy hết dải 5.000 ID/người. Phần kết quả ghi nhận tiến độ này và tách rõ số liệu đối chiếu được từ artifacts.

Trong bộ bằng chứng hiện có, audit TV2 và TV5 ghi nhận đủ 5.000 ID đúng dải. Điều này xác nhận việc xử lý đầu vào ở hai dải, đồng thời không bảo đảm tất cả lookup và đầu ra đều thành công. TV3/TV4 có thống kê của các lượt resume, nhưng chưa có kết quả audit toàn dải trong các ZIP đã đọc; chưa đủ cơ sở công bố chỉ số cuối cùng cho toàn bộ 25.000 ID.

## Chất lượng và nguyên nhân chưa đạt

Các lỗi kiểm định tập trung vào stage upstream chưa thành công, đường dẫn/tệp đầu ra và sự nhất quán của checkpoint. Các nhóm lỗi có thể cùng xuất hiện ở một paper. Cần phân biệt dữ liệu thực sự thiếu với checkpoint cũ hoặc quy tắc kiểm định chưa phù hợp; không thể kết luận toàn bộ paper validation fail đều không có dữ liệu sử dụng được.

Audit TV2 ghi cờ hoàn tất không khớp số paper fail theo công thức tại commit được benchmark khai báo. Đây là vấn đề cần tái kiểm ở báo cáo audit; không phủ nhận việc file đó liệt kê đủ 5.000 ID. TV5 vẫn có bốn lookup lỗi và các paper validation fail trong snapshot đã nộp. Các con số này mô tả trạng thái tại ngày audit, chưa khẳng định trạng thái của corpus sau những lần sửa/chạy tiếp chưa được xuất artifacts.

## Hiệu năng và giới hạn đo

Các run được nộp có phạm vi khác nhau và đều dùng chạy tiếp. Số đo chịu ảnh hưởng của cache, retry, thời gian chờ dịch vụ và quét file trên Drive. Những yếu tố này giải thích vì sao không dùng bảng benchmark hiện tại để xếp hạng tốc độ giữa thành viên hoặc ngoại suy tổng thời gian toàn nhóm. Các phiên TV4 bổ sung có nhiều mẫu hơn nhưng bị gián đoạn và chồng lặp phạm vi, nên vẫn được trình bày riêng.

Lấy mẫu RAM có thể bỏ lỡ đỉnh ngắn; RSS cộng tiến trình có thể đếm shared pages nhiều lần. Disk chỉ đo trong output root và có thể chứa dữ liệu các phiên trước. Kích thước trước/sau lọc chỉ có ý nghĩa khi đo cùng tập dữ liệu đã giải nén; không suy tỷ lệ loại hình từ package nén.

## Mức sẵn sàng cho MS2

Corpus đã tạo là nền tảng cho parsing, nhưng cần rà soát source/corpus thiếu, version chưa hoàn tất và metadata liên kết trước khi chốt đầu vào MS2. Validator không biên dịch LaTeX và không kiểm chứng toàn bộ ngữ nghĩa; các trường hợp rỗng/nhị phân cần kiểm tra mẫu thực tế. References phụ thuộc độ phủ và giới hạn của Semantic Scholar; thiếu dữ liệu ở đây cần được giữ nhãn khi chuyển sang matching.

## Kết luận và phần cần hoàn thiện

Kết quả hiện tại xác nhận phương pháp thu thập, pipeline tích hợp và khả năng tạo báo cáo từ artifacts. Tiến độ 5.000 ID/người do nhóm cung cấp được ghi nhận; mức thu thập thành công và chất lượng được công bố đúng phạm vi có bằng chứng. Chưa kết luận toàn bộ dữ liệu MS1 đạt yêu cầu chỉ từ việc kết thúc notebook.

Để hoàn thiện nghiệm thu, nhóm cần bổ sung audit/thống kê toàn dải còn thiếu, xử lý hoặc giải thích các lỗi kiểm định, xác minh lại audit không nhất quán và hoàn thiện benchmark CPU-only với biên đo rõ ràng. Sau đó có thể cập nhật tỷ lệ thành công toàn nhóm và chốt snapshot đầu vào cho MS2.
