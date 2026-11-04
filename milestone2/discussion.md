# Thảo luận, Phân tích Trường hợp Biên & Sẵn sàng cho Milestone 3

## 1. Phân tích các Trường hợp Biên (Edge Cases)

Trong quá trình phân tích cú pháp phân cấp và khử trùng lặp dữ liệu trên toàn bộ tập dữ liệu mẫu và corpus thật, nhóm đã phát hiện và xử lý thành công các trường hợp biên đặc thù:

### 1.1. Ấn phẩm chỉ có tệp PDF (PDF-only Publications)
- **Thực tế:** Một tỷ lệ nhỏ bài báo trên arXiv (khoảng $2.8\%$) không cung cấp mã nguồn LaTeX gốc mà chỉ có tệp PDF đã biên dịch hoàn chỉnh.
- **Giải pháp của nhóm:** Hệ thống ghi nhận trạng thái `no_source` với bản ghi rỗng hợp lệ trong `occurrences` và cây phân cấp. Điều này bảo đảm **tính toàn vẹn về mặt số liệu (statistical completeness)**: không bỏ sót bài báo nào khỏi mẫu số và không nhầm lẫn giữa lỗi đường truyền tải với ấn phẩm PDF-only.

### 1.2. Ấn phẩm chỉ có tệp BibTeX (Bib-only Publications)
- **Thực tế:** Một số phiên bản không có thân bài báo `.tex` nhưng tác giả vẫn đính kèm tệp `.bib`.
- **Giải pháp của nhóm:** Hợp đồng dữ liệu quy định rõ: *Không ép bảng `bibtex` phải rỗng chỉ vì bài báo không có mã nguồn TeX*. Module trích xuất vẫn lưu trữ đầy đủ danh mục trích dẫn để phục vụ bài toán tra cứu ở Milestone 3.

### 1.3. Bảo vệ Công thức Toán và Từ viết tắt khi Tách Câu (Sentence Splitting)
- **Thực tế:** Nhiều thuật toán tách câu thông thường sử dụng regex dấu chấm câu (`.`) sẽ vô tình cắt rời công thức toán (ví dụ: `$... v_1. v_2 ...$`), từ viết tắt tiếng Anh (`e.g.`, `i.e.`, `et al.`, `Fig. 1`, `Eq. 2`), số thập phân (`3.14159`) hoặc liên kết URL.
- **Giải pháp của nhóm:** Trạm 3 (`normalization.py`) thay thế tạm thời các khối toán nội dòng và từ viết tắt bằng placeholder an toàn trước khi thực hiện phân tách câu, sau đó khôi phục lại nguyên vẹn nội dung.

### 1.4. Xung đột trường dữ liệu BibTeX giữa các Phiên bản (`bib_field_conflict`)
- **Thực tế:** Khi tác giả cập nhật bài báo từ `v1` sang `v2`, thông tin về năm xuất bản, tên tác giả hoặc tên hội nghị/tạp chí có thể bị thay đổi cách viết (ví dụ: `year=2017` ở v1 nhưng sang v2 tác giả sửa thành `year=2018`).
- **Giải pháp của nhóm:** Thuật toán hợp nhất (`unionize_bibtex`) ưu tiên giữ lại giá trị xuất hiện sớm nhất ở phiên bản đầu tiên, đồng thời phát sinh cảnh báo có cấu trúc `bib_field_conflict` lưu vào `parsing_manifest.json` và báo cáo kiểm định để tiện đối soát thủ công.

---

## 2. Kiểm soát Chất lượng & Tính Toàn vẹn Dữ liệu (QA Validation)

Module thẩm định `validation.py` của TV5 đóng vai trò là "chốt chặn chất lượng" độc lập:
1. **Ràng buộc Non-null & Schema:** 100% dòng trong 3 bảng đầu ra có đầy đủ các khóa bắt buộc, đúng kiểu dữ liệu quy định. Bảng `hierarchy` tuân thủ nghiêm ngặt chuẩn 4 cột (`arxiv_id`, `version`, `element_id`, `parent_id`).
2. **Cấu trúc Cây Phân cấp (Tree Integrity):**
   - Không có cạnh tự trỏ (`element_id != parent_id`).
   - Đồ thị quan hệ cha-con của từng version hoàn toàn không chứa chu trình (Directed Acyclic Tree).
   - Mỗi phiên bản có TeX source đều có đúng duy nhất 1 nút gốc `#root{version}` làm tổ tiên cao nhất.
3. **Quy tắc Nghiệp vụ:**
   - Không còn bất kỳ nút `heading` nào mang tiêu đề `"References"` hay `"Bibliography"`.
   - Không có hai phần tử nào (ngoại trừ nút gốc tài liệu) có cùng cặp `(kind, content)`.

---

## 3. Tính Sẵn sàng Chuyển tiếp sang Milestone 3 (Citation Matching)

Kết quả đầu ra của Milestone 2 đáp ứng đầy đủ điều kiện tiên quyết cho Milestone 3:
- **Ngữ cảnh trích dẫn sạch (Clean Citation Context):** Mọi câu văn (`Sentence`) chứa thẻ `\cite{}` đều đã được làm sạch định dạng thừa, chuẩn hóa công thức toán, và đồng bộ mã trích dẫn (`citation_key`) xuyên suốt tất cả các phiên bản.
- **Danh mục BibTeX hợp nhất:** Bảng `bibtex` đã được chuẩn hóa về một khóa duy nhất cho mỗi công trình nghiên cứu, loại bỏ trùng lặp hoàn toàn, sẵn sàng làm kho dữ liệu đối sánh (Target Catalog) cho các mô hình học máy (Machine Learning) và đối sánh thực thể (Entity Matching).
- **Cấu trúc phân cấp giàu ngữ nghĩa:** Bảng `hierarchy` cho phép mở rộng ngữ cảnh trích dẫn không chỉ ở cấp câu văn mà còn ở cấp đoạn văn (`paragraph`) và đề mục (`heading/section`), giúp tăng cường độ chính xác cho mô hình phân loại trích dẫn.

