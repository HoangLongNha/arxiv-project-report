# Checklist Milestone 2 — TV1

Theo cập nhật ngày 31/10/2026 của người dùng, MS1 vẫn đang thu thập/làm sạch dữ liệu; chưa có thời điểm hoàn tất được xác nhận. TV1 có thể triển khai A–D bằng dữ liệu giả lập ngay; kiểm chứng dữ liệu thật và nghiệm thu ở E khi đầu vào đã hoàn tất. Các mục chưa đánh dấu chưa được xác nhận hoàn thành.

## A. Chuẩn bị kiến trúc và hợp đồng dữ liệu

- [x] A1 Kiểm tra đầu ra Milestone 1 — Hiểu cấu trúc `corpus/<paper_key>/vN/`, `DiscoveryRecord`, `VersionRecord` và `StageResult`.
- [x] A2 Xây dựng 3 schema đầu ra — Bổ sung `ElementRow`, `HierarchyRow`, `BibtexRow` vào `common/schemas.py`.
- [x] A3 Chuẩn hóa interface giữa các module — Thống nhất `run(record, output_dir, *, version=None, upstream=None) -> StageResult`.
- [x] A4 Chốt định dạng artifact — Thống nhất trường dữ liệu của `gathered.json`, `raw_tree.json`, `normalized_tree.json`, `raw_bibtex.json` và các bảng đầu ra.
- [ ] A5 Cập nhật hợp đồng dữ liệu — Bổ sung đặc tả Milestone 2 vào `docs/CONTRACTS.md` và gửi TV2–TV5 xác nhận.

- [x] A6 Chốt điều kiện bàn giao MS1 → MS2 — Chỉ parse version khi extract đã thành công và corpus đã ghi xong. `VersionRecord` hiện không có trường status; quy định checkpoint/kết quả download và extract nào cung cấp trạng thái. Phân biệt `no_source` được xác nhận với chưa sẵn sàng, lỗi tải và lỗi giải nén; không kết luận PDF-only từ thư mục thiếu/rỗng.
- [x] A7 Cụ thể hóa hợp đồng A2–A5 — Cung cấp ví dụ JSON đầu vào/đầu ra từng stage, gồm tên stage/artifact, trường bắt buộc, artifact rỗng, trạng thái lỗi và đường dẫn tương đối. Chốt cách biểu diễn root, thứ tự nút/cạnh, phần tử cùng nội dung xuất hiện nhiều lần và đầu vào nhiều version của deduplication. Giữ tương thích MS1; quy định phiên bản schema khi thay đổi hợp đồng.
- [x] A8 Chuẩn bị dữ liệu phát triển — Dùng chuỗi TeX/BibTeX giả lập trong tests và cây file trong thư mục tạm. Khi có mẫu thật, dùng bản sao MS1 đã hoàn tất; tách output MS2 khỏi output MS1 đang chạy, quy định rõ input root/output root và không sửa corpus đầu vào.

### Kết quả phần A — 29/10/2026

- Đã chuẩn bị baseline nội bộ cho A1–A4, A6–A8; dấu hoàn thành ở đây chỉ xác nhận triển khai local, chưa thay cho đồng thuận TV2–TV5 hoặc nghiệm thu corpus thật.
- Schema: `arxiv-data-science/src/arxiv_pipeline/common/schemas.py`; `hierarchy` giữ đúng 4 cột theo đề. MS1 giữ schema mặc định 1.0; artifact/StageResult MS2 dùng phiên bản riêng 2.0.
- Hợp đồng và audit: [MS2_CONTRACTS.md](arxiv-data-science/docs/MS2_CONTRACTS.md). Bản bàn giao: [MS2_HANDOFF.md](arxiv-data-science/docs/MS2_HANDOFF.md).
- Ví dụ và corpus giả lập: `arxiv-data-science/tests/parsing/ms2_contract_examples.py`; có 8 test hợp đồng, cây occurrences giữ thứ tự/lần xuất hiện; fixtures chỉ ghi vào thư mục tạm.
- Kiểm chứng toàn repo: **148 tests và 45 subtests qua**. Lượt đầu vướng quyền thư mục tạm pytest; chạy lại với `--basetemp artifacts/pytest-ms2-<unique-id>` đã qua. `git diff --check` không báo lỗi.
- **A5 còn chờ dữ liệu MS1:** theo người dùng, nhóm vẫn đang lấy dữ liệu. Hợp đồng baseline đã có; chờ corpus hoàn tất để đối chiếu và bàn giao thực tế. Xác nhận kỹ thuật của các thành viên được ghi riêng trong MS2_HANDOFF.md.
- Tiến độ B được cập nhật bên dưới; C chưa triển khai. Theo yêu cầu push tiếp theo, phần A được tách sang nhánh `feature/m2-tv1-contracts` từ `origin/main`, không gộp vào PR MS1.

## B. Xây dựng Resolver — Module chính của TV1

- [x] B1 Xử lý LaTeX comments — Bỏ các lệnh bị comment bởi `%`, nhưng xử lý đúng dấu `\%` đã escape.
- [x] B2 Tìm file TeX chính — Xác định file gốc chứa `\documentclass`, `\begin{document}` và `\end{document}`.
- [x] B3 Ghép file theo đường dẫn biên dịch — Duyệt `\input`, `\include` đệ quy nhiều cấp, bảo toàn thứ tự nội dung.
- [x] B4 Loại bỏ các file TeX không liên quan — Ghi nhận danh sách `ignored_files` và tránh ghép file bản nháp.
- [x] B5 Tách tài liệu tham khảo — Lấy `raw_bibitems`, thu thập file `.bib`, loại khối `thebibliography` khỏi nội dung chính.
- [x] B6 Xử lý phiên bản không có TeX — Trả `no_source` an toàn, không làm dừng toàn bộ pipeline.
- [x] B7 Tạo artifact gathered.json — Ghi đầu ra và trả `StageResult` theo hợp đồng.
- [x] B8 Viết unit tests cho Resolver — Kiểm tra file đơn, đa file, comment, references, vòng lặp include, PDF-only.

- [x] B9 Hoàn thiện quy tắc include — Chốt cách tìm file từ thư mục con, xử lý file đích thiếu và chặn đường dẫn thoát khỏi corpus của version. Dùng stack của nhánh đang duyệt để chặn vòng lặp, vẫn giữ các lần include lặp hợp lệ và thứ tự nội dung.
- [x] B10 Hoàn thiện chọn root và truy vết — Khi có nhiều ứng viên, chọn theo quy tắc ổn định và lưu lý do/cảnh báo; quy định kết quả khi không tìm được root hoặc ranh giới document nằm trong file include. Lưu thông tin file nguồn phục vụ truy vết; `ignored_files` chỉ biểu thị file không được sử dụng, không xóa file đầu vào.
- [x] B11 Giữ ngữ cảnh và tách References đúng phạm vi — Bàn giao ngữ cảnh preamble cần thiết riêng với body; giữ Appendix/Acknowledgements sau References. Nhận diện lệnh khai báo bibliography, phân biệt `.bib` được tham chiếu với `.bib` chỉ có trong thư mục và cảnh báo nguồn references bị thiếu.
- [x] B12 Ghi artifact an toàn — Ghi atomic rồi mới trả `success`; bổ sung thông tin schema, paper/version, provenance và cảnh báo theo hợp đồng. Ghi rõ cú pháp LaTeX được hỗ trợ và cách báo phần chưa hỗ trợ; đầu vào hỏng/chưa hoàn tất không được đổi thành `no_source`.
- [x] B13 Mở rộng tests B8 — Thêm thư mục con, bảo toàn thứ tự, include lặp, file đích thiếu, đường dẫn ngoài corpus, root mơ hồ, escaped percent, Appendix sau References và trạng thái đầu vào lỗi/chưa sẵn sàng. Tests không gọi mạng hoặc phụ thuộc corpus thật.

### Kết quả phần B — 31/10/2026

- Đã triển khai B1–B13 trên nhánh `feature/m2-tv1-resolver` từ main đã merge PR9; dấu hoàn thành xác nhận phạm vi cú pháp tĩnh và kiểm thử local, chưa thay cho nghiệm thu corpus thật.
- Resolver ghi `gathered.json`/StageResult schema 2.0, giữ preamble, source spans và inventory BibTeX. Include lặp giữ nguyên thứ tự, References được tách mà không mất Appendix/Acknowledgements.
- Đầu vào đi qua envelope context/stages của hợp đồng; phân biệt success/no_source/skipped/data_error/error. Checkpoint empty mâu thuẫn với corpus hoặc source thiếu/rỗng không được xem là PDF-only.
- Review độc lập đã tìm và sửa năm ca mất nội dung/trạng thái sai; mỗi ca có regression test. Giới hạn TeX động được ghi rõ trong `docs/MS2_RESOLVER.md` của repo.
- Tests Resolver: **40 passed, 1 skipped, 16 subtests passed** (0,86 giây). Test skip do host Windows không có quyền tạo symlink; kiểm tra traversal bằng path thường vẫn chạy.
- Toàn repo: **191 passed, 1 skipped, 61 subtests passed** (19,29 giây), chạy với thư mục tạm riêng trong artifacts. Không thay đổi module MS1 hoặc Hierarchy PR10.
- Chưa chạy corpus thật, chưa ghép với TV2, chưa triển khai C và chưa commit/push phần B.

## C. Framework và Pipeline Orchestrator

- [x] C1 Thiết kế luồng điều phối — Theo version: `Resolver → Hierarchy → Normalization` và `Resolver → Bibliography`. Theo paper: gom Normalization/Bibliography của các version rồi `Deduplication → Validation MS2`; xử lý riêng version `no_source` theo hợp đồng.
- [x] C2 Triển khai pipeline/parse.py — Kết nối Resolver, Hierarchy, Normalization, Bibliography, Deduplication và Validation.
- [x] C3 Mở rộng CLI — Cho phép chạy parsing bằng tham số CLI, đồng thời giữ nguyên chức năng Milestone 1.
- [x] C4 Hỗ trợ trạng thái và checkpoint — Xử lý `success`, `no_source`, `data_error`, `error`, cùng cơ chế `--resume` và `--force` phù hợp.
- [x] C5 Kiểm thử tích hợp bằng mock adapters — Mô phỏng TV2–TV5 và xác minh thứ tự gọi, truyền artifact, xử lý lỗi.

- [x] C6 Chốt tính đầy đủ cấp paper — Đối chiếu danh sách version kỳ vọng với các version đã xử lý và outcome `no_source`. Nếu còn version thiếu/lỗi/chưa sẵn sàng, ghi rõ kết quả chưa đầy đủ; không công bố bảng deduplication hoặc validation một phần như kết quả cuối cùng.
- [x] C7 Bổ sung quy tắc resume/force — Kiểm tra artifact và dấu nhận diện đầu vào/phụ thuộc phù hợp. Khi version mới xuất hiện hoặc đầu vào thay đổi, chạy lại các stage bị ảnh hưởng, gồm deduplication/validation cấp paper. `--force` chỉ làm mới kết quả MS2 trong phạm vi được chọn; không ghi đè dữ liệu MS1.
- [x] C8 Tích hợp validation với TV5 — Validator MS2 thật đã merge qua PR18/PR19; đã chạy cùng module TV1–TV4 trên bốn bài thật/sáu version ngày 10/11/2026. Validator MS1 giữ riêng tại `export/validation.py`; artifact MS2 ở `validation/parsing/`.
- [x] C9 Mở rộng tests C5 — Kiểm tra nhánh Bibliography, gom nhiều version, downstream bị chặn, `no_source`, artifact thiếu, resume/force và chạy lại kết quả cấp paper khi có version mới. Xác minh CLI MS1 vẫn hoạt động.

### Kết quả phần C — 02/11/2026

- Đã triển khai C1–C7 và C9 trên `feature/m2-tv1-orchestrator`, tích hợp Resolver phần B và Hierarchy đã sửa ở PR10. Dấu hoàn thành xác nhận framework và tests, chưa phải nghiệm thu mọi module thật.
- CLI có `--stage parse --ms1-input <snapshot> --output <ms2-output>`, lọc paper/version, resume/force và mã thoát phản ánh incomplete. Không khởi tạo client gọi API trong chế độ parse; MS1 giữ nguyên hành vi thành công đã kiểm thử.
- Pipeline có checkpoint/dependency fingerprints và SHA-256 artifact, phát hiện version mới, source/adapter thay đổi, artifact thiếu hoặc bị sửa; không tái sử dụng bảng paper lỗi thời. Snapshot đổi trong khi export/validation làm kết quả incomplete.
- Trạng thái `no_source` được giữ theo version; Bibliography đọc trực tiếp nhánh Resolver. Downstream chưa bàn giao là `not_implemented`, không được biến thành success giả.
- **C8 còn chờ validator TV5 thật:** đã nối stage `validate_parse` tại `reporting/milestone2/validation.py`, kiểm chứng giao tiếp bằng mock; chưa có module để nghiệm thu tích hợp.
- Có 29 tests Orchestrator mới; review độc lập đã tìm và sửa các lỗi junction log ghi vào MS1, discovery ID sai kiểu và manifest complete cũ khi Discovery hỏng.
- Toàn repo: **260 passed, 1 skipped, 61 subtests passed** (35,08 giây). Test skip thuộc trường hợp symlink của Resolver; test junction của phần C đã chạy qua.
- Chưa nghiệm thu corpus thật. Không tạo file kế hoạch cá nhân mới trong repo; tài liệu dùng chung được cập nhật tại README, MS2_CONTRACTS và MS2_HANDOFF.

## D. Báo cáo Milestone 2

**Cập nhật phân công 04/11/2026:** TV5 phụ trách phần báo cáo MS2. D1–D5 dưới đây
không còn là đầu việc triển khai của TV1; giữ danh sách để đối chiếu lịch sử.
TV1 chỉ cung cấp artifact, mô tả giao tiếp và kết quả chạy có nguồn khi TV5 cần.

- [ ] D1 Tạo milestone2/index.md — Khởi tạo chương Milestone 2 trong Jupyter Book.
- [ ] D2 Tạo milestone2/introduction.md — Giới thiệu mục tiêu, dữ liệu đầu vào, đầu ra và tổng quan pipeline.
- [ ] D3 Cập nhật _toc.yml — Đưa chương mới vào mục lục của Jupyter Book đang sử dụng.
- [ ] D4 Viết nội dung phương pháp của TV1 — Bàn giao thuyết minh Resolver và Orchestrator cho `milestone2/methodology.md`.

- [ ] D5 Hoàn thiện nội dung và phối hợp báo cáo — Ghi điều kiện bàn giao MS1, trạng thái dữ liệu, giới hạn cú pháp, xử lý lỗi và resume xuyên version. Phối hợp TV5 khi sửa `_toc.yml`/tích hợp `methodology.md` dùng chung và kiểm tra Jupyter Book build.

## E. Tích hợp và nghiệm thu

Cập nhật 10/11/2026: PR19 đã merge; đã chạy đủ sáu module thật trên bốn bài,
sáu version từ snapshot Drive TV1/TV5, gồm một file TeX, đa file, nhiều version
và PDF-only. Cả bốn validator valid=true, không có error; 26 stage success và
sáu stage no_source. Đầu ra có 1.176 elements, 1.738 hierarchy đúng bốn cột,
371 bibtex; còn 218 cảnh báo bib_field_conflict cần TV4/TV5 đối chiếu nội dung.

Đã sửa exporter TV4 giữ entry không có field bằng `title = {}`; không bỏ citation
key hoặc bịa dữ liệu. Resume tái sử dụng đủ 32 checkpoint, 58 hash file MS1 không
đổi. Kiểm tra riêng chọn thiếu version và bảng bị sửa đều chặn/phục hồi đúng.
Tests: 432 passed, 1 skipped, 65 subtests passed. Đây là nghiệm thu mẫu local,
chưa thay cho toàn corpus hoặc Colab CPU-only. Không viết báo cáo MS2 thay TV5.

Bằng chứng: `arxiv-data-science/artifacts/ms2-e-acceptance-20261110/`, gồm
`local-receipt.json`, `recovery-receipt.json` và output tv1/tv5. Mã tích hợp trên
nhánh `feat/m2-tv1-integration`; mã đã chạy tại commit `ef2845c`. Hướng dẫn dùng
chung cập nhật trong `docs/MS2_HANDOFF.md`; notebook thực thi toàn corpus là
`colab/MS2_Integration_CPU.ipynb`, chưa chạy trên Colab trong đợt này.

- [x] E1 Tích hợp module thật của TV2–TV5 — Đã chạy production adapters, sửa lỗi xuất entry BibTeX rỗng phát hiện khi tích hợp; không dùng mock để nghiệm thu.
- [x] E2 Chạy thử trên corpus mẫu thực tế — TV1: 2508.17481 v1/v2, 2508.17871 v1/v2, 2508.17740 v1; TV5: 2410.08024 v1. Snapshot/provenance và giới hạn được ghi trong bàn giao.
- [x] E3 Chạy kiểm thử toàn bộ pipeline — Đã xuất đủ elements/hierarchy/bibtex, references.bib, occurrences, manifest và validation; cả bốn mẫu qua QA cấu trúc. Không đồng nghĩa nghiệm thu nội dung toàn corpus.
- [ ] E4 Hỗ trợ nghiệm thu toàn corpus — Phối hợp TV5 xử lý lỗi tích hợp khi chạy Colab CPU-only và tổng hợp báo cáo.

  Đã chuẩn bị notebook chạy theo từng thành viên, số đo thật, danh sách lỗi và
  receipt; chưa có lượt Colab/toàn corpus đủ năm thành viên nên giữ chưa hoàn tất.

  Theo lựa chọn của người dùng, mỗi TV chạy đúng dải ID MS1 đã được giao.
  Notebook chọn MEMBER tự động ánh xạ range; SMOKE/FULL và ZIP tách riêng từng
  người, cùng production commit b932d98. Đã kiểm tra 23 ca liên quan và SMOKE
  mới trên bốn bài thật/sáu version; chưa chạy FULL trên Colab.

- [ ] E5 Kiểm tra nghiệm thu mở rộng — Kiểm tra khóa/quan hệ và thứ tự cấu trúc, đồng bộ citation, deduplication xuyên version và resume không giữ kết quả cấp paper lỗi thời. Sau bàn giao MS1, thống kê riêng thành công, `no_source`, lỗi, chưa xử lý và paper chưa đủ version; không dùng chạy mẫu thay nghiệm thu toàn corpus.

  Phần kiểm tra mở rộng trên mẫu thật đã qua: đa version, occurrence, citation,
  no_source, resume, chọn thiếu version và bảng bị sửa. Phần thống kê/nghiệm thu
  toàn corpus còn chờ thực thi notebook trên snapshot đầy đủ. Audit MS1 TV1 bàn
  giao có 685/5.000 bài chưa qua validation MS1; phải phân loại download/extract
  trước khi kết luận bài nào bị chặn parsing, không dùng tổng lỗi MS1 làm số lỗi MS2.

## Thứ tự triển khai trong lúc chờ MS1

1. **Làm ngay:** A1–A8; ưu tiên bàn giao schema, ví dụ artifact và hợp đồng cho TV2–TV5.
2. **Khi MS1 vẫn chạy:** B1–B13, C1–C9 bằng dữ liệu giả lập/mock adapters; chuẩn bị D1–D5.
3. **Khi có mẫu MS1 hoàn tất:** Chạy E2 trên bản sao mẫu, sửa lỗi; thực hiện E1 khi module thật sẵn sàng.
4. **Khi đủ đầu vào và module:** Hoàn tất E1–E5, kiểm tra tính đầy đủ theo paper/version và nghiệm thu toàn corpus.
