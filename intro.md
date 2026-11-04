# arXiv Project — Nhóm 6

Báo cáo Milestone 1: thu thập source LaTeX mọi phiên bản của các paper được giao, metadata và references; kiểm tra chất lượng và đánh giá hiệu năng.

```{warning}
Cập nhật ngày **04/11/2026**: đã nhận artifacts của **TV2–TV5**, chưa có dữ liệu TV1 trong thư mục nhóm được cung cấp. Kết quả hiện tại là **sơ bộ**: audit TV2 có mâu thuẫn, TV3/TV4 chưa có tệp kết quả audit trong bộ đã kiểm tra, TV5 còn lỗi Discovery/validation. Chưa thể xác nhận hoàn tất MS1 hoặc công bố thống kê cuối cùng cho 25.000 ID.
```

Theo file đăng ký nhóm, nhóm 6 có năm khoảng, tổng 25.000 ID đầu vào. ID có thể không tồn tại; số version chỉ được xác định sau discovery. Đầu vào đầy đủ được lưu trong `configs/ms1_group6_ranges.json` của repository source.

Một repository source dùng cho toàn dự án; Jupyter Book có repository riêng. Khi Milestone 2 sẵn sàng, thêm phần MS2 vào cùng book. Hiện book chỉ triển khai MS1.

[Kết quả sơ bộ và tiến độ thu thập](milestone1/preliminary-results.ipynb) trình bày riêng **coverage, collection success và data validity**, bảng theo thành viên, số đo theo từng run và giới hạn của bằng chứng. Bảng/biểu đồ được tính trực tiếp từ artifacts đã lưu; dữ liệu thiếu không được thay bằng 0.

Các bộ `demo`, `live-smoke-local` và `colab-cpu-sample` ngày 28/10/2026 được giữ làm bằng chứng thử nghiệm lịch sử. Audit mẫu một paper khi đó không mô tả tiến độ hiện tại của nhóm. Các bộ này không được cộng vào kết quả sơ bộ mới.

- [Source code](https://github.com/LeoTkiet/arxiv-data-science)
- [Đề chính thức](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/)

README hướng dẫn build/triển khai, notebook Colab để chạy lại, và nguồn tham khảo đi kèm giúp kiểm chứng kết quả.
