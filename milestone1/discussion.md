# Thảo luận và kết luận

## Bao phủ đầu vào và mức hoàn thiện corpus

Năm audit xác nhận đủ 25.000 record và 25.000 lookup thành công. Checkpoint giúp nhóm tiếp tục sau gián đoạn và thử lại riêng ID hoặc stage lỗi. Lookup thành công cho biết đã nhận diện bài báo và version; source/corpus và kiểm định còn có thể chưa đạt.

Cumulative TV2–TV5 thống kê dữ liệu tích lũy qua nhiều phiên. Tỷ lệ paper đủ source thấp hơn bao phủ Discovery vì mỗi paper có thể có nhiều version, gặp lỗi tải/giải nén hoặc không có source TeX. Trạng thái no_source được giữ riêng để không coi mọi trường hợp thiếu TeX là lỗi mạng. Số download success và số source có tệp còn chênh lệch; cần kiểm tra checkpoint, đường dẫn và tệp trước khi dùng số trạng thái làm số source thực có.

## Kích thước và references

Chỉ giữ TeX/BibTeX làm giảm dung lượng trên tập paper có đủ cặp đo. So sánh dùng kích thước giải nén trước lọc và corpus sau lọc; không so gói nén với dữ liệu đã giải nén. Cặp đo thiếu được loại khỏi mẫu số, còn số paper được tính luôn đi kèm kết quả.

References được đếm theo paper trích dẫn, loại dòng trùng trong cùng paper. Cùng tài liệu được nhiều paper trích dẫn vẫn được đếm ở mỗi quan hệ. Trung bình bao gồm danh sách rỗng hợp lệ; truy vấn lỗi hoặc chưa được index không được coi là danh sách rỗng. Tỷ lệ truy vấn đọc được và tỷ lệ reference đủ metadata là hai chỉ số riêng.

TV2 có mức bao phủ references thấp hơn các dải còn lại; cần xem checkpoint references lỗi trước khi dùng cho matching. Tiêu chí đủ năm trường khá chặt vì nhiều tài liệu không có arXiv ID. Nó không thay độ chính xác nội dung do Semantic Scholar cung cấp.

## Chất lượng và chuẩn bị MS2

Một paper có thể vướng nhiều loại lỗi: stage upstream, artifact, corpus hoặc metadata/references. Cần phân loại theo paper/version rồi thử lại stage cần thiết. Paper chưa đạt validator vẫn có thể có TeX sử dụng được; có TeX cũng không bảo đảm mọi trường khác hợp lệ.

Audit TV2 mới đã thống nhất cờ hoàn tất với số paper fail, nhưng known_version_count ghi 3.887 trong khi cộng versions của 5.000 paper trong chính audit được 7.987, khớp cumulative. Báo cáo giữ tệp gốc, dùng cumulative cho số version và ghi mâu thuẫn trong phụ lục. TV5 đã giải quyết bốn lookup, nhưng lần thử source 2410.05044 trong bộ bằng chứng sửa lỗi vẫn bị IncompleteRead.

Validator kiểm tra cấu trúc, định danh, trạng thái và tệp; chưa biên dịch LaTeX hay đánh giá toàn bộ ngữ nghĩa. MS2 cần giữ liên kết paper/version, xử lý record không có source và dùng danh sách lỗi để tránh coi đầu vào thiếu là kết quả parsing rỗng hợp lệ.

## Giới hạn thực nghiệm

Ngày 10/11, đối chiếu trực tiếp Drive xác nhận TV1 có manifest đủ 5.000 Discovery thành công, 7.852 version và mẫu corpus có TeX/BibTeX. Bao phủ TV1 đã được xác nhận; các chỉ số kích thước và references vẫn cần bản cumulative đọc đúng dữ liệu này. Bản TV5 ngày 10/11 có đủ 5.000 Discovery thành công và 8.348 version. Tổng TV2–TV5 mô tả các snapshot đủ coverage, không phải số liệu đồng thời hay tổng corpus năm thành viên. Cumulative đọc validation đã lưu, không thay audit mới.

Benchmark chủ yếu chạy resume. Phiên TV1 mới có toàn dải đầu vào và mẫu RAM trên Colab CPU-only nhưng dùng cache, nên chưa đo chi phí tải mới toàn dải. TV2/TV5 thiếu mẫu RAM đại diện trong các phiên đã nộp. Không thể khôi phục runtime, RAM hay disk peak của phiên không có log từ cumulative JSON.

Để chốt số liệu corpus của cả nhóm, cần xuất lại cumulative TV1 từ đúng thư mục dữ liệu đã audit. Để kết luận hiệu năng end-to-end của toàn quá trình, cần lịch sử đo đầy đủ hoặc benchmark Colab CPU-only có biên đo thống nhất. Báo cáo trình bày các số đo có bằng chứng và giữ rõ những giới hạn này.
