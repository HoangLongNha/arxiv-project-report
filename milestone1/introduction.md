# Giới thiệu và phạm vi dữ liệu

## Mục tiêu

Nhóm xây dựng corpus để phục vụ phân tích cấu trúc bài báo và đối chiếu tài liệu tham khảo. Với mỗi paper tồn tại, hệ thống tìm toàn bộ lịch sử phiên bản, tải từng source và giữ nguyên nội dung các tệp `.tex`/`.bib`. Tệp hình bị loại khỏi corpus; các lệnh LaTeX định nghĩa hình vẫn được giữ để không phá cấu trúc tài liệu.

## Phân công dữ liệu

| Thành viên chạy dữ liệu | Dải arXiv ID | Số ID được giao |
|---|---|---:|
| TV1 | 2508.12872–2508.17871 | 5.000 |
| TV2 | 2506.15788–2506.20787 | 5.000 |
| TV3 | 2411.08799–2411.13798 | 5.000 |
| TV4 | 2410.18025–2410.23024 | 5.000 |
| TV5 | 2410.03025–2410.08024 | 5.000 |
| **Toàn nhóm** | **Năm dải không giao nhau** | **25.000** |

Nguồn phân công là workbook đăng ký nhóm, sheet Teams. Mỗi thành viên chạy pipeline tích hợp trên dải cá nhân; điều này khác với vai trò phát triển module của thành viên đó.

## Đơn vị thống kê

- **ID đầu vào:** một định danh cần tra cứu, có thể không tồn tại hoặc gặp lỗi tạm thời.
- **Paper:** một bài báo được phát hiện thành công từ ID.
- **Version:** một phiên bản của paper; một paper có thể có nhiều version.
- **Reference:** một mục tài liệu tham khảo mà Semantic Scholar trả về cho paper.

Vì vậy, chạy 5.000 ID không đồng nghĩa thu được 5.000 paper hoặc 5.000 source. ID không tồn tại là một kết quả lookup đã giải quyết, còn lỗi API có thể cần thử lại.

## Đầu ra và phạm vi nộp

Dữ liệu làm việc gồm source thô, corpus TeX/BibTeX, metadata, references và checkpoint. Source/corpus được tách theo paper và version; metadata và references được liên kết theo paper. Dữ liệu được nhóm giữ để dùng cho MS2–MS3, không đưa corpus vào repository mã nguồn.

Hai bảng dữ liệu được chuẩn bị cho lần nộp cuối là bảng paper (định danh, tiêu đề, tác giả, ngày nộp/cập nhật, venue) và bảng references (paper trích dẫn, định danh arXiv của reference và metadata đi kèm). References chưa có arXiv ID vẫn được giữ trong dữ liệu làm việc, nhưng không trở thành dòng của bảng references cuối nếu chưa đáp ứng khóa định danh.
