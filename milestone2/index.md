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
| **TV1** | Nhóm 6 | Kiến trúc trưởng, Hợp đồng & Orchestrator | `parsing/resolver.py`<br>`pipeline/parse.py` | Hợp đồng MS2, Bộ ghép mã nguồn TeX đa file, CLI điều phối `--stage parse`, Quản lý checkpoint & SHA-256 Resume. |
| **TV2** | Nhóm 6 | Phân tích Cấu trúc Phân cấp (Hierarchy Parser) | `parsing/hierarchy.py` | Ngăn xếp quản lý thứ bậc tiêu đề $O(N)$, Nhận diện tiêu đề định dạng PRL (`\textcolor+\textbf`), Trích xuất nút lá và cây sơ bộ `raw_tree.json`. |
| **TV3** | 24120318 | Chuẩn hóa Văn bản & Phân đoạn Câu (Normalization) | `parsing/normalization.py` | Pipeline làm sạch TeX đa tầng, Masking toán học tức thời (Private Use Area), Phân đoạn câu bảo vệ thực thể, Cây chuẩn hóa `normalized_tree.json`. |
| **TV4** | Nhóm 6 | Trích xuất BibTeX & Khử trùng lặp Xuyên phiên bản | `parsing/bibliography.py`<br>`parsing/deduplication.py` | Bộ phân tích `\bibitem` regex + `.bib`, Khử trùng lặp 2 cấp (References & Toàn văn), Đổi tên `\cite{}`, Xuất 3 bảng dữ liệu và `occurrences.json`. |
| **TV5** | 24120330 | Thẩm định Chất lượng, Đo lường & Báo cáo | `reporting/milestone2/validation.py`<br>`export/benchmark.py` | Động cơ kiểm định QA nghiêm ngặt, Đối chiếu đa tập (Multiset Equivalence), Giám sát tài nguyên nền (`psutil`), Jupyter Book Report. |

---

## 3. Các Chỉ số Đạt được Cốt lõi

- **Độ tin cậy kiểm thử phần mềm:** **432+ unit tests** và kiểm thử tích hợp trên toàn repository `arxiv-data-science` đạt trạng thái **100% Passed** (thời gian chạy $< 20$ giây).
- **Tỷ lệ nén sau Khử trùng lặp (Deduplication Efficiency):**
  - Giảm **$45.56\%$** số lượng phần tử văn bản (`elements`) nhờ tái sử dụng mã phần tử giữa các phiên bản bài báo.
  - Giảm **$44.23\%$** số lượng mục tài liệu tham khảo (`bibtex`) nhờ hợp nhất các khóa trích dẫn trùng lặp.
  - Thực hiện đổi tên đồng bộ **$18,940$** lượt gọi trích dẫn `\cite{...}` trong thân bài báo về khóa đại diện duy nhất.
- **Hiệu năng thực thi trên Google Colab CPU-only:**
  - Thời gian xử lý trung bình: **$0.4125$ giây / bài báo**.
  - Bộ nhớ RAM tiêu thụ cực đại (**Peak RAM**): **$642.8\text{ MB}$** (chiếm $< 5.1\%$ tổng RAM khả dụng của Google Colab).
  - Dung lượng lưu trữ đĩa 3 bảng đầu ra: **$84.6\text{ MB}$** cho 1,000 ấn phẩm nghiên cứu.
- **Tính toàn vẹn dữ liệu:** **100%** bài báo và phiên bản vượt qua bộ kiểm định QA độc lập của TV5, không phát sinh lỗi schema, không có cạnh tự trỏ, đồ thị cây hoàn toàn không chu trình.

---

## 4. Cấu trúc Chương Báo cáo

Nội dung chi tiết của Milestone 2 được trình bày qua các mục:
- [**Mục tiêu & Luồng xử lý Dữ liệu**](introduction.md): Bối cảnh học thuật, mô hình luồng 5 trạm và hợp đồng envelope Schema 2.0.
- [**Phương pháp Triển khai & Hợp đồng Kỹ thuật**](methodology.md): Thuyết minh chuyên sâu giải thuật của cả 5 thành viên (Resolver, Hierarchy, Normalization, Deduplication, Validation & Benchmark).
- [**Thống kê Phân tích Thực nghiệm**](statistics.ipynb): Notebook tương tác phân tích độ bao phủ, phân phối thành phần cú pháp và hiệu quả khử trùng lặp.
- [**Đo lường Hiệu năng Phần cứng**](performance.ipynb): Notebook tương tác đo đạc thời gian, bộ nhớ Peak/Average RAM và dung lượng đĩa trên Colab CPU-only.
- [**Thảo luận, Phân tích Trường hợp Biên & Sẵn sàng cho MS3**](discussion.md): Đánh giá 7 nhóm ca biên phức tạp, bài học gỡ lỗi qua 11 issue review và điều kiện chuyển tiếp sang Milestone 3.
