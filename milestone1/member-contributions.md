# Đóng góp thành viên

Nhóm phân chia trách nhiệm phát triển theo module, đồng thời mỗi thành viên chạy pipeline tích hợp trên dải 5.000 ID cá nhân. Hoàn thành module và hoàn thành thu thập/QA của assignment là hai loại kết quả được đánh giá riêng.

| Thành viên | Trách nhiệm phát triển | Sản phẩm chính |
|---|---|---|
| TV1 | Kiến trúc, Discovery và điều phối | Schema/hợp đồng chung, phân giải ID/version, CLI, checkpoint và resume |
| TV2 | Source downloader và raw storage | Tải theo version, streaming, hash, tệp tạm và xử lý lỗi tải |
| TV3 | Xử lý source và tạo corpus | Giải nén an toàn, lọc TeX/BibTeX, tổ chức corpus và sidecar |
| TV4 | Metadata và references | Chuẩn hóa metadata, Semantic Scholar client/batch, phân trang và loại trùng |
| TV5 | QA, thống kê, benchmark và báo cáo | Validator, audit assignment, đo tài nguyên, tổng hợp artifacts và Jupyter Book |

Các kiểm thử module kiểm tra những trường hợp như định danh sai, thiếu version, archive không an toàn, source không có TeX, lỗi API và checkpoint chạy tiếp. Kết quả kiểm thử phần mềm không được dùng thay tỷ lệ thành công thu thập dữ liệu thực tế.

## Tư liệu bàn giao

Các tài liệu gốc dưới đây được giữ để truy vết quá trình phát triển. Chúng phản ánh thời điểm thành viên viết báo cáo và có thể chứa hướng dẫn nội bộ, ví dụ hoặc số liệu thí nghiệm riêng. Nội dung chính đã được biên tập thống nhất trong phần phương pháp và thực nghiệm; không dùng tuyên bố hoàn thành trong tài liệu lịch sử làm kết luận nghiệm thu hiện tại.

- {download}`Tài liệu TV1 <contributions/tv1-discovery.md>`
- {download}`Tài liệu TV2 <contributions/tv2-downloader.md>`
- {download}`Tài liệu TV3 <contributions/tv3-extractor.md>`
- {download}`Tài liệu TV4 <contributions/tv4-metadata-references.md>`
