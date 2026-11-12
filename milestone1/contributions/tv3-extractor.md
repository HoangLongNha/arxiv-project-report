# BÁO CÁO CÔNG VIỆC THÀNH VIÊN 3 (TV3) — MILESTONE 1
## ĐỒ ÁN NHẬP MÔN KHOA HỌC DỮ LIỆU — NHÓM 6

> **Lưu ý nguồn tư liệu:** Nội dung và kết quả kiểm thử trong trang này do TV3 tự báo cáo. Kết quả này minh họa kiểm thử module, **không thay thế benchmark corpus toàn nhóm**. Thông tin định danh cá nhân không thiết yếu được lược bỏ trong bản dành cho website công khai.

---

### 1. THÔNG TIN CHUNG
- **Họ và tên:** Trịnh Văn Hợp
- **Vai trò đảm nhiệm:** **TV3 — File Processing & Corpus Builder**
- **Module phụ trách:** `src/arxiv_pipeline/crawling/extractor.py`
- **Bộ kiểm thử:** `tests/crawling/test_extractor.py`
- **Nhánh phát triển:** `feature/tv3-file-processing`
- **Pull Request:** PR #5 *(Đã merge vào `main` tại commit `5715188`)*

---

### 2. MỤC TIÊU & NHIỆM VỤ ĐƯỢC GIAO
Theo kế hoạch Milestone 1 và hợp đồng dữ liệu tại `docs/CONTRACTS.md`, TV3 chịu trách nhiệm xử lý các gói mã nguồn thô (raw source) do TV2 (Downloader) tải về từ arXiv:
1. **Giải nén an toàn:** Nhận diện và giải nén các tệp nén (`tar.gz`, `tar`, `gz`, hoặc plain text), tuyệt đối ngăn chặn lỗ hổng bảo mật **Zip-Slip / Path Traversal**.
2. **Lọc sạch dữ liệu Corpus:** Chỉ giữ lại các tệp mã nguồn LaTeX (`.tex`) và thư viện trích dẫn BibTeX (`.bib`). Loại bỏ toàn bộ các file nhị phân, hình ảnh (`.png`, `.jpg`, `.pdf`, `.eps`) và file phụ trợ biên dịch (`.aux`, `.log`, `.out`).
3. **Bảo toàn tính nguyên bản:** Không chỉnh sửa, không thay đổi bất kỳ ký tự hoặc lệnh nào trong các tệp LaTeX (kể cả các lệnh chèn hình `\includegraphics`).
4. **Phân lập theo phiên bản:** Xây dựng corpus tách biệt theo từng phiên bản (`corpus/<paper_key>/vN/`), đảm bảo `v1` và `v2` không ghi đè lên nhau.
5. **Ghi nguyên tử (Atomic Commit):** Sử dụng thư mục tạm `.staging` để đảm bảo dữ liệu corpus không bị rách (corrupted) nếu tiến trình bị dừng đột ngột hoặc khi sử dụng cờ `--force`.
6. **Sinh dữ liệu kiểm chứng (Sidecar Metadata):** Ghi file `extract_metadata.json` lưu trữ dung lượng trước/sau lọc, danh sách tệp được giữ lại và thời gian xử lý.
7. **Tích hợp Adapter:** Cung cấp hàm `run()` trả về đối tượng `StageResult` tuân thủ đúng hợp đồng hệ thống.

---

### 3. KIẾN THỨC ĐÃ TÌM HIỂU & ÁP DỤNG
- **Thư viện chuẩn Python (Standard Library):** Sử dụng `tarfile`, `gzip`, `pathlib.Path`, `shutil`, `os` — hoàn toàn không phát sinh dependency bên ngoài, bảo đảm tính nhẹ và tương thích cao.
- **Lỗ hổng Zip-Slip (Path Traversal in Archives):** Nghiên cứu kỹ thuật kẻ tấn công chèn các đường dẫn `../` hoặc đường dẫn tuyệt đối vào trong tệp archive để ghi đè tệp hệ thống ngoài thư mục dự định. Triển khai thuật toán kiểm tra nghiêm ngặt `Path.resolve().is_relative_to()`.
- **Cấu trúc gói mã nguồn arXiv:** Phân tích các dạng gói source thực tế trên arXiv:
  - Gói đa tệp: thường nén dưới dạng `tar.gz` hoặc `tar`.
  - Gói đơn tệp: thường là một file TeX đơn lẻ được nén gzip (`.gz`) (phổ biến với các bài báo trước năm 2007).
  - Gói dạng text: mã nguồn TeX thuần chưa qua nén.
  - Gói chỉ có PDF (PDF-only): không có mã nguồn TeX, cần trả trạng thái `no_source` thay vì báo lỗi hệ thống.
- **Quy trình làm việc nhóm chuyên nghiệp trên GitHub:** Làm việc trên branch riêng `feature/tv3-file-processing`, tuân thủ quy tắc commit rõ ràng, viết unit test đầy đủ trước khi tạo Pull Request và nhờ thành viên khác review trước khi merge vào `main`.

---

### 4. CHI TIẾT MÃ NGUỒN ĐÃ TRIỂN KHAI

#### 4.1. Module trích xuất: `src/arxiv_pipeline/crawling/extractor.py` (347 dòng code)
Bao gồm các hàm chức năng nòng cốt:

* **Kiểm tra an toàn đường dẫn:**
  ```python
  def is_safe_path(base_dir: Path, target_path: Path) -> bool:
      """Xác thực target_path phải luôn nằm trọn vẹn bên trong base_dir."""
  ```
* **Chặn đứng Path Traversal khi duyệt tar member:**
  ```python
  def _check_tar_member(member: tarfile.TarInfo, dest_dir: Path) -> Path:
      """Chặn đường dẫn tuyệt đối, ổ đĩa C:\, ký tự '..' và symlink nguy hiểm."""
  ```
* **Giải nén đa định dạng:**
  - `safe_extract_tar()`: Duyệt qua từng member, kiểm tra an toàn rồi mới trích xuất.
  - `safe_extract_gz()`: Giải nén file `.gz` đơn lẻ thành file `.tex`.
  - `safe_extract_plain_tex()`: Sao chép an toàn file văn bản thô.
* **Bộ lọc Corpus (`filter_corpus`):**
  - Quét đệ quy toàn bộ thư mục đã giải nén.
  - Chỉ đưa vào danh sách các file có đuôi `.tex` hoặc `.bib` (không phân biệt hoa thường).
  - Tự động xóa các file khác (ảnh `.png`, `.jpg`, `.pdf`, mã nhị phân, file tạm `.aux`).
  - Dọn dẹp sạch các thư mục rỗng sau khi đã lọc.
* **Quy trình giải nén nguyên tử (`extract_source`):**
  - Bước 1: Tạo thư mục tạm `corpus/<paper_key>/.vN.staging`.
  - Bước 2: Giải nén và lọc file bên trong thư mục staging.
  - Bước 3: Đổi tên (atomic rename) từ `.vN.staging` thành `vN/`.
  - Bước 4: Tạo sidecar metadata `extract_metadata.json`.
* **Giao diện Adapter chuẩn (`run`):**
  - Tự động lấy đường dẫn tải từ `upstream['artifacts']['source']` do TV2 bàn giao.
  - Phân loại lỗi chuẩn xác:
    - `success`: Có file `.tex`/`.bib`.
    - `no_source`: Nguồn gốc là PDF-only hoặc archive không chứa TeX.
    - `data_error`: Archive bị hỏng (corrupted) hoặc phát hiện vi phạm bảo mật Zip-Slip.
    - `error`: Lỗi I/O không lường trước.

#### 4.2. Cấu trúc đầu ra của TV3
```text
corpus/
  └── 2301.00001/
      ├── v1/
      │   ├── main.tex
      │   ├── references.bib
      │   ├── sub/
      │   │   └── chapter1.tex
      │   └── extract_metadata.json
      └── v2/
          ├── main.tex
          └── extract_metadata.json
```

Nội dung file `extract_metadata.json`:
```json
{
  "extracted_files": [
    "main.tex",
    "references.bib",
    "sub/chapter1.tex"
  ],
  "raw_size_bytes": 1048576,
  "corpus_size_bytes": 245760,
  "file_count": 3,
  "extracted_at": "2026-10-27T13:20:00Z"
}
```

---

### 5. KẾT QUẢ KIỂM THỬ & NGHIỆM THU

Đã xây dựng bộ unit test toàn diện tại `tests/crawling/test_extractor.py` với **11 ca kiểm thử**, tất cả đều đạt kết quả **PASS 100%**:

| STT | Tên Test Case | Mô tả kiểm thử | Kết quả |
| :---: | :--- | :--- | :---: |
| 1 | `test_is_safe_path` | Kiểm tra thuật toán phát hiện và ngăn chặn path traversal. | **PASS** |
| 2 | `test_path_traversal_attack_blocked` | Chặn đứng tệp nén độc hại chứa `../escape.txt`, bảo vệ an toàn hệ thống. | **PASS** |
| 3 | `test_safe_tar_gz_extract_and_filter` | Giải nén gói `tar.gz`, giữ đúng `.tex`/`.bib`, lọc sạch toàn bộ ảnh `.png`, file PDF và `.aux`. | **PASS** |
| 4 | `test_safe_gz_single_tex_extract` | Giải nén chính xác tệp `.tex` đơn lẻ nén định dạng `.gz`. | **PASS** |
| 5 | `test_plain_tex_extract` | Đọc và xử lý đúng mã nguồn LaTeX dạng plain text chưa nén. | **PASS** |
| 6 | `test_pdf_only_source_returns_no_source` | Phát hiện tệp chỉ có PDF, gán nhãn trạng thái chuẩn `no_source`. | **PASS** |
| 7 | `test_archive_without_tex_returns_no_source` | Archive hợp lệ nhưng không có tệp LaTeX nào $\rightarrow$ trả về `no_source`. | **PASS** |
| 8 | `test_corrupt_archive_returns_data_error` | Bắt lỗi archive hỏng byte, phân loại chính xác `data_error` mà không làm crash pipeline. | **PASS** |
| 9 | `test_multi_version_isolation` | Kiểm tra trích xuất độc lập các phiên bản `v1` và `v2` của cùng một bài báo mà không bị ghi đè. | **PASS** |
| 10 | `test_adapter_run_integration` | Kiểm tra hàm `run()` trả về `StageResult` có `artifacts={'corpus': ...}` chuẩn hợp đồng. | **PASS** |
| 11 | `test_pipeline_crawl_integration` | Kiểm tra tích hợp liên thông với Discovery, Downloader, Metadata, References và Validation. | **PASS** |

#### Kiểm tra liên thông toàn bộ Pipeline (End-to-End):
Đã chạy thử nghiệm luồng đầy đủ từ Discovery $\rightarrow$ Downloader $\rightarrow$ **Extractor (TV3)** $\rightarrow$ Metadata $\rightarrow$ References $\rightarrow$ Validation. Báo cáo kiểm định của TV5 (`validation.py`) xác nhận:
```text
valid = True, counts = {'versions': 2, 'source_versions': 2, 'no_source_versions': 0, 'source_files': 4, 'references': 1}
Pipeline summary: complete = True, stage_statuses = {'success': 7}
```

---

### 6. ĐÓNG GÓP & TRẠNG THÁI TRÊN GITHUB
- **Branch:** `feature/tv3-file-processing`
- **Commit:** `79dcd6e` — *feat: implement TV3 safe corpus extractor and unit tests*
- **Pull Request:** [PR #5](https://github.com/LeoTkiet/arxiv-data-science/pull/5) — *Merge pull request #5 from LeoTkiet/feature/tv3-file-processing (Commit `5715188`)*
- **Tình trạng nghiệm thu:** **ĐÃ HOÀN THÀNH 100% VÀ ĐÃ MERGE VÀO NHÁNH `main` CỦA REPO DỰ ÁN.**
