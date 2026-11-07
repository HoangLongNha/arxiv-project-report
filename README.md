# arXiv Project Report — Nhóm 6

Repository Jupyter Book riêng, chỉ chứa báo cáo và artifacts kiểm chứng, không chứa corpus. Cập nhật ngày 07/11/2026 bổ sung phiên benchmark TV1 và audit mới của TV5: TV5 có đủ 5.000 lookup thành công, 4.620 paper đạt và 380 chưa đạt validation. ZIP TV1 hiện chỉ có statistics của sáu ID cuối và inputs khai báo toàn dải, chưa có assignment-audit.json. Chưa nghiệm thu toàn nhóm.

Cấu trúc bản nộp gồm giới thiệu/phạm vi, phương pháp, thiết lập thực nghiệm, kết quả thu thập và chất lượng, hiệu năng, thảo luận/kết luận, đóng góp thành viên, tài liệu tham khảo và phụ lục. Các notebook vẫn thực thi khi build nhưng ẩn input code trên HTML bằng tag `remove-input`. Tiến độ 5.000 ID/người do nhóm cung cấp được phân biệt với số liệu kiểm chứng từ artifacts; không suy hoàn tất dữ liệu từ việc notebook kết thúc.

## Build

Sử dụng Python 3.12. Cố định Jupyter Book 1.0.4.post1 để phù hợp `_config.yml`/`_toc.yml`; không dùng lệnh/config Book 2 cho project này.

```powershell
python -m pip install -r requirements.txt
python -m ipykernel install --user --name python3
jupyter-book build . --all --warningiserror
```

Mở `_build/html/index.html`. `execute_notebooks: force` buộc chạy notebook khi build; lỗi notebook làm build thất bại. Ba notebook kết quả, hiệu năng và phụ lục chỉ đọc artifacts đã lưu và kiểm hash, không gọi arXiv/Drive trong CI, không phụ thuộc `TV5_RUN`.

Để tạo lại nội dung, chạy `python scripts/prepare_submission_report.py`. Phần biên tập hiện nằm trong `scripts/submission_updates.py`, được generator dùng để tạo Markdown và ba notebook báo cáo. `scripts/prepare_preliminary_results.py` là tên tương thích. Notebook xuất thống kê tích lũy cũng được tạo lại, với hash code tương ứng phiên bản hiện tại.

`scripts/import_member_artifacts.py` nhập các ZIP đã tải về workspace cha, kiểm CRC/SHA-256, không sửa ZIP/corpus và từ chối ghi đè bằng nội dung khác. Bộ nộp TV2 có một lớp ZIP lồng; script xử lý cả hai lớp. `scripts/import_supplementary_artifacts.py` nhập riêng hai phiên TV4 bổ sung vào `supplementary-20261104`, không thay kết quả phiên cuối đã lưu. Nguồn Drive và hash nằm trong `provenance.json`. Import chỉ lược đường dẫn cục bộ trong `run.json`/`benchmark.json`; các artifacts còn lại giữ nguyên bytes. Snapshot không tự cập nhật khi Drive thay đổi; dữ liệu mới cần nhập thành bộ riêng và đối chiếu phạm vi trước khi chọn vào báo cáo.

Bộ bổ sung ngày 07/11 được nhập bằng `scripts/import_nov07_artifacts.py --tv1 <ZIP> --tv5-retry <ZIP> --tv5-audit <ZIP>`. Script kiểm CRC, chọn artifacts cần cho báo cáo và lưu hash vào `updated-20261107`; không công bố pipeline log hoặc bản sao dữ liệu riêng. TV5 dùng audit mới nhưng giữ benchmark lịch sử. TV1 có dữ liệu phiên đo, chưa có audit toàn dải.

## Xuất artifacts từ pipeline

### Thống kê toàn corpus tích lũy

Mở [notebook xuất thống kê trên Colab](https://colab.research.google.com/github/HoangLongNha/arxiv-project-report/blob/main/colab/MS1_Cumulative_Statistics.ipynb), dừng các tiến trình ghi dữ liệu, chọn đúng thành viên và đường dẫn `data/`. Công cụ chỉ đọc dữ liệu hiện có; không gọi API crawl, không sửa manifest/checkpoint và không tạo benchmark giả. Tệp JSON được ghi mới vào `artifacts/cumulative_<UUID>/` và có thể tải về để gửi TV5.

Hoặc chạy trên máy có corpus:

```powershell
python scripts/export_cumulative_ms1.py --member TV3 --output 'D:/corpus/tv3/data' --save 'D:/corpus/tv3/artifacts/cumulative-statistics.json' --writers-stopped
```

`--writers-stopped` là xác nhận của người chạy, không phải công cụ tự phát hiện tiến trình. Export kiểm lại hash JSON và metadata tệp đã đọc; nếu có thay đổi thì dừng và không tạo báo cáo. Các sidecar kích thước có thể thiếu; số mẫu ghép cặp và diagnostics phải được xem cùng kết quả. Validation được đọc từ báo cáo đã lưu, không phải một lượt audit mới. Code notebook được tải từ repository và đối chiếu SHA-256 trước khi chạy; nếu code đã đổi, dùng bản notebook mới.

Nhận JSON từ thành viên rồi kiểm tra và nhập vào báo cáo:

```powershell
python scripts/import_cumulative_statistics.py --member TV3 --input 'D:/received/TV3-cumulative-statistics.json'
```

Importer xác minh member, dải, số lượng/định danh, snapshot và lưu hash tệp gốc. Nó từ chối ghi đè dữ liệu đã nhập. Các trang báo cáo chỉ dùng bản có provenance hợp lệ ở `summaries/milestone1/cumulative/TV3/`; khi chưa có, phần kích thước/references toàn dải tiếp tục ghi đang chờ xuất. Không dùng statistics 828/6/6 ID hoặc cộng các statistics resume để thay thế.

### Bằng chứng audit đã sửa

`scripts/import_updated_artifacts.py` nhập ba ZIP TV3/TV4 vào `updated-20261106`, giữ nguyên byte artifacts ngoài phần lược đường dẫn trong benchmark/run. Mỗi thành viên chọn một audit; hai audit TV4 cho cùng dải không được cộng. `session_members()` khử trùng lặp benchmark theo run ID, giữ các phiên cũ để phân tích chi phí thực tế.

### Xuất một run benchmark

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
