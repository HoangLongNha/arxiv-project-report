# arXiv Project Report — Nhóm 6

Repository Jupyter Book riêng, chỉ chứa báo cáo và artifacts kiểm chứng, không chứa corpus. Kết quả sơ bộ ngày 04/11/2026 đã đối chiếu bộ nộp của TV2–TV5; chưa nghiệm thu toàn nhóm. MS2 sẽ nối tiếp MS1 trong cùng book sau khi nhóm bàn giao.

Cấu trúc bản nộp gồm giới thiệu/phạm vi, phương pháp, thiết lập thực nghiệm, kết quả thu thập và chất lượng, hiệu năng, thảo luận/kết luận, đóng góp thành viên, tài liệu tham khảo và phụ lục. Các notebook vẫn thực thi khi build nhưng ẩn input code trên HTML bằng tag `remove-input`. Tiến độ 5.000 ID/người do nhóm cung cấp được phân biệt với số liệu kiểm chứng từ artifacts; không suy hoàn tất dữ liệu từ việc notebook kết thúc.

## Build

Sử dụng Python 3.12. Cố định Jupyter Book 1.0.4.post1 để phù hợp `_config.yml`/`_toc.yml`; không dùng lệnh/config Book 2 cho project này.

```powershell
python -m pip install -r requirements.txt
python -m ipykernel install --user --name python3
jupyter-book build . --all --warningiserror
```

Mở `_build/html/index.html`. `execute_notebooks: force` buộc chạy notebook khi build; lỗi notebook làm build thất bại. Ba notebook kết quả, hiệu năng và phụ lục chỉ đọc artifacts đã lưu và kiểm hash, không gọi arXiv/Drive trong CI, không phụ thuộc `TV5_RUN`.

Để tạo lại toàn bộ nội dung đã biên tập, chạy `python scripts/prepare_submission_report.py`. Script này là nguồn nội dung Markdown/notebook của bản nộp; sửa nội dung tại đây rồi tạo lại để tránh mất thay đổi. `scripts/prepare_preliminary_results.py` là tên tương thích và gọi cùng generator mới.

`scripts/import_member_artifacts.py` nhập các ZIP đã tải về workspace cha, kiểm CRC/SHA-256, không sửa ZIP/corpus và từ chối ghi đè bằng nội dung khác. Bộ nộp TV2 có một lớp ZIP lồng; script xử lý cả hai lớp. `scripts/import_supplementary_artifacts.py` nhập riêng hai phiên TV4 bổ sung vào `supplementary-20261104`, không thay kết quả phiên cuối đã lưu. Nguồn Drive và hash nằm trong `provenance.json`. Import chỉ lược đường dẫn cục bộ trong `run.json`/`benchmark.json`; các artifacts còn lại giữ nguyên bytes. Snapshot không tự cập nhật khi Drive thay đổi; dữ liệu mới cần nhập thành bộ riêng và đối chiếu phạm vi trước khi chọn vào báo cáo.

## Xuất artifacts từ pipeline

Từ repository source sau khi có benchmark:

```powershell
python -m arxiv_pipeline.reporting.milestone1.export --run artifacts/ms1-colab-final --book ../arxiv-project-report --name colab-final
```

Exporter giữ statistics/samples/timings, loại local argv/path khỏi benchmark công khai và ghi hash nguyên bản trong provenance. Không ghi đè run cũ. Lưu originals và logs trong hồ sơ chạy; không đưa API key hay corpus vào Git. Bản nộp hiện chọn bộ artifacts trong `utils/preliminary_results.py`; chỉ đổi biến `TV5_RUN` không thay dữ liệu trên các trang này. Khi cập nhật cần xác minh dải, run ID, snapshot và các kết luận trong generator trước khi build.

## Google Colab

Mở `colab/MS1_Benchmark_CPU.ipynb`, chọn CPU-only, cấu hình source ref đã push có code TV5, chạy smoke trước. Cấu hình năm range nhóm 6 được notebook đọc từ source repo. Chỉ chuyển sang full sau khi kiểm tra môi trường, disk và API. Notebook đóng gói kết quả để tải về; không tự trình bày lượt local/demo là benchmark cuối.

## GitHub Pages

Workflow `.github/workflows/deploy.yml` build trên PR/push, chỉ deploy khi không phải PR. Trên repository GitHub report đặt Settings → Pages → Source = GitHub Actions. Trang đang dùng snapshot artifacts đã commit; không cần cấu hình `TV5_RUN` cho bản nộp hiện tại.

Repository này được chuẩn bị độc lập với source. Nếu cần tạo remote ở tài khoản khác, dùng tài khoản có quyền phù hợp:

```powershell
git add .
git commit -m "docs: add MS1 executable Jupyter Book report"
gh repo create arxiv-project-report --public --source . --remote origin --push
```

Kiểm tra link GitHub Pages và các trang/biểu đồ sau khi workflow thành công. Trong sandbox có thể không đọc được keyring; kiểm tra đăng nhập bằng môi trường người dùng có quyền hợp lệ. Trạng thái triển khai thực tế được ghi trong tài liệu bàn giao TV5.

## Nội dung

- `milestone1/`: mục tiêu, phương pháp, notebooks thống kê/hiệu năng, phân tích hạn chế.
- `milestone1/contributions/`: tài liệu bàn giao gốc TV1–TV4, được tải qua trang Đóng góp thành viên; không còn là các chương báo cáo độc lập trong mục lục.
- `milestone1/experimental-setup.md`: đơn vị đánh giá, mẫu số và thiết kế đo.
- `milestone1/preliminary-results.ipynb`: tiến độ nhóm báo cáo, kết quả thu thập và chất lượng được kiểm chứng.
- `milestone1/performance.ipynb`: số đo theo từng phiên, tách các lượt resume/chồng lặp.
- `milestone1/audit-appendix.ipynb`: định danh run, nguồn, hash và đối chiếu audit.
- `summaries/milestone1/demo/`: số đo local trên fixtures tổng hợp, có nhãn synthetic_demo.
- `summaries/milestone1/live-smoke-local/`: smoke một ID thật trên máy hiện tại, nhãn live_unverified; có thể chọn bằng `TV5_RUN=live-smoke-local`, không phải benchmark Colab.
- `summaries/milestone1/colab-cpu-sample/`: mẫu CPU-only trên Colab, nhãn colab_cpu_sample, run ID, số đo thô và provenance; coverage assignment được ghi riêng trong corpus_coverage.json.
- `colab/`: notebook tái lập benchmark CPU-only; mẫu một paper đã chạy trong Colab. Chọn source commit `0f8d83b591c89cf085f344f5fb59af671ab43b81` để tái lập phiên bản đã đo.
- `references.md`: nguồn chính thức và tài liệu kỹ thuật.

Ngôn ngữ hiện tại là tiếng Việt; nếu chương trình học quy định ngôn ngữ khác, cần chuyển trước khi nộp.
