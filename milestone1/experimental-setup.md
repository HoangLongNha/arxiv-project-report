# Thiết lập thực nghiệm

## Phạm vi dữ liệu

Kết quả corpus dùng bộ MS1 đã được nhóm chốt, gồm năm dải không giao nhau, tổng 25.000 ID. Mỗi paper chỉ được tính một lần; mỗi version dùng cặp arXiv ID và số phiên bản. Trạng thái kiểm định lấy từ audit hoặc validation trong bản kiểm kê tương ứng với bộ bàn giao.

## Định nghĩa chỉ số

| Chỉ số | Cách tính và giới hạn |
|---|---|
| Bao phủ Discovery | ID nhận diện thành công / 25.000 ID được giao |
| Source thu thập được | Version có source theo dữ liệu kiểm định; phân biệt với record no_source |
| Tỷ lệ đạt kiểm định | Paper đạt toàn bộ quy tắc / paper đã kiểm định |
| References đã ghi nhận | Tổng quan hệ paper–reference đọc được trong bản kiểm định, không phải số tài liệu tham khảo duy nhất toàn cục |
| References/paper | References đã ghi nhận / paper của phạm vi xét; không ước lượng references chưa thu được |
| Kích thước trước/sau lọc | Cộng version trong từng paper, rồi lấy trung bình trên cùng tập có đủ cặp đo |
| Metadata references đầy đủ | Reference đủ năm trường / references được xét trong phép đo |

Một record no_source hợp lệ có thể đại diện cho PDF-only, không tự động là lỗi thu thập. Paper đạt validator cũng không có nghĩa luôn có TeX: record rỗng hợp lệ được giữ theo hợp đồng. Tỷ lệ Discovery, mức hiện diện source và tỷ lệ đạt validator vì vậy được báo riêng.

## Thực nghiệm dung lượng và hiệu năng

Các phép đo kích thước và benchmark đã lưu được giữ làm bằng chứng thực nghiệm, với ngày và phạm vi riêng. Chúng không được gắn lại thành phép đo trên bộ corpus cuối chỉ bằng cách thay nhãn. Kích thước trước lọc lấy từ sidecar giải nén; sau lọc là TeX/BibTeX. Trung bình gộp có trọng số theo số paper có cặp đo.

Testbed là Google Colab CPU-only. Công cụ benchmark đo wall time của tiến trình pipeline, RSS của cây tiến trình và dung lượng toàn output; sample/timing giữ trong artifacts. Các phiên resume có thể dùng cache và thử lại stage, nên thời gian đo mô tả phiên thực thi đó. Tổng thời gian các phiên được khử trùng lặp theo run ID và không coi là toàn bộ thời gian thu thập ban đầu nếu lịch sử đo không đầy đủ.

Peak RAM/disk là cực đại tại các lần quan sát; RAM trung bình dùng trọng số thời gian. Phiên không có đủ khoảng lấy mẫu được đánh dấu không tính. Final output gồm raw, corpus, checkpoint và sidecar, không đồng nghĩa kích thước riêng TeX/BibTeX. Nhóm không cộng disk của các phiên chồng lặp thành dung lượng corpus.
