# arXiv Project — Nhóm 6

Báo cáo Milestone 1: thu thập source LaTeX mọi phiên bản của các paper được giao, metadata và references; kiểm tra chất lượng và đánh giá hiệu năng.

```{warning}
Đã có benchmark **mẫu một paper trên Google Colab CPU-only**, run `colab-cpu-sample`, bên cạnh demo offline và smoke local. Chưa crawl đủ assignment 25.000 ID. Luôn đọc nhãn/phạm vi run; số đo mẫu không đại diện hiệu năng hay độ bao phủ toàn corpus.
```

Theo file đăng ký nhóm, nhóm 6 có năm khoảng, tổng 25.000 ID đầu vào. ID có thể không tồn tại; số version chỉ được xác định sau discovery. Đầu vào đầy đủ được lưu trong `configs/ms1_group6_ranges.json` của repository source.

Một repository source dùng cho toàn dự án; Jupyter Book có repository riêng. Khi Milestone 2 sẵn sàng, thêm phần MS2 vào cùng book. Hiện book chỉ triển khai MS1.

Smoke cục bộ ngày 28/10/2026: `2508.12872`, một version, 97 references, validation pass; số đo đầy đủ và nhãn live_unverified nằm trong `summaries/milestone1/live-smoke-local/`. Hai notebook có thể build lại với `TV5_RUN=live-smoke-local`; không trộn vào run demo.

Mẫu Colab CPU-only ngày 28/10/2026: `2508.12872`, một version, 97 references, validator pass; wall time 21,511 giây, peak RSS quan sát 41.771.008 bytes. Source commit sạch `0f8d83b`; raw samples, timings và provenance được xuất vào `summaries/milestone1/colab-cpu-sample/`. Audit trên runtime này xác nhận còn 24.999 ID chưa có discovery record. Biến `TV5_RUN=colab-cpu-sample` chọn dữ liệu này khi build.

- [Source code](https://github.com/LeoTkiet/arxiv-data-science)
- [Đề chính thức](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/)

README hướng dẫn build/triển khai, notebook Colab để chạy lại, và nguồn tham khảo đi kèm giúp kiểm chứng kết quả.
