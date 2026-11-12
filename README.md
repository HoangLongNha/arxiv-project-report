# arXiv Project Report, nhóm 6

Jupyter Book công khai cho MS1 và các milestone tiếp theo, tách khỏi [repository code](https://github.com/LeoTkiet/arxiv-data-science). [GitHub Pages](https://hoanglongnha.github.io/arxiv-project-report/) được build và deploy bằng GitHub Actions.

Bộ bằng chứng có audit toàn dải và cumulative của cả năm thành viên. Audit xác nhận đủ 25.000 record và lookup thành công; còn paper chưa đạt validator. Cumulative TV1 đã nhận nhưng ghi 0 record và 5.000 unseen, nên chỉ giữ để đối chiếu, chưa dùng các số 0 đó làm thống kê corpus thực tế. TV5 đã bổ sung cumulative ngày 10/11/2026, ghi đủ 5.000 Discovery thành công và 8.348 version sau sửa lookup. Trường tổng version audit TV2 không khớp chi tiết; phần thống kê version dùng cumulative và phụ lục ghi rõ mâu thuẫn.

## Môi trường và build

Dùng Python 3.12. Jupyter Book cố định phiên bản 1.0.4.post1 để phù hợp cấu hình Book 1.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m ipykernel install --user --name python3
jupyter-book build . --all --warningiserror
```

Trên Linux/macOS dùng `source .venv/bin/activate`. Mở `_build/html/index.html` sau build. Notebook bắt buộc thực thi; lỗi làm build thất bại. Bảng, biểu đồ và CSV thời gian từng paper tính lại từ artifacts đã commit; input code được ẩn trên HTML. Build không gọi API crawl/Drive và không cần corpus gốc.

Tạo lại các trang đã biên tập:

```powershell
python scripts/prepare_submission_report.py
```

`scripts/final_ms1_sections.py` chứa kết quả và kết luận hiện hành, phối hợp với `scripts/submission_updates.py` và generator. Sửa các nguồn này rồi tạo lại trang để giữ nội dung nhất quán.

## Kiểm thử

Các kiểm thử notebook benchmark cần source pipeline. Cài bản tương thích với CI vào môi trường kiểm thử hoặc dùng checkout cục bộ qua biến TV5_SOURCE:

```powershell
python -m pip install "arxiv-data-science[reporting,dev] @ git+https://github.com/LeoTkiet/arxiv-data-science.git@0f8d83b591c89cf085f344f5fb59af671ab43b81"
python -m unittest discover -s tests -v
```

Kiểm thử bảo vệ kết quả khi chạy lại, xác minh run/hash, phạm vi audit, checkpoint nhiều phiên và tổng hợp có trọng số. Chúng không thay audit dữ liệu thực.

## Pipeline và benchmark trên Colab

Mở `colab/MS1_Benchmark_CPU.ipynb`, chọn runtime CPU-only, cấu hình đúng thành viên/dải ID, output và source ref. Notebook cài source riêng và kiểm tra trước khi chạy. Chạy smoke trước khi thực hiện cấu hình full. Hướng dẫn pipeline chi tiết nằm trong README repo code.

Dữ liệu sẵn có dùng AUTO_RESUME=True để tái sử dụng checkpoint. Fresh run cần output riêng. Benchmark resume đo kiểm tra cache và stage thử lại, không phải chi phí tải mới toàn dải. Giữ mỗi run trong thư mục kết quả riêng; dừng tiến trình ghi trước audit hoặc xuất cumulative.

## Thống kê corpus tích lũy

Mở [MS1_Cumulative_Statistics.ipynb trên Colab](https://colab.research.google.com/github/HoangLongNha/arxiv-project-report/blob/main/colab/MS1_Cumulative_Statistics.ipynb), chọn đúng TV và DATA, xác nhận WRITERS_STOPPED=True sau khi dừng pipeline/audit. Notebook không crawl lại hoặc sửa checkpoint. Nếu code tải về không khớp SHA-256, mở notebook mới nhất.

Chạy tương đương trên máy có corpus và nhập kết quả đã nhận:

```powershell
python scripts/export_cumulative_ms1.py --member TV3 --output 'D:/corpus/tv3/data' --save 'D:/corpus/tv3/artifacts/cumulative-statistics.json' --writers-stopped
python scripts/import_cumulative_statistics.py --member TV3 --input 'D:/received/TV3-cumulative-statistics.json'
python scripts/import_cumulative_statistics.py --member TV5 --input 'D:/received/TV5-new.json' --snapshot cumulative-20261110
```

Importer giữ byte gốc, kiểm phạm vi/định danh/số đếm và lưu SHA-256. Nó từ chối ghi đè bản đã nhập; bản mới cần snapshot riêng qua --snapshot cumulative-YYYYMMDD và phải được chọn trong bộ đọc báo cáo sau rà soát. TV5 hiện chọn cumulative-20261110; bản cũ được giữ nguyên. WRITERS_STOPPED là xác nhận của người chạy, không phải phát hiện tiến trình tự động. Export kiểm thay đổi trong lúc đọc; validation lấy từ báo cáo đã lưu, không phải audit mới. Cumulative không khôi phục runtime/RAM/disk peak lịch sử.

Bộ TV1/TV2 bổ sung được nhập bằng:

```powershell
python scripts/import_nov09_artifacts.py --tv1 'D:/received/TV1-results.zip' --tv2-audit 'D:/received/assignment-audit-tv2.json'
```

Các importer cũ giữ snapshot TV2–TV5, các phiên TV4 và bằng chứng sửa TV5 ngày 07/11. Không nhập corpus hoặc pipeline.log vào repo báo cáo. Benchmark/run công khai lược đường dẫn máy; provenance lưu hash gốc và bản công bố. Khi chọn snapshot mới cần kiểm phạm vi, thời điểm và kết luận trước build.

## Cấu trúc

- `milestone1/`: phương pháp, thiết lập, kết quả, hiệu năng, thảo luận, đóng góp và phụ lục.
- `summaries/milestone1/`: snapshot bất biến, cumulative và provenance; demo/smoke không thay kết quả toàn assignment.
- `utils/preliminary_results.py`: đọc bằng chứng, kiểm hash/phạm vi và tính bảng tổng hợp.
- `utils/cumulative_statistics.py`: kiểm kê corpus tích lũy chỉ đọc.
- `_static/generated/`: CSV timing sinh khi build, không commit.
- `colab/`: notebook benchmark và cumulative.

## GitHub Pages và nộp bài

Workflow `.github/workflows/deploy.yml` kiểm thử, thực thi notebook và build. Push main hoặc workflow_dispatch triển khai Pages; PR chỉ kiểm tra. Settings → Pages chọn GitHub Actions. Kiểm tra trang kết quả, hiệu năng và link tải CSV sau deploy. MS2 bổ sung vào cùng book.

Bản hiện dùng tiếng Việt; nhóm cần đối chiếu ngôn ngữ chính thức chương trình trước nộp Moodle. Liên kết nộp gồm repo code công khai và Jupyter Book trên GitHub Pages.
