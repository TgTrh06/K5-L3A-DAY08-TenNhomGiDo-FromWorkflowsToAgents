# Báo cáo cá nhân — 2A202603456_TrinhThanhTung

## 1. Thông tin thành viên

- Họ tên: Trịnh Thành Tùng
- MSSV: 2A202603456
- Email: 26ai.tungtt2@vinuni.edu.vn
- GitHub: TgTrh06

## 2. Phần việc phụ trách

- **Kiến trúc & Shape:** Phụ trách đối chuẩn, phân tích hiệu năng và độ ổn định của Shape D (`swarm_reference`).
- **Kiểm thử & Đảm bảo an toàn (Evaluation & Crash safety):**
  - Thực thi bộ test đối chứng `test_swarm_reference.py`, chạy benchmark trên 5 seed (`11, 22, 33, 44, 55`).
  - Chạy và kiểm tra crash test suite `python -m lab8.crash_test --count 20` để đảm bảo tính Idempotency và an toàn giao dịch (`crash_safety = 20/20`).
  - Viết test case mới kiểm tra hiện tượng variance / prompt injection của Swarm khi seed chia hết cho 5 (`REFERENCE_WEAKNESS`).
- **Phân tích số liệu:** Đóng góp số liệu benchmark đối chuẩn cho tài liệu quyết định kiến trúc (`report/team/decision_adr.md`) và phiếu nghiên cứu (`report/team/research_card.md`).

## 3. Đóng góp cụ thể

- **Viết test mới:** Bổ sung test `test_swarm_seed_divisible_by_5_overrides_delay_with_ticket` trong [src/tests/test_swarm_reference.py]. Test kiểm tra và xác nhận khi gặp seed chia hết cho 5 (như seed 55), Swarm tin dữ liệu ticket sai lệch thay vì DB đơn hàng và ghi nhận chính xác sự kiện `model_override` trong trace JSON.
- **Thực thi Benchmark Swarm:** Chạy `benchmark` trên 12 claims public qua 5 seed, ghi nhận pass rate đạt 0.986, pass^5 đạt 0.929, variance 0.000816, cost/success 49.57 VND (mô phỏng).
- **Quyết định kỹ thuật:**
  - Nhận diện rõ rủi ro của mô hình Multi-agent phân tán không có Verifier tập trung: Swarm có cost cao (~49.57 VND) và variance lớn ở seed 55 do không có cơ chế đối chiếu ràng buộc dữ liệu có cấu trúc.
  - Ủng hộ quyết định kiến trúc: Workflow hoặc Single Agent an toàn và ổn định hơn Swarm cho bài toán bồi thường LogiX-VN.

## 4. Bằng chứng

- **Test đã thêm:** `tests/test_swarm_reference.py::test_swarm_seed_divisible_by_5_overrides_delay_with_ticket` (kết quả `python -m pytest -q tests/test_swarm_reference.py` đạt 14/14 passed).
- **Benchmark sinh ra:** [src/reports/benchmark_swarm.json] với chỉ số:
  - `pass`: 0.986
  - `pass^5`: 0.929
  - `variance`: 0.000816
  - `cost/success`: 49.57 VND
- **Báo cáo crash test:** [src/reports/crash.json] đạt `20/20` an toàn tuyệt đối trước sự cố crash và phục hồi giao dịch.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity AI Assistant (Gemini 3.8 Flash).
- **Mục đích:** Hỗ trợ phân tích mã nguồn `swarm_reference.py`, tra cứu cấu trúc trace contract và gợi ý cú pháp test case `pytest` kiểm tra sự kiện `model_override`.
- **Cách tự kiểm tra (Verification):**
  - Chạy trực tiếp `pytest -q tests/test_swarm_reference.py` trên môi trường terminal local đảm bảo test pass 100%.
  - Trực tiếp kiểm tra và đọc file `trace-*.json` sinh ra từ `RunResult.trace_path` để xác nhận đúng payload của sự kiện `model_override`.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các nhiệm vụ được phân công cho Shape Swarm, Benchmark và Crash Evaluation.
- Thực hiện nghiêm túc quy định bảo mật: không làm lộ secret, không sửa đổi code host/metrics trái phép.
- Đạt chuẩn toàn bộ test của module phụ trách.