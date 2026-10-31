# TÀI LIỆU NGỮ CẢNH KỸ THUẬT BIÊN TẬP JUPYTER BOOK — MILESTONE 1
## PHẦN: CƠ CHẾ TẢI NGUỒN VÀ LƯU TRỮ DỮ LIỆU THÔ (SOURCE DOWNLOADING & RAW STORAGE)

> **Lưu ý nguồn tư liệu:** Tư liệu kỹ thuật do TV2 cung cấp để TV5 biên tập, **không phải bản benchmark đã kiểm chứng**. Những mức tiết kiệm I/O, dung lượng, tỉ lệ PDF-only, bảo đảm tránh HTTP 429 và giới hạn RAM nêu trong tài liệu là ước tính/nhận định của tác giả, không được đưa vào phần kết quả đo cuối nếu chưa có dữ liệu.

> **Mục đích tài liệu:** Cung cấp đầy đủ cơ sở lý thuyết, kiến trúc kỹ thuật, giải thuật chi tiết và các điểm đo lường thống kê (metrics) cho **Thành viên 5 (TV5)** để biên tập trực tiếp vào chương trình Báo cáo **Jupyter Book** (Milestone 1 section) theo đúng yêu cầu tại đề mục *Report Requirements (Jupyter Book)* trong `Docs/miles1_crawling.md`.

---

### 1. NGUYÊN LÝ HOẠT ĐỘNG VÀ CƠ CHẾ CRAWLING CỦA BỘ TẢI (SCRAPING METHODOLOGY)

#### 1.1. Công cụ, Thư viện và API Endpoints
* **Thư viện mạng:** Sử dụng `requests.Session()` nhằm duy trì một kết nối HTTP Keep-Alive tuần tự, giảm thiểu chi phí bắt tay TCP (TCP handshake) và TLS renegotiation khi truy vấn hàng loạt phiên bản bài báo.
* **Endpoints bắt buộc (Dedicated Endpoint):**
  $$\text{URL} = \text{https://export.arxiv.org/src/}\{\text{arxiv\_id}\}\text{v}\{\text{version}\}$$
  * *Lý do kỹ thuật:* Không sử dụng web UI thông thường (`arxiv.org/src/` hay `arxiv.org/e-print/`) vì các endpoint này áp dụng Cloudflare WAF và cơ chế chống bot nghiêm ngặt. arXiv cung cấp cụm máy chủ `export.arxiv.org` riêng biệt phục vụ mục đích nghiên cứu học thuật.
* **Định danh học thuật (arXiv Etiquette):** Khởi tạo header `User-Agent` tùy biến chứa tên dự án, thông tin nhóm sinh viên và email liên hệ (`User-Agent: ArxivDataPipeline/1.0 (mailto:CONTACT_EMAIL)`), tuân thủ đúng khuyến nghị công khai của arXiv API Terms of Use.

#### 1.2. Điều tiết Tần suất truy vấn (Rate Limiting Strategy)
* **Giới hạn thời gian:** Giãn cách tối thiểu cố định $\Delta t \ge 3.0$ giây giữa hai yêu cầu mạng liên tiếp.
* **Cơ chế cài đặt (`RateLimiter`):** 
  * Lưu vết nhãn thời gian của lần hoàn tất request gần nhất (`last_request_time`).
  * Trước khi gửi request tiếp theo, tính toán độ trễ trôi qua: $\text{elapsed} = t_{\text{current}} - t_{\text{last}}$.
  * Nếu $\text{elapsed} < 3.0$s, luồng chủ động gọi `time.sleep(3.0 - elapsed)`. Cơ chế này giảm việc gửi request dồn dập; vẫn có thể gặp `HTTP 429 Too Many Requests`, nên cần xử lý throttle và retry thay vì bảo đảm không bị giới hạn.

#### 1.3. Cơ chế Ngắt sớm phát hiện bài báo PDF-Only (Early Abort)
* **Bối cảnh do TV2 nêu:** Tỉ lệ 1–2% PDF-only là ước lượng trong tư liệu thành viên, chưa có dữ liệu kiểm chứng đi kèm; không dùng làm tỉ lệ của corpus nhóm hoặc toàn bộ arXiv. Pipeline cần ghi nhận riêng các version không có source TeX.
* **Cơ chế hoạt động:**
  * Kích hoạt chế độ tải luồng nhị phân: `requests.get(..., stream=True)`.
  * Thay vì tải toàn bộ nội dung tệp, bộ tải đọc ngay khối phản hồi HTTP Headers đầu tiên:
    $$\text{Kiểm tra: } \text{Content-Type} \stackrel{?}{=} \text{"application/pdf"}$$
  * **Hành động ngắt:** Nếu phát hiện `application/pdf`, phương thức lập tức gọi `response.close()`, hủy luồng kết nối TCP ngay tại chỗ, ghi nhận trạng thái `"no_source"` và thoát.
  * *Ước lượng của TV2:* Mức tiết kiệm $5\text{ MB} \sim 50\text{ MB}$ mỗi bài PDF-only chưa có log đo kèm theo. Lợi ích thực tế phụ thuộc kích thước response và số bytes đã đọc trước khi ngắt; cần đo riêng, không coi khoảng này là kết quả Colab đã xác minh.

#### 1.4. Đảm bảo toàn vẹn dữ liệu: Ghi nguyên tử (Atomic Write) và Băm SHA-256 On-the-fly
* **Nguy cơ lỗi tệp (Corrupted Files):** Khi thực thi trên Google Colab CPU-only, phiên làm việc có thể bị ngắt đột ngột (Kernel crash, timeout, rớt mạng). Nếu ghi trực tiếp vào tệp đích `source`, tệp sẽ bị dở dang (partial file), làm sập các trạm giải nén sau.
* **Quy trình ghi nguyên tử (Atomic Write Pipeline):**
  ```text
  [HTTP Stream Chunk 64KB] 
            │
            ├──> Cập nhật hashlib.sha256() & đếm tổng size_bytes (trong RAM)
            │
            └──> Ghi tuần tự vào tệp tạm "source.part" trên đĩa
                      │
            [Stream hoàn tất không lỗi?]
                 ├── YES ──> os.replace("source.part", "source")  (Atomic Rename)
                 └── NO  ──> os.remove("source.part")             (Clean Rollback)
  ```
* **Băm SHA-256 Trên luồng (On-the-fly Computation):**
  * Tích lũy băm SHA-256 đồng thời khi duyệt qua từng khối `chunk_size = 65,536` bytes (64 KB).
  * *Lợi ích thiết kế:* Không cần đọc lại toàn bộ tệp chỉ để tính checksum. Mức giảm 50% Disk I/O là ước lượng trong tư liệu TV2, không phải phép đo trên workload thực tế của nhóm.

#### 1.5. Khả năng khôi phục (Resume/Idempotency) và Xử lý Lỗi Tự động
* **Bộ nhớ đệm idempotent:** Trước khi gọi mạng, kiểm tra sự tồn tại của `source` và `download_metadata.json`. Nếu tệp đã tải thành công, bỏ qua (skip) và trả về đường dẫn hiện có, cho phép pipeline tiếp tục chạy lại từ điểm dừng (resume) mà không tốn chi phí tải lại.
* **Cơ chế Thử lại (Exponential Backoff):** Với các lỗi mạng tạm thời hoặc mã lỗi `HTTP 429`, `500`, `502`, `503`, `504`, thực hiện tối đa 3 lần thử lại với thời gian chờ tăng lũy thừa cơ số 2: $t_{\text{wait}} = 2^{\text{attempt}} + \text{jitter}$.

---

### 2. CẤU TRÚC DỮ LIỆU ĐẦU RA PHỤC VỤ TRÍCH XUẤT THỐNG KÊ (DATA ARTIFACTS)

Để TV5 viết code Python sinh bảng biểu và biểu đồ tự động trong Jupyter Book, dữ liệu của mỗi phiên bản bài báo được chuẩn hóa tại:
`raw/{sanitized_arxiv_id}/v{version}/download_metadata.json`

#### Lược đồ JSON (Schema Definition):
```json
{
  "arxiv_id": "2301.00001",
  "version": 1,
  "status": "success",
  "content_type": "application/x-eprint-tar",
  "size_bytes": 1048576,
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "downloaded_at": "2026-10-25T14:30:00.123456Z"
}
```

---

### 3. CÁC ĐIỂM DỮ LIỆU VÀ GỢI Ý MÃ NGUỒN CHO TV5 VIẾT BÁO CÁO (CODE SNIPPETS CHO JUPYTER BOOK)

Đoạn mã dưới đây là gợi ý trong tài liệu bàn giao của TV2, không được thực thi khi build trang này. Tên trường và dependency phải được đối chiếu với `download_metadata.json` của commit dùng để chạy trước khi sử dụng. Các notebook thống kê/hiệu năng đang xuất bản đọc summary đã được TV5 kiểm tra, không dùng trực tiếp đoạn minh họa này.

TV5 có thể dùng trực tiếp đoạn mã Python sau trong notebook để tổng hợp các thống kê bắt buộc:

```python
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Đọc toàn bộ download_metadata.json sinh ra bởi TV2
records = []
for meta_path in Path("raw").glob("*/v*/download_metadata.json"):
    with open(meta_path, "r", encoding="utf-8") as f:
        records.append(json.load(f))

df_dl = pd.DataFrame(records)

# 2. Thống kê tỷ lệ thành công (Success Rate & Content-Type Breakdown)
total_attempts = len(df_dl)
success_count = (df_dl["status"] == "success").sum()
pdf_only_count = (df_dl["status"] == "no_source").sum()
error_count = (df_dl["status"] == "api_error").sum()

print(f"Tổng số lượt tải: {total_attempts}")
print(f"Thành công (có mã nguồn LaTeX): {success_count} ({success_count/total_attempts*100:.2f}%)")
print(f"Bài báo PDF-only (Ngắt sớm): {pdf_only_count} ({pdf_only_count/total_attempts*100:.2f}%)")
print(f"Lỗi API/Mạng: {error_count} ({error_count/total_attempts*100:.2f}%)")

# 3. Phân phối kích thước tệp tải về (File Size Distribution trước khi giải nén)
df_success = df_dl[df_dl["status"] == "success"]
size_kb = df_success["size_bytes"] / 1024

print(f"Dung lượng trung bình: {size_kb.mean():.2f} KB")
print(f"Dung lượng trung vị: {size_kb.median():.2f} KB")
print(f"Dung lượng nhỏ nhất: {size_kb.min():.2f} KB, Lớn nhất: {size_kb.max():.2f} KB")

# 4. Đoạn mã vẽ biểu đồ kích thước gói nén (sinh động trong lúc compile Jupyter Book)
plt.figure(figsize=(8, 4))
sns.histplot(size_kb, bins=30, kde=True, color="royalblue")
plt.title("Distribution of Raw Download Package Sizes (KB)")
plt.xlabel("Package Size (KB)")
plt.ylabel("Number of Papers")
plt.grid(True, linestyle="--", alpha=0.5)
plt.show()
```

---

### 4. ĐÁNH GIÁ HIỆU NĂNG TRÊN GOOGLE COLAB CPU-ONLY (BENCHMARKING CONTEXT)

Theo yêu cầu mục *Scraper's Performance* (`running time` và `memory footprint`):

1. **Thời gian chạy (Running Time / Latency):**
   - **Độ trễ có kiểm soát (Intentional Delay):** Do áp dụng Rate Limit $\ge 3.0$s giữa mỗi yêu cầu, tổng thời gian tải tỷ lệ thuận tuyến tính với số lượng phiên bản:
     $$T_{\text{total}} \approx N_{\text{versions}} \times (3.0\text{s} + t_{\text{network\_transfer}})$$
   - *Điểm nhấn cho TV5:* Cần phân tích rõ trong báo cáo rằng độ trễ này là **quy định đạo đức học thuật bắt buộc (Etiquette Policy)** để bảo vệ hệ thống khỏi bị ban IP, chứ không phải do nghẽn hiệu năng thuật toán.
2. **Dấu chân Bộ nhớ RAM (Memory Footprint):**
   - **Cơ chế Chunk Streaming:** Dữ liệu tải về không bao giờ được nạp nguyên khối vào RAM. Thay vào đó, tệp nhị phân được đọc từng khối `64 KB` và ghi ngay xuống đĩa.
   - **Mức tiêu thụ RAM đỉnh (Peak RAM):** Ngưỡng $\le 25\text{ MB}$ do TV2 ước lượng, chưa phải số đo Colab đã xác minh. Streaming giới hạn bộ đệm tải nhưng không bảo đảm giới hạn RSS toàn tiến trình hoặc loại bỏ mọi nguy cơ OOM; báo cáo cuối dùng số đo sampler của đúng run.
3. **Dung lượng Đĩa (Disk Storage Footprint):**
   - Tệp tạm `.part` được tự động thu hồi ngay nếu luồng truyền tải bị lỗi.
   - Tổng bytes các tệp `source` là kích thước dữ liệu tải, khác dung lượng output đầy đủ còn có sidecar, checkpoint, logs và file tạm trong lúc chạy. Benchmark đĩa cần ghi rõ phạm vi đo.
