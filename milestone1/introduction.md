# Mục tiêu và dữ liệu đầu vào

Mục tiêu MS1 là thu thập corpus phục vụ parsing và reference matching, bao gồm mọi version của paper được giao; metadata và references được liên kết theo publication. Tệp hình bị loại khỏi corpus nhưng lệnh LaTeX như `\includegraphics` được giữ nguyên để không phá cấu trúc tài liệu.

## Phạm vi nhóm 6

| Range | Số ID đầu vào |
|---|---:|
| 2508.12872–2508.17871 | 5.000 |
| 2506.15788–2506.20787 | 5.000 |
| 2411.08799–2411.13798 | 5.000 |
| 2410.18025–2410.23024 | 5.000 |
| 2410.03025–2410.08024 | 5.000 |

Nguồn: sheet Teams trong workbook đăng ký nhóm; cột tháng là ngày Excel nên được chuyển thành YYMM. Các khoảng không giao nhau, tổng 25.000 ID. Đây là số lookup được giao, chưa phải số paper tồn tại hay số version tải thành công.

## Đầu ra

Source thô ở `raw/<paper_key>/vN/`, corpus ở `corpus/<paper_key>/vN/`, metadata và references theo paper. Checkpoint từng stage giúp resume và truy vết lỗi; validator ghi báo cáo riêng. Corpus không đưa vào repository Git. Bảng `papers` và `references` được đặc tả cho bộ dữ liệu nộp cuối, không phải yêu cầu nộp corpus trung gian ở MS1.

Demo đi kèm có hai paper discovery được và một ID cố ý không tồn tại: paper thứ nhất có hai version source, paper thứ hai có một version PDF-only. Đây là fixtures do nhóm tạo, không phải kết quả crawl hai paper thật cùng ID.
