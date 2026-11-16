# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: e356009
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 34.29
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 leak / 0 bypass

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Nhóm chọn kiến trúc `workflow` theo nguyên lý "kiến trúc ít tự chủ nhất mà vẫn hoàn thành nhiệm vụ" (Occam's Razor cho Agent Systems). Trên cùng 12 claim public qua 5 seed (tổng 60 trials), `workflow` đạt độ tin cậy tuyệt đối (pass rate 1.000, pass^5 1.000, variance 0.000000) và chi phí bồi hoàn mô phỏng cực kỳ tiết kiệm (34.29 VND/thành công). So sánh trực tiếp với `swarm`, swarm có chi phí cao nhất (49.57 VND) và gặp hiện tượng mất ổn định (variance 0.000816, pass^5 giảm xuống 0.929 do lỗi seed 55 tin lời khai người dùng). Vì nghiệp vụ hoàn tiền của LogiX-VN là bài toán quy tắc tài chính tất định, việc thực thi bằng code deterministic mang lại độ chính xác, an toàn và hiệu quả kinh tế vượt trội so với multi-agent.

## Có đáng đổi lấy multi-agent không

Không đáng đổi. Việc chuyển sang multi-agent phân tán (`swarm`) không làm tăng pass rate mà trái lại làm tăng chi phí tới 44.5% (từ 34.29 VND lên 49.57 VND), đồng thời khuếch đại rủi ro lỗi và dao động seed. Quyết định kiến trúc chỉ đảo lại khi bài toán xuất hiện các yếu tố mở mà workflow không thể giải quyết bằng rule cứng: (1) Ticket chứa thông tin bán cấu trúc hoặc phi cấu trúc đa ngôn ngữ phức tạp cần suy luận ngôn ngữ sâu, (2) Khung chính sách bồi thường thay đổi linh hoạt theo ngữ cảnh đàm phán với khách hàng, hoặc (3) Hệ thống cần giao tiếp mở với các bên thứ ba phi tập trung mà không thể biểu diễn bằng pipeline tuần tự.

## Trace và bằng chứng

Trace của `workflow` ghi nhận đầy đủ các sự kiện nghiệp vụ tối thiểu cần thiết để phục vụ audit: `claim_lookup`, `order_lookup`, `policy_evaluated`, `compensation_computed` và `refund_issued` (hoặc `status_resolved`/`status_denied`). Hệ thống cố ý **KHÔNG** ghi các field: `parent_secret`, `CANARY_SECRET_*`, `raw_headers`, thông tin định danh cá nhân (PII như SĐT, địa chỉ nhà khách hàng), và toàn bộ nội dung ticket thô. Nếu trace nằm ngoài vùng scanner tự động, đội bảo mật có thể kiểm chứng qua audit log của Host (`db.py` và `durability.py`): mọi khoản tiền ghi vào ledger đều có audit event `refund_committed` gắn kèm hash băm xác thực, không có bản ghi nào bị lộ dữ liệu nhạy cảm hay bypass bước phê duyệt (approval binding).

## Giới hạn

MockLLM trong bài lab là mô hình mô phỏng tất định theo seed, không phản ánh toàn bộ sự phong phú và độ trễ ngẫu nhiên của các LLM sản xuất thực tế. Thước đo latency là `unavailable` (chi phí tính bằng VND mô phỏng chứ không phải hóa đơn API thực). Nhóm cam kết dữ liệu benchmark trung thực từ `reports/benchmark.json`, không chỉnh sửa thủ công để đối phó tiêu chí đánh giá.
