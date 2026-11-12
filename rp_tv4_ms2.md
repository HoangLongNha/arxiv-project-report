# BÁO CÁO MILESTONE 2 — THÀNH VIÊN 4 (TV4)
## PHẦN: TRÍCH XUẤT BIBTEX VÀ KHỬ TRÙNG LẶP XUYÊN PHIÊN BẢN

> **Mục đích báo cáo:** Trình bày phần việc TV4 thực hiện trong Milestone 2 của dự án `arxiv-data-science`: chuyển các mục tham khảo (`\bibitem` và tệp `.bib`) sang BibTeX chuẩn, khử trùng lặp tài liệu tham khảo xuyên các phiên bản (chọn một khóa, hợp nhất trường, đổi tên `\cite{}`), khử trùng lặp nội dung toàn văn, và xuất ba bảng `elements`, `hierarchy`, `bibtex`. Báo cáo ghi rõ điều nào **đề bài yêu cầu**, điều nào là **quy ước của nhóm** (đề không nói), và phân biệt số liệu đo được trên dữ liệu thật với kết quả kiểm thử bằng dữ liệu mô phỏng.

---

## 1. MỤC TIÊU VÀ PHẠM VI CÔNG VIỆC

### 1.1. Vai trò của TV4
Theo hợp đồng `docs/MS2_CONTRACTS.md` (TV1), TV4 phụ trách hai stage ở cuối chuỗi parsing:

- **`bibliography`** (cấp version): đọc kết quả của Resolver, trích xuất mọi tài liệu tham khảo của version đó thành các hàng BibTeX.
- **`deduplicate`** (cấp paper): nhận kết quả của mọi version (cây đã chuẩn hóa từ TV3 và BibTeX thô từ `bibliography`), khử trùng lặp hai cấp và ghi ra ba bảng đầu ra cùng tệp phụ trợ.

Cả hai đều theo chữ ký adapter chung `run(record, output_dir, *, version=None, upstream=None) -> StageResult` với `schema_version="2.0"`.

### 1.2. Phạm vi đã triển khai

| Hạng mục | Trạng thái |
| --- | --- |
| Chuyển `\bibitem` sang BibTeX bằng regex | Đã triển khai (`parsing/bibliography.py`) |
| Đọc tệp `.bib` bằng `bibtexparser` | Đã triển khai |
| Khử trùng lặp tài liệu tham khảo, hợp nhất trường, chọn một khóa | Đã triển khai (`parsing/deduplication.py`) |
| Đổi tên mọi lệnh `\cite` về khóa đã chọn | Đã triển khai |
| Khử trùng lặp nội dung toàn văn, sinh `elements`, `hierarchy`, `occurrences` | Đã triển khai |
| Xuất `references.bib` và `parsing_manifest.json` | Đã triển khai |
| Unit test offline | 56 test (16 bibliography + 40 deduplication) |
| Chạy thật trên dữ liệu | Một paper một version (`2410.08024`); chưa chạy toàn corpus (mục 8) |

---

## 2. KIẾN TRÚC MODULE

### 2.1. Cấu trúc file

```text
src/arxiv_pipeline/parsing/
├── bibliography.py     # parse_bibitem, parse_bib_text, run (stage `bibliography`)
└── deduplication.py    # unionize_bibtex, rename_citations, deduplicate_elements_and_build_hierarchy, run (stage `deduplicate`)
tests/parsing/
├── test_bibliography.py
└── test_deduplication.py
```

### 2.2. Đường đi dữ liệu

```text
Resolver (TV1) ── gathered.json ──► bibliography (mỗi version)
                                      │   raw_bibitems  ─► parse_bibitem (regex)
                                      │   .bib được \bibliography tham chiếu ─► parse_bib_text (bibtexparser)
                                      ▼
                         parsed/<key>/vN/raw_bibtex.json (+ provenance)
                                      │
Normalization (TV3) ── normalized_tree.json (mỗi version)
                                      │
                                      ▼
                     deduplicate (cấp paper, mọi version cùng lúc)
        ┌─────────────────────────────┴───────────────────────────────┐
        │ Cấp 1: gộp BibTeX trùng → key_mapping, hợp nhất trường      │
        │ Rename \cite{} trong mọi nút của cây (TRƯỚC khi so nội dung) │
        │ Cấp 2: gộp nút cùng (kind, nội dung) → một element_id       │
        └─────────────────────────────┬───────────────────────────────┘
                                      ▼
     tables/<key>/{elements,hierarchy,bibtex}.json + references.bib + parsing_manifest.json
     parsed/<key>/vN/occurrences.json
```

### 2.3. Nguyên tắc thiết kế
- **Không đoán dữ liệu.** Trường nào không tách chắc chắn thì để trống (`""`, `[]`, `null`) và lưu nguyên văn bản gốc ở tệp provenance.
- **Không đổi hợp đồng của người khác.** Dùng đúng `ElementRow`, `HierarchyRow`, `BibtexRow` trong `common/schemas.py`; không thêm cột vào ba bảng.
- **Ghi atomic, chỉ ghi khi đủ điều kiện.** Một version chưa sẵn sàng làm cả paper `skipped`, không ghi bảng dở dang.
- **Đường dẫn an toàn.** Mọi đường dẫn đọc/ghi đi qua `safe_join`, từ chối đường dẫn tuyệt đối, `..` và symlink thoát khỏi root.

---

## 3. STAGE `bibliography`

### 3.1. Đầu vào và nguồn tham khảo

| Nguồn | Cách xử lý |
| --- | --- |
| `raw_bibitems` trong `gathered.json` | Từng khối `\bibitem` được `parse_bibitem` chuyển thành hàng BibTeX |
| `.bib` trong `referenced_bib_file_paths` (được lệnh `\bibliography` nhắc tới) | Đọc bằng `parse_bib_text` |
| Nếu danh sách trên rỗng | Đọc mọi `.bib` trong `bib_file_paths`, để version không có TeX (chỉ còn `.bib`) vẫn giữ được tài liệu tham khảo, theo hợp đồng TV1 |

### 3.2. Chuyển `\bibitem` bằng regex
Hàm `parse_bibitem` bóc từng trường:

| Trường | Cách lấy |
| --- | --- |
| `citation_key` | `\bibitem[nhãn]{key}`, bỏ phần nhãn tùy chọn |
| `doi` | `doi:`, `\doi{}` hoặc URL `doi.org/…` |
| `url` | `\url{}`, `\href{}` hoặc URL trần (không lấy link `doi.org`) |
| `year` | năm 18xx–20xx cuối cùng, **sau khi loại số arXiv** (để `2010.11929` không bị đọc là năm 2010) |
| `title`, `authors`, `journal` | theo kiểu có `\newblock` (tác giả / tiêu đề / nơi đăng) hoặc kiểu tiêu đề trong ngoặc kép; tên tác giả dạng `Doe, J.` được giữ nguyên cặp |

Quy ước quan trọng: một `\bibitem` viết tay **không cho biết loại ấn phẩm**, nên `entry_type` luôn là `misc`, không suy ra `article` chỉ vì có tên tạp chí. Khi không tách chắc chắn (ví dụ văn bản tự do không có `\newblock` hay ngoặc kép), `title=""`, `authors=[]` và chỉ trường chắc chắn (như `year`) được điền. Nguyên văn nằm trong `raw_bibtex.provenance.json` cùng danh sách trường đã tách được.

### 3.3. Đọc tệp `.bib`
`parse_bib_text` dùng `bibtexparser` (>=1.4, <2), thư viện được import muộn nên thiếu thư viện chỉ làm stage này lỗi. Quy tắc chuẩn hóa: tên `Last, First` đổi thành `First Last`; `year` thành số nguyên khi có bốn chữ số; DOI bỏ tiền tố `https://doi.org/`; `journal` lấy từ `journal` hoặc `booktitle`; `entry_type` viết thường theo loại gốc. Số entry khai báo (`@loại{`) lớn hơn số entry parse được thì ghi cảnh báo `bib_entries_unparsed`.

### 3.4. Trạng thái trả về

| Điều kiện | Status | Ghi chú |
| --- | --- | --- |
| Có ít nhất một entry | `success` | |
| Không có entry nào | `no_source` | Nếu version có TeX mà không có nguồn tham khảo thì thêm cảnh báo `bib_source_missing` |
| Resolve chưa sẵn sàng hoặc lỗi | `skipped` | Giữ nguyên nguyên nhân upstream |
| Envelope, danh tính hoặc đường dẫn sai | `data_error` | |
| Lỗi I/O | `error` | |

Đầu ra: `parsed/<key>/vN/raw_bibtex.json` (`entries` + `warnings`) và `raw_bibtex.provenance.json`.

---

## 4. STAGE `deduplicate` — CẤP 1: TÀI LIỆU THAM KHẢO

### 4.1. Khi nào hai entry là cùng một tài liệu
Đề chỉ nói "cùng nội dung tham khảo" mà không định nghĩa. Nhóm dùng ba tín hiệu, gộp bắc cầu bằng union-find trong phạm vi một paper (cả trong cùng version lẫn xuyên version):

| Tín hiệu | Chi tiết |
| --- | --- |
| Cùng `citation_key` | Xuyên version, cùng key được coi là cùng tài liệu |
| Cùng DOI | Chuẩn hóa: bỏ tiền tố URL và không phân biệt hoa/thường |
| Cùng tiêu đề chuẩn hóa | Bỏ lệnh LaTeX, dấu câu, hoa/thường; **chỉ khi dài từ 15 ký tự** (tiêu đề quá ngắn như "Survey" không đủ chứng minh là cùng một tài liệu) |

### 4.2. Chọn khóa và hợp nhất trường
- **Khóa được chọn** là khóa xuất hiện sớm nhất (version nhỏ nhất, rồi thứ tự trong version). Đề chỉ yêu cầu "một khóa duy nhất" và không quy định chọn khóa nào.
- **Hợp nhất (union):** trường nào của entry đầu còn trống thì lấy từ entry sau; `entry_type = misc` (mặc định của `\bibitem`) nhường cho loại cụ thể hơn.
- **Khi hai entry có giá trị khác nhau cho cùng một trường:** giữ giá trị của entry sớm nhất, bỏ giá trị kia và ghi cảnh báo `bib_field_conflict` vào `parsing_manifest.json`. Đề không nói gì về trường hợp này. Hai giá trị coi là giống nhau nếu chỉ khác hoa/thường hoặc dấu câu (tiêu đề), tiền tố URL (DOI) hay hoa/thường (tác giả).

### 4.3. Đổi tên `\cite{}`
`rename_citations` đổi khóa bên trong mọi lệnh họ trích dẫn: `\cite`, `\citep`, `\citet`, `\citealp`, `\citealt`, `\citeauthor`, `\citeyear`, `\citeyearpar`, `\citenum`, `\nocite`, `\parencite`, `\textcite`, `\autocite`, `\footcite`, `\smartcite` (kể cả dạng `*`, đối số tùy chọn `[…]`, và nhiều khóa `{a,b}`). Nếu sau khi đổi hai khóa của cùng một lệnh trở thành một thì chỉ giữ một. Khóa không có trong bảng tham khảo được giữ nguyên và ghi cảnh báo `citation_key_unknown`. Bước này **chạy trước** khi so khớp nội dung văn bản, đúng thứ tự mà đề yêu cầu (so khớp toàn văn sau cleanup).

---

## 5. STAGE `deduplicate` — CẤP 2: NỘI DUNG TOÀN VĂN

### 5.1. Quy tắc dùng chung một phần tử
Các nút của cây chuẩn hóa được xét theo cặp `(kind, cleaned_content)` (sau khi đã đổi `\cite`). Cùng cặp trong cùng một paper thì dùng **chung một `element_id`**, kể cả xuyên version. Nút gốc `document` không bị gộp mà mỗi version có một gốc riêng.

### 5.2. Mã phần tử
`<paper_key>#<tiền tố><số>` với `paper_key` là ID có `.` đổi thành `-` và `/` thành `_` (ví dụ `2310-12345#s1`). Tiền tố theo loại nút:

| `kind` | Tiền tố | `kind` | Tiền tố |
| --- | --- | --- | --- |
| `document` | `root<version>` | `block_formula` | `eq` |
| `heading` | `h` | `figure` (gồm bảng) | `fig` |
| `sentence` | `s` | `itemize` / `item` | `list` / `item` |

Số thứ tự tăng theo từng loại, theo thứ tự version tăng dần và thứ tự duyệt cây trước-sau (cha trước con, con theo `position`), nên kết quả ổn định giữa các lần chạy.

### 5.3. Bảng `hierarchy` và `occurrences`
- Mỗi cạnh nút-cha của từng version là một hàng `HierarchyRow(arxiv_id, version, element_id, parent_id)`. Gốc không có hàng riêng, nên `parent_id` không bao giờ rỗng.
- **Không loại hàng trùng:** nếu hai câu giống nhau cùng nằm dưới một tiêu đề, ta vẫn có hai cạnh.
- Vì cột của `hierarchy` không phân biệt được hai lần xuất hiện của cùng một phần tử, TV4 ghi thêm `parsed/<key>/vN/occurrences.json` (mã lần xuất hiện, cha, vị trí) làm nguồn sự thật về cấu trúc cây từng version. Bảng chính vẫn giữ đúng bốn cột theo đề.
- Cây sai (hai gốc, cha không tồn tại, vòng lặp, `temp_id` trùng, `kind` lạ) bị từ chối bằng `data_error` thay vì sinh bảng sai.

---

## 6. ĐẦU RA VÀ HỢP ĐỒNG

### 6.1. Tệp được ghi

| Tệp | Nội dung |
| --- | --- |
| `tables/<key>/elements.json` | Mảng `ElementRow` (`element_id`, `arxiv_id`, `kind`, `content`) |
| `tables/<key>/hierarchy.json` | Mảng `HierarchyRow` (`arxiv_id`, `version`, `element_id`, `parent_id`) |
| `tables/<key>/bibtex.json` | Mảng `BibtexRow` sau khi gộp và hợp nhất |
| `tables/<key>/references.bib` | Cùng dữ liệu bảng `bibtex`, ở cú pháp BibTeX chuẩn |
| `tables/<key>/parsing_manifest.json` | `expected_versions`, `complete`, trạng thái từng version, đường dẫn bảng, `counts`, `warnings` |
| `parsed/<key>/vN/occurrences.json` | Các lần xuất hiện của phần tử trong từng version |

`counts` gồm `elements_before/after` và `bibtex_before/after`, tính từ các artifact từng version chứ không suy ngược từ bảng cuối, để báo cáo thống kê "trước và sau dedup".

### 6.2. Trạng thái paper

| Điều kiện | Status |
| --- | --- |
| Có ít nhất một version parse được | `success` |
| Mọi version đều không có TeX (kể cả khi còn `.bib`) | `no_source`, bảng vẫn được xuất (rỗng hoặc chỉ còn `bibtex`) |
| Thiếu version, version lỗi hoặc chưa sẵn sàng | `skipped`, không ghi gì |
| Dữ liệu upstream sai danh tính hoặc cây không hợp lệ | `data_error` |

Một version `no_source` vẫn có mặt trong `manifest.versions` kèm lý do, đúng yêu cầu "ghi nhận là rỗng thay vì bỏ qua".

### 6.3. Phối hợp với TV5
Validator MS2 của TV5 (`reporting/milestone2/validation.py`) đối chiếu `references.bib` với `bibtex.json` từng entry một, và kiểm tra counts, `occurrences` so với `hierarchy`, tên bảng trong manifest so với artifact khai báo. Vì vậy `references.bib` và các artifact trên là một phần của hợp đồng giữa TV4 và TV5, không chỉ là đầu ra phụ.

---

## 7. HƯỚNG DẪN CHẠY

Cài dependency (có thêm `bibtexparser`) và chạy từ thư mục gốc repo:

```bash
python -m pip install -e ".[reporting,dev]"
python main.py --stage parse --ms1-input artifacts/ms1-snapshot --output artifacts/ms2 --ids 2410.08024 --resume
```

`artifacts/ms1-snapshot` là bản sao MS1 đã hoàn tất (discovery, checkpoint download/extract, source, corpus). MS1 và MS2 phải ở hai thư mục tách biệt. Chạy riêng test của TV4:

```bash
python -m pytest tests/parsing/test_bibliography.py tests/parsing/test_deduplication.py -q
```

---

## 8. KẾT QUẢ THỰC TẾ: PAPER `2410.08024` (v1)

### 8.1. Điều kiện
Dữ liệu là corpus của paper `2410.08024` (một version, `main.tex`, `si.tex`, `bibliografia.bib`). Tôi chạy trực tiếp `parse_bib_text` và `unionize_bibtex` của `main` trên tệp `bibliografia.bib` (98.784 byte) ngày 06/11/2026, không qua toàn bộ pipeline (không có checkpoint MS1 trong bộ dữ liệu tải về). Kết quả khớp số liệu mà TV1 ghi trong `docs/MS2_HANDOFF.md` cho lần chạy cả pipeline của họ.

### 8.2. Bảng tham khảo

| Chỉ số | Giá trị |
| --- | ---: |
| Entry trong `.bib` (trừ `@string`/`@comment`) | 122 (121 khóa khác nhau) |
| Hàng `bibtex` sau dedup | **117** (gộp 5 hàng) |
| Khóa bị đổi tên | 4 |
| Cảnh báo xung đột trường | 4 (3 `authors`, 1 `journal`) |
| Cảnh báo parse `.bib` | 0 |

Năm nhóm bị gộp đều là cùng một bài viết với hai khóa khác nhau hoặc là một entry lặp: `Caruana:97` (cùng khóa, cùng DOI chỉ khác hoa/thường, cùng tiêu đề) và bốn cặp cùng tiêu đề (`Chithrananda`, `Hu`, `Fabian`, `survey_oversmoothing`/`rusch2023survey`). Không nhóm nào bị gộp sai.

### 8.3. Độ đầy đủ của 117 hàng

| Trường | Số hàng có giá trị | Tỉ lệ |
| --- | ---: | ---: |
| `title` | 117 | 100,0% |
| `authors` | 117 | 100,0% |
| `year` | 117 | 100,0% |
| `journal` | 97 | 82,9% |
| `doi` | 79 | 67,5% |
| `url` | 71 | 60,7% |

Loại ấn phẩm: `article` 80, `misc` 19, `inproceedings` 12, `inbook` 5, `book` 1.

### 8.4. Bốn cảnh báo xung đột
Cả bốn cặp đều nằm trong cùng version v1 (do `.bib` có entry gần như trùng), nên quy tắc "giữ entry sớm nhất" quyết định kết quả:

| Trường | Giá trị được giữ | Giá trị bị bỏ |
| --- | --- | --- |
| `authors` (`Chithrananda`) | `S. Chithrananda, G. Grand, B. Ramsundar` (viết tắt) | tên đầy đủ |
| `authors` (`Hu`) | `W. Hu, B. Liu, …` (viết tắt) | tên đầy đủ |
| `authors` (`Fabian`) | tên đầy đủ | `B. Fabian, T. Edlich, …` (viết tắt) |
| `journal` (`Fabian`) | `CoRR` | `Proc. NeurIPS 2020 Workshop on Machine Learning for Molecules` |

Đây là hệ quả của quy ước nhóm, không phải lỗi gộp: ở hai trong ba xung đột tác giả, hàng cuối cùng giữ bản viết tắt dù có bản đầy đủ hơn. Hành vi này được ghi lại ở mục 10.

### 8.5. Các phần tử toàn văn
Số liệu dedup toàn văn của cùng paper do TV1 báo cáo trong lần chạy toàn pipeline: `elements` 232 → 229, `hierarchy` 231 hàng. Tôi **không tự tái hiện** con số này vì cần đầu ra của Resolver và Normalization trên snapshot MS1 đầy đủ.

### 8.6. Hiệu năng (một paper, một version)

| Bước | Thời gian | Ghi chú |
| --- | ---: | --- |
| `parse_bib_text` (122 entry, 98 KB) | 887 ms | Gồm cả lần import `bibtexparser` đầu tiên |
| `unionize_bibtex` | 5,1 ms | |
| `render_bibtex` | 1,0 ms | |
| Bộ nhớ đỉnh do Python cấp phát | 8,5 MB | Đo bằng `tracemalloc`, chỉ cho ba bước trên |

Kiểm tra độ phức tạp bằng dữ liệu tổng hợp (không phải dữ liệu thật): gộp 1.000 / 5.000 / 20.000 entry mất 9 / 27 / 107 ms, tức gần tuyến tính. Đây không phải benchmark nghiệm thu: chưa đo trên Google Colab CPU-only, chưa đo toàn pipeline, và `tracemalloc` không phải RSS của tiến trình (phần đo RAM chuẩn là việc của công cụ benchmark TV5).

### 8.7. Nhận xét về dữ liệu
- Corpus của paper chỉ có `.bib`, không có `\bibitem` và không có `.bbl`, nên **chưa kiểm chứng được `parse_bibitem` trên dữ liệu thật**; mọi kiểm thử cho nhánh này dùng chuỗi mô phỏng.
- `.bib` có 122 entry nhưng chỉ có 78 khóa được `\cite` trong `main.tex` và `si.tex` (không khóa nào được trích mà thiếu trong `.bib`). Tức **43 entry của tệp thô không được trích dẫn ở đâu**, và vì ta đọc toàn bộ `.bib` được `\bibliography` tham chiếu nên bảng `bibtex` chứa cả các entry này. Số này gần với 81 reference mà Semantic Scholar báo cho paper hơn là 117.

---

## 9. KIỂM THỬ

### 9.1. Các nhóm test

| Nhóm | Nội dung |
| --- | --- |
| `\bibitem` | Kiểu `\newblock`, nhãn tùy chọn, DOI và URL, năm không lẫn số arXiv, tiêu đề trong ngoặc kép, tác giả `Last, First`, item mơ hồ để trống, item không có khóa |
| `.bib` | `@string`, `@comment`, ngoặc lồng, `Last, First`, DOI dạng URL, entry hỏng có cảnh báo |
| Adapter `bibliography` | Gộp `\bibitem` với `.bib` được trích, chỉ đọc `.bib` được tham chiếu, đọc toàn bộ khi không có tham chiếu, version chỉ còn `.bib`, `no_source`, lỗi đầu vào và đường dẫn thoát root |
| Dedup cấp 1 | **Ví dụ của đề** (`vaswani2017` → `vit_transformer` qua 3 version), DOI khác hoa/thường, trùng trong một version, bắc cầu, tiêu đề ngắn không gộp, xung đột giữ entry sớm nhất, thứ tự khóa |
| Rename `\cite` | Mọi lệnh họ cite, `*`, `[…]`, nhiều khóa, hai khóa thành một, khóa lạ có cảnh báo |
| Dedup cấp 2 | **Ví dụ của đề cho đúng 5 hàng `elements` và 4 hàng `hierarchy`**, câu lặp giữ đủ occurrence và cạnh, `kind` là một phần định danh, đổi tên `\cite` trước khi so nội dung, ID cho paper dạng cũ, cây sai bị từ chối |
| Adapter `deduplicate` | Ba bảng + manifest + `references.bib` + occurrences, mọi version rỗng, version chỉ có `.bib`, version chưa sẵn sàng làm cả paper `skipped` và không ghi gì, lỗi dữ liệu, tính tất định khi chạy lại |

Toàn bộ test dùng chuỗi mô phỏng, không cần Internet, hoàn tất dưới 0,2 giây.

### 9.2. Kết quả chạy
Trên `origin/main` ngày 06/11/2026, Python 3.14, cài `".[reporting,dev]"`: **426 test đạt** toàn repo (65 subtest), trong đó 56 test thuộc TV4 (16 `test_bibliography.py`, 40 `test_deduplication.py`).

---

## 10. ĐỐI CHIẾU VỚI ĐỀ BÀI

Nguồn: [đề Milestone 2](https://hcmus-cs-ta.github.io/lab-book/intro-ds/statement/parsing/) (trích qua công cụ đọc web, mỗi câu dưới 125 ký tự).

### 10.1. Những điều đề yêu cầu rõ

| Việc đã làm | Trích từ đề | Mục trong đề |
| --- | --- | --- |
| Chuyển `\bibitem` bằng regex | "students must convert them into standard BibTeX entries using programmatic tools such as regular expressions" | Reference Extraction |
| Gộp tài liệu trùng trong version và xuyên version | "Duplicated reference entries inside each version or across different versions of a single publication" | Deduplication |
| Chọn một khóa | "a single citation key should be chosen" | Deduplication |
| Đổi `\cite` | "the `\cite{}` commands of the remaining entries must be renamed to this chosen key" | Deduplication |
| Hợp nhất trường | "unionize the fields of the duplicate entries rather than selecting one entry" | Deduplication |
| Gộp toàn văn sau cleanup | "full-text matching should be performed after cleanup" | Deduplication |
| `elements`: một hàng cho mỗi phần tử phân biệt | "one row per _distinct_ element across all versions of the publication" | Requirement |
| `hierarchy`: một hàng cho mỗi cạnh mỗi version | "with one row per node-parent edge of each version" | Requirement |
| Phần tử version cũ làm nút ở version sau | "an element contributed by an earlier version may act as a node in a later version's edges" | Requirement |
| Mã phần tử | "Element IDs begin with the publication key followed by a discriminant that is unique inside the publication" | Requirement |
| Cột `bibtex` | `arxiv_id`, `citation_key`, `entry_type`, `title`, `authors`, `year`, `doi`, `journal`, `url`; `year (int, nullable)` | Requirement |
| Version không có TeX | "record the version as empty rather than skipping it" | Requirement |
| Thống kê trước/sau dedup | "the element/entry counts before and after deduplication" | Report Requirements |

### 10.2. Những điều đề không nói (quy ước của nhóm)

| # | Điểm | Đề nói gì | Cách nhóm xử lý |
| --- | --- | --- | --- |
| 1 | Chọn khóa nào | Không nói | Khóa xuất hiện sớm nhất |
| 2 | Giá trị xung đột khi hợp nhất | Không nói | Giữ entry sớm nhất, ghi cảnh báo |
| 3 | Tiêu chí "cùng tài liệu" | Chỉ nói "cùng nội dung" | Cùng khóa, DOI hoặc tiêu đề chuẩn hóa từ 15 ký tự |
| 4 | `\cite` còn trong `content` | Không nói | Giữ lại, đã đổi sang khóa được chọn |
| 5 | Entry không được trích dẫn có vào `bibtex` | Không nói | Có, nếu `.bib` được `\bibliography` tham chiếu |
| 6 | Giá trị `entry_type` | "(string, dictionary)", không liệt kê | `.bib` giữ loại gốc, `\bibitem` luôn `misc` |
| 7 | `doi`, `journal`, `url`, `title` thiếu | Chỉ `year` ghi nullable | Theo hợp đồng TV1: `null` (title `""`, authors `[]`) |
| 8 | Tệp `references.bib` | Không yêu cầu cũng không cấm | Xuất thêm từ bảng đã gộp để có cú pháp BibTeX chuẩn |
| 9 | Đọc `.bib` | Đề MS2 không nhắc `.bib` | Có, vì corpus MS1 giữ `.bib` ("extract only the `.tex` and `.bib` files", đề MS1) |

---

## 11. HẠN CHẾ VÀ HƯỚNG PHÁT TRIỂN

1. **Phạm vi dữ liệu thật rất hẹp.** Chỉ một paper, một version, nhánh `.bib`. Nhánh `\bibitem`, dedup xuyên nhiều version và các trạng thái `no_source` thật chưa được kiểm chứng trên corpus.
2. **Nguồn tham khảo bị thiếu ở MS1.** Đề MS1 chỉ giữ `.tex` và `.bib` nên tệp `.bbl` (chứa `\bibitem` đã biên dịch) bị loại. Paper chỉ nộp `.bbl` sẽ có bảng `bibtex` rỗng (manifest ghi `bib_source_missing_versions` để đo tỉ lệ khi có corpus lớn).
3. **Quy tắc giải quyết xung đột là "giữ entry sớm nhất".** Ở dữ liệu thật điều này giữ bản viết tắt của tên tác giả trong hai trên ba cảnh báo tác giả. Đề chưa quy định, và có thể cải thiện bằng cách giữ bản đầy đủ hơn khi hai tên tương thích.
4. **Entry không được trích dẫn nằm trong `bibtex`** (43 trên 122 ở paper mẫu). Chưa lọc vì đề không quy định và thay đổi này ảnh hưởng hợp đồng của TV1/TV5.
5. **Danh sách tác giả `and others`** trong `.bib` hiện bị coi là một tên (`others`); paper mẫu không có trường hợp này.
6. **Nhận diện trùng bằng tiêu đề** là heuristic (từ 15 ký tự); hai tài liệu khác nhau có tiêu đề rất giống nhau có thể bị gộp.
7. **Chất lượng dedup toàn văn phụ thuộc `cleaned_content` của TV3.** Nếu bước chuẩn hóa còn để lại khác biệt định dạng thì hai phần tử giống nhau không được gộp.
8. **Chưa đo hiệu năng chuẩn.** Cần chạy toàn corpus trên Google Colab CPU-only với công cụ benchmark của TV5.
9. **Thêm phụ thuộc `bibtexparser`** vào `pyproject.toml` (file do TV1 quản lý).

---

## 12. KẾT LUẬN

TV4 đã hoàn thành hai stage `bibliography` và `deduplicate` đúng hợp đồng MS2 và đã tích hợp trên `main`. Các thao tác đề yêu cầu (chuyển `\bibitem`, gộp tài liệu trùng, một khóa duy nhất, đổi `\cite`, hợp nhất trường, dedup toàn văn, ba bảng, mã phần tử, version rỗng, số đếm trước/sau) đều có cài đặt và test, kể cả hai ví dụ nhỏ trong đề (hợp nhất `vaswani2017`, và bảng 5 `elements` / 4 `hierarchy`). Trên dữ liệu thật của một paper, 122 entry được gộp thành 117 hàng với năm nhóm gộp đều đúng; 4 cảnh báo xung đột còn lại phản ánh khoảng trống mà đề chưa quy định, được ghi lại thay vì che giấu. Những việc chưa làm được là đo trên toàn corpus, kiểm chứng nhánh `\bibitem` trên dữ liệu thật và đo hiệu năng chuẩn trên Colab.
