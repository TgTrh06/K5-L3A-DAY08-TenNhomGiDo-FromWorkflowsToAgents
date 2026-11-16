# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: TenNhomGiDo
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): e5e82e7

## 2. Mục tiêu và cách tiếp cận

Bài toán yêu cầu xử lý quy trình bồi thường cước vận chuyển của LogiX-VN qua 4 kiến trúc: **Workflow (A)**, **Single Agent (B)**, **Orchestrator (C)**, và **Swarm (D)** nhằm tìm ra kiến trúc **ít tự chủ nhất nhưng vẫn đạt hiệu quả tối ưu**.
Nhóm tiếp cận có hệ thống:
1. **Phân ranh giới rạch ròi giữa Code và Model**: Tiền bồi thường, duyệt chính sách (policy/approval), trần hạn mức đơn hàng (order cap) và chống ghi trùng lặp (idempotency) hoàn toàn do **code/host** kiểm soát. Model chỉ được dùng để soạn thảo phản hồi hoặc hỗ trợ trích xuất văn bản khi cần.
2. **Tuân thủ quy trình kiểm thử và an toàn**: Đảm bảo toàn vẹn giao dịch trước sự cố (Crash safety 20/20), không rò rỉ secret (`CANARY_SECRET_*`, PII) qua ranh giới agent và trace.
3. **Thứ tự thực hiện**: Cài đặt CP1 (Host gate, smoke) $\rightarrow$ Hoàn thiện CP2 (Workflow, Single, Orchestrator) $\rightarrow$ Kiểm thử CP3 & CP4 (Handoff, Crash suite) $\rightarrow$ Benchmark CP5 & Ra quyết định kiến trúc (ADR, Research card).

## 3. Giải pháp

### 3.1. Shape A — Workflow (`src/lab8/shapes/workflow.py`)
- **Nguyên lý hoạt động**: Quy trình tất định (deterministic pipeline) thuần code Python.
- **Ranh giới Code/Model**: Không gọi model để quyết định nghiệp vụ. Đọc claim $\rightarrow$ tra cứu order và policy qua hàm truy vấn an toàn $\rightarrow$ tính bồi hoàn bằng `compute_compensation` $\rightarrow$ chuyển quote đầy đủ cho `durability.issue_refund`.
- **An toàn & Idempotency**: Đảm bảo chuyển tiếp `crash_at` không bắt `InjectedCrash`. Trace chỉ ghi các sự kiện nghiệp vụ chuẩn hóa, loại bỏ hoàn toàn PII và secret.

### 3.2. Shape B — Single Agent ReAct (`src/lab8/shapes/single.py`)
- **Nguyên lý hoạt động**: Vòng lặp ReAct tối đa 8 bước (`run_react`).
- **Ranh giới Code/Model**: Model chỉ được chọn các công cụ đọc (`lookup_order`, `lookup_policy`, `compute_compensation`). Quyết định xuất tiền bồi hoàn sau vòng lặp do code của shape thực hiện qua host.
- **Xử lý điểm yếu của Swarm**: Kiên quyết lấy số ngày trễ từ DB `order`, không bị lừa bởi prompt injection / lời khai trong `ticket`.

### 3.3. Shape C — Orchestrator + Handoff (`src/lab8/shapes/orchestrator.py`)
- **Nguyên lý hoạt động**: Kiến trúc điều phối tập trung với các worker investigators chỉ có quyền đọc (`run_readonly_investigators`).
- **Giao thức Handoff an toàn**: Đóng gói bằng `lab8.handoff.make_handoff` với allowlist công cụ đọc rõ ràng. Dữ liệu trong `facts` được sanitize triệt để, không chuyển giao `parent_secret` hay `raw_headers`.

## 4. Kết quả

### 4.1. Bảng so sánh 4 Shape trên bộ Public Claims (5 seeds: 11, 22, 33, 44, 55)

Số liệu trích xuất trực tiếp từ file do benchmark sinh ra (`src/reports/benchmark.json`):

| Shape | Pass Rate | Pass^5 | Variance | Min | Max | Cost/Success (VND) | Mean Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Workflow** | **1.000** | **1.000** | **0.000000** | **1.000** | **1.000** | **34.29** | 4.43 |
| **Single** | 1.000 | 1.000 | 0.000000 | 1.000 | 1.000 | 28.79 | 1.86 |
| **Orchestrator** | 1.000 | 1.000 | 0.000000 | 1.000 | 1.000 | 47.36 | 2.79 |
| **Swarm** | 0.986 | 0.929 | 0.000816 | 0.929 | 1.000 | 49.57 | 2.80 |

*(Ghi chú: Swarm gặp lỗi `status resolved != denied x1` tại seed 55 trên claim C-002 do tin ticket thay vì DB).*

### 4.2. Crash Safety & Độ tin cậy
- Kiểm thử Crash Suite: Đạt **20/20** an toàn tuyệt đối (`src/reports/crash.json`), đảm bảo tính Idempotency (khóa `refund:{claim_id}`) và không bao giờ xuất trùng 2 khoản hoàn tiền cho một claim.
- Rò rỉ thông tin: **0 Secret Leak / 0 Approval Bypass** trên toàn bộ 4 shape.

Quyết định kiến trúc chọn **Workflow**: xem chi tiết tại `report/team/decision_adr.md`.
Phiếu nghiên cứu phân loại lỗi theo MAST (R2): xem tại `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

1. **Lỗi lệch ngày trễ (Variance ở Seed 55)**:
   - *Khó khăn*: Tại seed 55 của claim C-002, Swarm bị prompt injection từ ticket dẫn đến bồi thường sai.
   - *Xử lý*: Ở Workflow và Single/Orchestrator, nhóm cài đặt nguyên tắc bất di bất dịch: trường `delay_days` và `order_id` phải đọc từ DB đơn hàng có cấu trúc, tuyệt đối không lấy từ text tự do của người dùng.
2. **Đảm bảo Crash Recovery và Per-order Cap**:
   - *Khó khăn*: Một số kịch bản hoàn tiền theo đợt dễ bị tính trùng hoặc trừ sai phần đã hoàn trước đó.
   - *Xử lý*: Luôn truyền quote đầy đủ vào `durability.issue_refund`, để Host tự động kiểm tra trần còn lại của đơn hàng và ghi nhận dòng `refund_committed`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`:
- **Bùi Xuân Thành**: Cài đặt Shape Workflow, tích hợp kiểm thử CI/CD và test giới hạn trần đơn hàng T14.
- **Phạm Tuấn Anh**: Cài đặt Shape Single Agent ReAct, chống prompt injection và bộ test `test_single_student.py`.
- **Nguyễn Mạnh Quyền**: Cài đặt Shape Orchestrator, giao thức Handoff an toàn và bộ test `test_orchestrator.py`.
- **Trịnh Thanh Tùng**: Kiểm thử Swarm Reference, thực thi Crash Test Suite 20/20, Benchmark 4 shape và viết test lỗi variance seed 55.

## 7. Hạn chế và hướng cải thiện

- MockLLM trong bài lab là mô hình mô phỏng tất định, chi phí là VND giả lập. Chưa phản ánh đầy đủ độ trễ mạng thực tế (`latency unavailable`).
- Nếu bài toán mở rộng sang việc đàm phán linh hoạt với khách hàng hoặc xử lý hóa đơn quét ảnh/chứng từ phi cấu trúc phức tạp, kiến trúc Single Agent hoặc Orchestrator sẽ phát huy thế mạnh vượt trội hơn Workflow.

## 8. Tài liệu tham khảo

1. Google Research (2026), *Towards a Science of Scaling Agent Systems*.
2. NeurIPS (2025), *Why Do Multi-Agent LLM Systems Fail? (MAST Taxonomy)*.
3. EMNLP (2026), *Rethinking Evaluation of MAS Efficiency*.
