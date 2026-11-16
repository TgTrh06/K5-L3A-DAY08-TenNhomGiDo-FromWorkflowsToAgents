# Báo cáo cá nhân — Bùi Xuân Thành

## 1. Thông tin thành viên

- Họ tên: Bùi Xuân Thành
- MSSV: 2A202603521
- Email: 26ai.thanhbx@vinuni.edu.vn
- GitHub: KDAGRAGAS

## 2. Phần việc phụ trách

- Phụ trách Shape A (`workflow`) và kiểm tra shape được đăng ký, gọi qua runner/CLI và harness benchmark.

## 3. Đóng góp cụ thể

- Hoàn thiện `src/lab8/shapes/workflow.py`: đọc claim và order qua helper an toàn, tính quote bằng `compute_compensation`, rồi chuyển quote đầy đủ cho host xử lý approval, giới hạn hoàn theo đơn và idempotency.
- Chuyển tiếp `crash_at`, để `InjectedCrash` được harness nhận biết, và ghi trace không chứa ticket thô hay dữ liệu riêng tư.
- Thêm test `src/tests/test_workflow.py::test_workflow_quotes_full_entitlement_and_host_pays_remaining_cap`, kiểm tra T14: quote 150.000 VND, ledger ghi phần còn lại 120.000 VND và có đúng một audit `refund_committed`.
- Quyết định kỹ thuật: code quyết định số tiền; host là nơi duy nhất kiểm duyệt và ghi refund.
- Commit chính: `f55bee2`.

## 4. Bằng chứng

- Commit: [f55bee2 — Hoàn thành shape workflow và kiểm thử](https://github.com/TgTrh06/K5-L3A-DAY08-TenNhomGiDo-FromWorkflowsToAgents/commit/f55bee2).
- Test riêng: `python -m pytest -q tests/test_workflow.py` — 1 passed.
- Ma trận workflow: `python -m pytest -q -m student -o addopts= -k workflow` — 62 passed.
- Cổng host: `python -m pytest -q` — 55 passed.
- Run ID dẫn chứng: `R-workflow-C-014-s11`.

## 5. Công cụ AI đã dùng

- Công cụ: Codex (GPT-6).
- Cách dùng: hỗ trợ đọc yêu cầu, hỗ trợ triển khai workflow và hỗ trợ viết test cho trường hợp T14.
- Tự kiểm tra: hỗ trợ đối chiếu với luật nghiệp vụ và contract; hỗ trợ chạy test riêng T14 (1 passed), bộ workflow (62 passed) và cổng host (55 passed).

## 6. Tự đánh giá

- Hoàn thành và kiểm thử luồng workflow trên các test public; các test workflow và cổng host đều xanh.
- Chưa chạy benchmark hoặc hidden self-check, nên chưa kết luận về pass rate hidden hay lựa chọn shape cuối cùng của nhóm.
