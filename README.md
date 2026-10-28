# arXiv Project Report — Nhóm 6

Repository Jupyter Book riêng, chỉ chứa báo cáo và số liệu tổng hợp, không chứa corpus. Đã có demo offline, smoke local và mẫu CPU-only trên Colab; chưa có kết quả toàn corpus. MS2 sẽ nối tiếp MS1 trong cùng book sau khi nhóm bàn giao.

Cập nhật: đã có mẫu `colab-cpu-sample` chạy CPU-only trên Google Colab từ commit source sạch `0f8d83b`; một paper, một version, 97 references, exit 0. Audit assignment xác nhận còn 24.999/25.000 ID chưa có dữ liệu. Đây chưa phải nghiệm thu toàn corpus.

## Build

Sử dụng Python 3.12. Cố định Jupyter Book 1.0.4.post1 để phù hợp `_config.yml`/`_toc.yml`; không dùng lệnh/config Book 2 cho project này.

```powershell
python -m pip install -r requirements.txt
python -m ipykernel install --user --name python3
jupyter-book build . --all --warningiserror
```

Mở `_build/html/index.html`. `execute_notebooks: force` buộc chạy notebook mỗi lần build; lỗi notebook làm build thất bại. Notebook chỉ xử lý summary đã lưu, không gọi arXiv trong CI. Default `TV5_RUN=demo`; tên run không tồn tại sẽ gây lỗi, không tự fallback về demo.

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
- `summaries/milestone1/demo/`: số đo local trên fixtures tổng hợp, có nhãn synthetic_demo.
- `summaries/milestone1/live-smoke-local/`: smoke một ID thật trên máy hiện tại, nhãn live_unverified; có thể chọn bằng `TV5_RUN=live-smoke-local`, không phải benchmark Colab.
- `summaries/milestone1/colab-cpu-sample/`: mẫu CPU-only trên Colab, nhãn colab_cpu_sample, run ID, số đo thô và provenance; coverage assignment được ghi riêng trong corpus_coverage.json.
- `colab/`: notebook tái lập benchmark CPU-only; mẫu một paper đã chạy trong Colab. Chọn source commit `0f8d83b591c89cf085f344f5fb59af671ab43b81` để tái lập phiên bản đã đo.
- `references.md`: nguồn chính thức và tài liệu kỹ thuật.

Ngôn ngữ hiện tại là tiếng Việt; nếu chương trình học quy định ngôn ngữ khác, cần chuyển trước khi nộp.
