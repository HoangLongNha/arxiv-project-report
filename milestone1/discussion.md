# Phân tích và hạn chế

Bản hiện tại xác nhận code có thể tạo corpus mẫu, kiểm tra chất lượng, thu thập số đo, tổng hợp và sinh bảng/biểu đồ bằng notebook. Lượt smoke cục bộ với `2508.12872` cũng đã hoàn tất: một version, 97 references, validator pass. Nó chưa chứng minh độ bao phủ 25.000 ID hay hiệu năng toàn corpus/Colab.

## Mẫu thực nghiệm Colab CPU-only đã chạy

Đã đo lại một paper `2508.12872` trên runtime Colab CPU, từ commit sạch `0f8d83b`. Wall time 21,511 giây; thời gian paper 21,240 giây; bước references chiếm khoảng 19,312 giây. Tổng RSS cực đại quan sát 41.771.008 bytes, mean theo thời gian khoảng 38.603.952 bytes. Peak disk quan sát 17.676.608 bytes, final 10.907.480 bytes. Đây là một mẫu, không đủ để khái quát hiệu năng toàn assignment hoặc so sánh thuật toán.

Audit đối chiếu đủ 25.000 ID nhưng chỉ tìm được record/data cho một ID; phần còn lại là **chưa được crawl**, không phải kết luận 24.999 paper không tồn tại. Không được dùng tỷ lệ thành công 100% của mẫu một paper làm tỷ lệ thành công toàn nhóm.

Demo có một discovery not_found và một version PDF-only. Vì vậy pipeline exit 1 và source success rate thấp hơn 100% là tình huống có chủ đích. Validator vẫn có thể pass paper PDF-only nếu trạng thái nhất quán. Điều này minh họa vì sao cần xem cả coverage, từng status, nguồn thiếu dữ liệu và validation, thay vì chỉ nhìn exit code.

## Cần hoàn tất khi có dữ liệu thật

1. Mẫu smoke/Colab đã chạy; tiếp tục thu thập assignment, giữ nguyên pacing và lưu checkpoint trên storage phù hợp để resume.
2. Lưu số liệu theo run; tách fresh/resume, xác nhận commit và môi trường.
3. Chạy lại validator trên corpus thật và rà soát lỗi/cảnh báo; không tự coi mọi success stage là corpus tốt.
4. Xuất summary/samples/timings sang repository report, chọn run thật khi build, cập nhật intro và phân tích này theo kết quả đo.
5. Bổ sung ví dụ lỗi thực tế, nguyên nhân, ảnh hưởng tới các milestone sau và hướng cải thiện có số liệu chứng minh.

## Giới hạn phương pháp

RSS theo mẫu có thể bỏ lỡ đỉnh ngắn; tổng RSS không bằng bộ nhớ vật lý duy nhất do shared pages. Quét disk gây overhead và chỉ đo trong output root, không đo hệ điều hành hay cache pip. Không so package nén với corpus giải nén để kết luận tỷ lệ bỏ hình. Reference metadata không đầy đủ và Semantic Scholar có thể chưa index paper. Validator dùng schema/heuristics, không kiểm chứng ngữ nghĩa toàn bộ LaTeX, không biên dịch PDF và không thay kiểm tra thủ công trên mẫu.

Sau khi tiến trình bị ngắt, checkpoint mới có thể chưa xuất hiện trong manifest cuối. Hoàn tất resume để có snapshot nhất quán trước khi thống kê; không cộng các run chồng lặp như các paper mới.
