# Phân tích và hạn chế

Kết quả sơ bộ ngày 04/11/2026 dựa trên artifacts của TV2–TV5, được trình bày trong [Preliminary Results & Data Collection Progress](preliminary-results.ipynb). Chưa có đủ bằng chứng để kết luận toàn bộ nhóm hoàn thành MS1. Việc tải ZIP, có record cho mọi ID, tải source thành công và validation pass là những điều kiện khác nhau.

## Độ bao phủ và chất lượng

TV2 có record cho 5.000 ID, không có unseen/unresolved nhưng báo cáo 2.579 validation fail trong khi cờ `audit_complete=true`. Cờ này không phù hợp công thức tại commit source do benchmark khai báo. Cần xác minh code audit thực dùng, độ mới của validation và chạy lại audit; chưa công nhận hoàn tất. TV5 có record cho 5.000 ID nhưng còn bốn Discovery chưa giải quyết và 379 validation fail. TV3/TV4 chưa cung cấp kết quả audit trong các ZIP đã kiểm tra; khai báo dải trong `inputs.json` không thay thế kết quả thực thi.

Các thống kê TV3/TV4/TV5 tương ứng các run resume 828/6/6 ID. Không dùng chúng để kết luận về toàn dải 5.000 ID, không cộng với dòng audit toàn dải và không cộng các phiên chồng lặp. Cần nhận kết quả audit còn thiếu, giải quyết các lỗi đang mở, rồi tạo thống kê toàn corpus trên snapshot được xác định rõ.

## Hiệu năng và tính tái lập

Bốn benchmark được nộp đều là resume; TV2 bị ngắt và không có snapshot thống kê hợp lệ cho run hiện tại. TV2 không có RAM sample, TV4/TV5 chỉ có một sample nên không đủ bằng chứng diễn giải peak/mean RAM. TV3 có nhiều mẫu hơn nhưng phạm vi và điều kiện cache khác, chưa phù hợp xếp hạng tốc độ giữa thành viên. `wall_seconds` không bao gồm tổng thời gian các phiên trước và chưa khớp hoàn toàn khoảng cách giữa hai timestamp của artifact; cần làm rõ biên đo trước benchmark chính thức.

## Phần cần hoàn thiện

1. Nhận dữ liệu TV1 và kết quả audit đúng dải của TV3/TV4; kiểm tra lại audit TV2 có mâu thuẫn.
2. Rà soát nguyên nhân các Discovery/validation fail, phân biệt lỗi upstream, checkpoint/đường dẫn và quy tắc validator; sửa và tái kiểm trên dữ liệu thật.
3. Chốt snapshot corpus từng thành viên, kiểm tra định danh/range, nguồn code và tính nhất quán trước khi tổng hợp toàn nhóm.
4. Bổ sung thống kê toàn dải và benchmark có cấu hình, phạm vi, chế độ fresh/resume/cache, thời gian đo và số mẫu tài nguyên được mô tả rõ.

## Giới hạn phương pháp

RSS theo mẫu có thể bỏ lỡ đỉnh ngắn; tổng RSS không bằng bộ nhớ vật lý duy nhất do shared pages. Quét disk gây overhead và chỉ đo trong output root, không đo hệ điều hành hay cache pip. Không so package nén với corpus giải nén để kết luận tỷ lệ bỏ hình. Reference metadata không đầy đủ và Semantic Scholar có thể chưa index paper. Validator dùng schema/heuristics, không kiểm chứng ngữ nghĩa toàn bộ LaTeX, không biên dịch PDF và không thay kiểm tra thủ công trên mẫu.

Sau khi tiến trình bị ngắt, checkpoint mới có thể chưa xuất hiện trong manifest cuối. Hoàn tất resume để có snapshot nhất quán trước khi thống kê; không cộng các run chồng lặp như các paper mới.

Các mẫu demo/smoke ngày 28/10 được giữ để tái lập quy trình, không phải số liệu nghiệm thu hiện tại. Kiểm tra hash artifact khi build không thay cho tái kiểm manifest/checkpoint và corpus sống trên Drive.
