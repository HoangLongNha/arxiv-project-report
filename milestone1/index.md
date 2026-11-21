# Milestone 1: Thu thập dữ liệu arXiv

Pipeline xác định version, tải source, trích xuất TeX/BibTeX, chuẩn hóa metadata, truy vấn references và kiểm định đầu ra. Mỗi thành viên xử lý một dải 5.000 ID; tổng phạm vi là 25.000 ID.

Năm audit toàn dải xác nhận không còn ID chưa ghi nhận hoặc lookup chưa giải quyết. Kết quả này chứng minh bao phủ Discovery; số paper đạt kiểm định và mức đầy đủ source được báo riêng. Audit TV2 mới đã sửa cờ hoàn tất về false, phù hợp việc còn paper chưa đạt, nhưng trường tổng version vẫn chưa khớp chi tiết.

Báo cáo phân tích cumulative của cả năm thành viên và các phiên Colab đã nộp. TV1 đã có bản xuất mới ghi đủ 5.000 Discovery thành công, thay bản 0 record trước đó. Audit và cumulative vẫn ghi ngày riêng; thống kê tích lũy không thay phép kiểm định mới.

- [Phương pháp](methodology.md)
- [Thiết lập và mẫu số](experimental-setup.md)
- [Kết quả thu thập và chất lượng](preliminary-results.ipynb)
- [Hiệu năng](performance.ipynb)
- [Thảo luận và hạn chế](discussion.md)
- [Bằng chứng và tái lập](audit-appendix.ipynb)
