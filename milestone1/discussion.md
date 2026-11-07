# Thảo luận, hạn chế và kết luận

## Kết quả đã xác minh

Audit TV2–TV5 xác nhận mỗi dải đã có record và lookup thành công cho đủ 5.000 ID. TV5 đã thử lại bốn Discovery lỗi; audit ngày 07/11 ghi nhận 8.348 version, 4.620 paper đạt và 380 chưa đạt. TV1 đã có kết quả một phiên resume sáu ID cuối, chưa có audit toàn assignment trong ZIP được gửi.

Các kết quả này ghi nhận tiến độ đầu vào và những paper đã được kiểm tra. Số source, kích thước và references cần được tổng hợp từ dữ liệu tích lũy. Statistics của lượt resume cuối không đủ để suy các chỉ số đó cho toàn nhóm.

## Chất lượng và ảnh hưởng tới MS2

TV3 còn 180 paper chưa đạt, TV4 còn 118, theo audit được nộp. Validator có thể báo lỗi do stage upstream, tệp/đường dẫn hoặc trạng thái checkpoint chưa nhất quán. Mỗi paper cần được xem theo version và loại lỗi trước khi quyết định chạy lại bước nào. Một lỗi references cũng có thể làm paper fail dù source LaTeX vẫn hiện diện.

Audit TV2 vẫn có mâu thuẫn giữa cờ hoàn tất và số paper fail. TV5 đã hết lỗi Discovery nhưng còn lỗi validation. Riêng 2410.05044, việc tải source bị ngắt trước khi đủ dữ liệu sau năm lần thử; metadata và references đã có không thay thế source còn thiếu. Các số đếm giữ nguyên theo nguồn và ngày audit.

Trước MS2, nhóm cần kiểm tra các version thiếu source/corpus và liên kết metadata. Trường hợp PDF-only được giữ trạng thái riêng. Những tệp bị báo rỗng/nhị phân cần kiểm tra mẫu; validator không biên dịch LaTeX và không kiểm chứng toàn bộ ngữ nghĩa nội dung.

## Giới hạn của phép đo

Benchmark hiện có ghi lại một số phiên resume. Các run đã được khử trùng lặp theo định danh; tổng thời gian được ghi là thời gian của các phiên đã nộp. Chưa có đủ lịch sử để coi đó là toàn bộ chi phí thu thập 25.000 ID hoặc một benchmark fresh thống nhất.

Mẫu RAM có thể bỏ lỡ đỉnh ngắn. RSS của cây tiến trình có thể đếm shared pages nhiều lần; thao tác quét file trên Drive cũng làm khoảng lấy mẫu dài hơn cấu hình. Dung lượng output được đo theo mốc thời gian, gồm cả dữ liệu các phiên trước. Kích thước trước/sau lọc phải dùng cùng tập dữ liệu giải nén.

## Phần cần hoàn thiện

Nhóm cần bổ sung kết quả audit TV1 (ZIP hiện chỉ có inputs), rà soát các lỗi còn mở và xuất thống kê tích lũy trên các dải cá nhân. Công cụ đọc checkpoint/corpus đã được chuẩn bị trong repository báo cáo; thao tác này không crawl lại dữ liệu. Những tệp thống kê được xuất sẽ cung cấp số source/corpus, cặp đo kích thước và references cho phần kết quả.

Pipeline đã tích hợp các bước thu thập và QA. Bốn assignment có bằng chứng bao phủ record đầy đủ, nhưng chất lượng và thống kê cuối cùng của cả nhóm vẫn cần các bước trên trước khi nghiệm thu.
