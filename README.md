# arXiv Project Report — Nhóm 6

Repository Jupyter Book riêng, chỉ chứa báo cáo và artifacts kiểm chứng, không chứa corpus. Kết quả sơ bộ ngày 04/11/2026 đã đối chiếu bộ nộp của TV2–TV5; chưa nghiệm thu toàn nhóm. MS2 sẽ nối tiếp MS1 trong cùng book sau khi nhóm bàn giao.

Cập nhật hiện tại: `milestone1/preliminary-results.ipynb` sinh bảng coverage, collection outcomes và performance theo từng thành viên/run từ `summaries/milestone1/preliminary-20261104`. Chưa có TV1; audit TV2 mâu thuẫn; ZIP TV3/TV4 thiếu kết quả audit; TV5 còn unresolved/validation fail. Các mẫu demo/smoke trước đây được giữ riêng làm lịch sử.

## Build

Sử dụng Python 3.12. Cố định Jupyter Book 1.0.4.post1 để phù hợp `_config.yml`/`_toc.yml`; không dùng lệnh/config Book 2 cho project này.

```powershell
python -m pip install -r requirements.txt
python -m ipykernel install --user --name python3
jupyter-book build . --all --warningiserror
```

Mở `_build/html/index.html`. `execute_notebooks: force` buộc chạy notebook mỗi lần build; lỗi notebook làm build thất bại. Trang kết quả mới chỉ đọc artifacts đã lưu và kiểm hash, không gọi arXiv/Drive trong CI và không phụ thuộc `TV5_RUN`. Biến này chỉ dùng cho hai notebook thống kê/hiệu năng lịch sử hiện không nằm trong mục lục.

Để tạo lại notebook kết quả sơ bộ, chạy `python scripts/prepare_preliminary_results.py`. `scripts/import_member_artifacts.py` nhập các ZIP đã tải về workspace cha, kiểm CRC/SHA-256, không sửa ZIP/corpus và từ chối ghi đè bằng nội dung khác. Bộ nộp TV2 có một lớp ZIP lồng; script xử lý cả hai lớp. Nguồn Drive và hash nằm trong `provenance.json` của từng thành viên. Import chỉ lược đường dẫn cục bộ trong `run.json`/`benchmark.json`; các artifacts còn lại giữ nguyên bytes. Snapshot này không tự cập nhật khi Drive thay đổi; lần cập nhật dữ liệu tiếp theo cần một snapshot mới và cập nhật lựa chọn trong `utils/preliminary_results.py`.

## Thay số liệu demo bằng run thật

Từ repository source sau khi có benchmark:

```powershell
python -m arxiv_pipeline.reporting.milestone1.export --run artifacts/ms1-colab-final --book ../arxiv-project-report --name colab-final
```

Sau đó ở repo report:

```powershell
$env:TV5_RUN = 'colab-final'
jupyter-book build . --all --warningiserror
```

Exporter giữ statistics/samples/timings, loại local argv/path khỏi benchmark công khai và ghi hash nguyên bản trong provenance. Không ghi đè run cũ. Lưu originals và logs trong hồ sơ chạy; không đưa API key hay corpus vào Git. Cập nhật intro/discussion sau khi nghiệm thu thật, không để banner demo gây nhầm.

## Google Colab

Mở `colab/MS1_Benchmark_CPU.ipynb`, chọn CPU-only, cấu hình source ref đã push có code TV5, chạy smoke trước. Cấu hình năm range nhóm 6 được notebook đọc từ source repo. Chỉ chuyển sang full sau khi kiểm tra môi trường, disk và API. Notebook đóng gói kết quả để tải về; không tự trình bày lượt local/demo là benchmark cuối.

## GitHub Pages

Workflow `.github/workflows/deploy.yml` build trên PR/push, chỉ deploy khi không phải PR. Trên repository GitHub report đặt Settings → Pages → Source = GitHub Actions. Nếu có run thật, đặt repository variable `TV5_RUN=colab-final`; tên phải khớp thư mục summary đã commit.

Repository này được chuẩn bị độc lập với source. Nếu cần tạo remote ở tài khoản khác, dùng tài khoản có quyền phù hợp:

```powershell
git add .
git commit -m "docs: add MS1 executable Jupyter Book report"
gh repo create arxiv-project-report --public --source . --remote origin --push
```

Kiểm tra link GitHub Pages và các trang/biểu đồ sau khi workflow thành công. Trong sandbox có thể không đọc được keyring; kiểm tra đăng nhập bằng môi trường người dùng có quyền hợp lệ. Trạng thái triển khai thực tế được ghi trong tài liệu bàn giao TV5.

## Nội dung

- `milestone1/`: mục tiêu, phương pháp, notebooks thống kê/hiệu năng, phân tích hạn chế.
- `milestone1/contributions/`: bốn trang đóng góp TV1–TV4 từ bộ cập nhật báo cáo thành viên; được liên kết dưới mục Phương pháp triển khai. Trạng thái và số liệu thành viên nêu được giữ trong phạm vi nguồn tư liệu, không thay cho nghiệm thu end-to-end hoặc số đo Colab đã xác minh.
- `summaries/milestone1/demo/`: số đo local trên fixtures tổng hợp, có nhãn synthetic_demo.
- `summaries/milestone1/live-smoke-local/`: smoke một ID thật trên máy hiện tại, nhãn live_unverified; có thể chọn bằng `TV5_RUN=live-smoke-local`, không phải benchmark Colab.
- `summaries/milestone1/colab-cpu-sample/`: mẫu CPU-only trên Colab, nhãn colab_cpu_sample, run ID, số đo thô và provenance; coverage assignment được ghi riêng trong corpus_coverage.json.
- `colab/`: notebook tái lập benchmark CPU-only; mẫu một paper đã chạy trong Colab. Chọn source commit `0f8d83b591c89cf085f344f5fb59af671ab43b81` để tái lập phiên bản đã đo.
- `references.md`: nguồn chính thức và tài liệu kỹ thuật.

Ngôn ngữ hiện tại là tiếng Việt; nếu chương trình học quy định ngôn ngữ khác, cần chuyển trước khi nộp.
