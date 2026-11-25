# Milestone 2 — Phân tích Cú pháp Phân cấp & Chuẩn hóa Dữ liệu

Chương này trình bày toàn bộ kết quả phân tích cú pháp phân cấp, chuẩn hóa và khử trùng lặp dữ liệu LaTeX từ Corpus bài báo khoa học đã thu thập ở Milestone 1.

---

## 1. Tóm tắt Tổng quan (Executive Summary)

Trong Milestone 2, Nhóm 6 đã thiết kế và triển khai thành công hệ thống đường ống phân tích cú pháp tự động hóa 5 trạm (**5-Stage Hierarchical Parsing & Standardization Pipeline**) nhằm chuyển đổi mã nguồn TeX phi cấu trúc thành cấu trúc cây phân cấp ngữ nghĩa chuẩn hóa và xuất bản 3 bảng dữ liệu quan hệ cốt lõi phục vụ bài toán tra cứu trích dẫn ở Milestone 3:
1. **Bảng `elements`:** Lưu trữ các phần tử nội dung độc nhất xuyên suốt các phiên bản (`document`, `heading`, `sentence`, `block_formula`, `figure`, `itemize`, `item`).
2. **Bảng `hierarchy`:** Lưu trữ các cạnh quan hệ cha - con phân cấp theo từng phiên bản (đúng chuẩn 4 cột: `arxiv_id`, `version`, `element_id`, `parent_id`).
3. **Bảng `bibtex`:** Danh mục tài liệu tham khảo được trích xuất từ `\bibitem` / `.bib`, hợp nhất thông tin và khử trùng lặp về một khóa duy nhất (`chosen_key`).

```text
[Corpus MS1 (Multi-file TeX)]
            │
            ▼
┌─────────────────────────┐
│   Trạm 1: Resolver      │ ──► gathered.json (merged_body_tex, raw_bibitems, .bib)
│        (TV1)            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   Trạm 2: Hierarchy     │ ──► raw_tree.json (Heading stack, leaf nodes)
│        (TV2)            │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐         ┌─────────────────────────┐
│  Trạm 3: Normalization  │         │  Trạm 4A: Bibliography  │
│        (TV3)            │         │        (TV4)            │
└───────────┬─────────────┘         └───────────┬─────────────┘
            │ normalized_tree                   │ raw_bibtex
            └─────────────────┬─────────────────┘
                              ▼
                  ┌─────────────────────────┐
                  │ Trạm 4B: Deduplication  │ ──► tables/{elements, hierarchy, bibtex}.json
                  │        (TV4)            │     references.bib & occurrences.json
                  └───────────┬─────────────┘
                              │
                              ▼
                  ┌─────────────────────────┐
                  │   Trạm 5: Validation    │ ──► validation/<key>.json & Benchmark
                  │        (TV5)            │     Jupyter Book Report
                  └─────────────────────────┘
```

---

## 2. Phân công Trách nhiệm Thành viên (Task Allocation)

Hệ thống được phát triển theo mô hình phân tầng module độc lập, giao tiếp thông qua hợp đồng dữ liệu chuẩn `docs/MS2_CONTRACTS.md` (Schema 2.0):

| Thành viên | MSSV | Vai trò chính | Module phụ trách | Sản phẩm cốt lõi bàn giao |
| :--- | :--- | :--- | :--- | :--- |
| **TV1** | Đang cập nhật | Kiến trúc trưởng, Hợp đồng & Orchestrator | `parsing/resolver.py`<br>`pipeline/parse.py` | Hợp đồng MS2, Bộ ghép mã nguồn TeX đa file, CLI điều phối `--stage parse`, Quản lý checkpoint & SHA-256 Resume. |
| **TV2** | Đang cập nhật | Phân tích Cấu trúc Phân cấp (Hierarchy Parser) | `parsing/hierarchy.py` | Ngăn xếp quản lý thứ bậc tiêu đề $O(N)$, Nhận diện tiêu đề định dạng PRL (`\textcolor+\textbf`), Trích xuất nút lá và cây sơ bộ `raw_tree.json`. |
| **TV3** | 24120318 | Chuẩn hóa Văn bản & Phân đoạn Câu (Normalization) | `parsing/normalization.py` | Pipeline làm sạch TeX đa tầng, Masking toán học tức thời (Private Use Area), Phân đoạn câu bảo vệ thực thể, Cây chuẩn hóa `normalized_tree.json`. |
| **TV4** | Đang cập nhật | Trích xuất BibTeX & Khử trùng lặp Xuyên phiên bản | `parsing/bibliography.py`<br>`parsing/deduplication.py` | Bộ phân tích `\bibitem` regex + `.bib`, Khử trùng lặp 2 cấp (References & Toàn văn), Đổi tên `\cite{}`, Xuất 3 bảng dữ liệu và `occurrences.json`. |
| **TV5** | 24120330 | Thẩm định Chất lượng, Đo lường & Báo cáo | `reporting/milestone2/validation.py`<br>`export/benchmark.py` | Động cơ kiểm định QA nghiêm ngặt, Đối chiếu đa tập (Multiset Equivalence), Giám sát tài nguyên nền (`psutil`), Jupyter Book Report. |

---

## 3. Kết quả Thực nghiệm Toàn nhóm (25.000 Bài báo — 5 Thành viên)

Toàn bộ 5 thành viên (TV1 – TV5) đã hoàn tất chạy đường ống Milestone 2 trên toàn bộ dải phân công **25.000 bài báo** (**40.677 phiên bản**, snapshot ngày 20–21/11/2026 trên **Google Colab CPU-only**) và xuất bản 5 gói kết quả `MS2_RESULTS.zip` kèm mã kiểm SHA-256. Số liệu dưới đây được tổng hợp trực tiếp từ `summaries/parsing_summary.json`, `summaries/parse-run.json`, `manifests/stages.json` và `delivery.json` của cả 5 thành viên (lưu trong `summaries/milestone2/whole_team_summary.json`):

| Thành viên | Dải ID arXiv | Đã parse TeX (`success`) | PDF-only (`no_source`) | Đạt QA hoàn chỉnh | Chưa hoàn chỉnh (`incomplete`) | Giảm `elements` | Giảm `bibtex` | Peak RAM (MB) | Dung lượng 3 bảng (MB) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **TV1** | `2508.12872:2508.17871` | 3.334 (66,68%) | 391 (7,82%) | **3.725 (74,50%)** | 1.275 (25,50%) | 30,93% | 36,35% | 1.757,20 | 734,79 |
| **TV2** | `2506.15788:2506.20787` | 3.247 (64,94%) | 373 (7,46%) | **3.620 (72,40%)** | 1.380 (27,60%) | 31,69% | 37,18% | 3.561,79 | 730,13 |
| **TV3** | `2411.08799:2411.13798` | 3.158 (63,16%) | 428 (8,56%) | **3.586 (71,72%)** | 1.414 (28,28%) | 32,28% | 38,10% | 920,60 | 719,66 |
| **TV4** | `2410.18025:2410.23024` | 3.277 (65,54%) | 385 (7,70%) | **3.662 (73,24%)** | 1.338 (26,76%) | 34,75% | 39,12% | 967,61 | 789,65 |
| **TV5** | `2410.03025:2410.08024` | 3.305 (66,10%) | 343 (6,86%) | **3.648 (72,96%)** | 1.352 (27,04%) | 35,13% | 40,63% | 1.970,39 | 790,29 |
| **Toàn nhóm** | **25.000 ID (40.677 version)** | **16.321 (65,28%)** | **1.920 (7,68%)** | **18.241 (72,96%)** | **6.759 (27,04%)** | **33,04%** | **38,36%** | **3.561,79 (max)** | **3.764,52 (3,68 GB)** |

**Các phát hiện định lượng chính:**
- **Độ bao phủ & Chất lượng (QA):** Trong **25.000** bài được giao, có **18.241 bài (`72,96%`)** hoàn tất toàn bộ các phiên bản và vượt qua kiểm định QA nghiêm ngặt của TV5 (gồm **16.321** bài có mã nguồn TeX và **1.920** bài `no_source` được ghi nhận rỗng hợp lệ). Ở cấp phiên bản, **29.902 / 40.677** phiên bản (`73,51%`) parse thành công cả TeX lẫn BibTeX và **2.642** phiên bản (`6,50%`) là `no_source`.
- **Phân tách nguyên nhân `incomplete` (`6.759` bài — `27,04%`):**
  - **5.257 bài (`21,03%`)** dừng trước bước khử trùng lặp do có ít nhất một phiên bản lỗi ở Trạm 1 (`resolve`: 7.482 phiên bản `data_error` + 240 phiên bản thiếu upstream MS1) hoặc Trạm 4A (`bibliography`: 411 phiên bản `data_error`).
  - **1.501 bài (`6,00%`)** đã qua `deduplicate` nhưng bị `validate_parse` từ chối (**100% do sai lệch đối chiếu round-trip giữa `references.bib` và `bibtex.json`**, không có bất kỳ lỗi schema, chu trình cây hay khóa ngoại `hierarchy`/`occurrences` nào; tỷ lệ qua QA trên các bài đã deduplicate đạt **92,40%**).
  - **1 bài (`2506.19089` thuộc dải TV2)** vượt ngưỡng timeout 300 giây.
- **Hiệu quả Khử trùng lặp Xuyên phiên bản (trên 16.321 bài có TeX đạt QA):**
  - Giảm từ **9.821.396** xuống **6.576.538** phần tử nội dung (`elements`) — tiết kiệm **3.244.858 phần tử (`33,04%`)**.
  - Giảm từ **1.424.979** xuống **878.307** bản ghi tài liệu tham khảo (`bibtex`) — tiết kiệm **546.672 bản ghi (`38,36%`)**.
  - Đổi tên đồng bộ **20.568** lượt gọi `\cite{...}` xuyên phiên bản về khóa đại diện `chosen_key`.
- **Tài nguyên & Lưu trữ trên Google Colab CPU-only (2 vCPU Xeon 2,20 GHz, 12,67 GB RAM):**
  - **Peak RAM** trong cả 5 phiên dao động từ **920,60 MB** đến **3.561,79 MB** (tối đa **27,45%** giới hạn RAM Colab), vận hành ổn định không OOM trên toàn bộ 25.000 bài.
  - **Tổng dung lượng 3 bảng đầu ra chưa nén:** **3.764,52 MB (`3,68 GB`)**; tổng 5 gói nén `MS2_RESULTS.zip` xuất bản đạt **4.412,34 MB (`4,31 GB`)**.
  - **Lưu ý về thời gian thực thi:** Các phiên chạy sử dụng `resume=True` với số bài đã cache (`skipped_completed_papers`) khác nhau giữa 5 thành viên (từ 39 bài ở TV5 đến 3.586 bài ở TV3); chi tiết phạm vi đo được tách bạch rõ trong trang [Đo lường Hiệu năng Phần cứng](performance.ipynb).

---

## 4. Cấu trúc Chương Báo cáo

Nội dung chi tiết của Milestone 2 được trình bày qua các mục:
- [**Mục tiêu & Luồng xử lý Dữ liệu**](introduction.md): Bối cảnh học thuật, mô hình luồng 5 trạm và hợp đồng envelope Schema 2.0.
- [**Phương pháp Triển khai & Hợp đồng Kỹ thuật**](methodology.md): Thuyết minh chuyên sâu giải thuật của cả 5 thành viên (Resolver, Hierarchy, Normalization, Deduplication, Validation & Benchmark).
- [**Thống kê Phân tích Cú pháp & Khử trùng lặp**](statistics.ipynb): Notebook phân tích thực nghiệm toàn nhóm (25.000 bài báo): độ bao phủ, hiệu quả khử trùng lặp, phễu 6 stage, phân loại lỗi và ảnh hưởng số phiên bản.
- [**Đo lường Hiệu năng Phần cứng**](performance.ipynb): Notebook phân tích thời gian thực thi theo phạm vi resume, Peak/Average RAM và dung lượng lưu trữ trên Colab CPU-only.
- [**Thảo luận, Phân tích Trường hợp Biên & Sẵn sàng cho MS3**](discussion.md): Đánh giá 7 nhóm ca biên, 11 issue review, phân tích thực nghiệm nguyên nhân 6.759 bài chưa hoàn chỉnh và điều kiện chuyển tiếp sang Milestone 3.
