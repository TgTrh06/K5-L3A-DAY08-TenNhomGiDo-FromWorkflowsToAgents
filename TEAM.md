# Team

## Thông tin nhóm

- Tên nhóm: TenNhomGiDo
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhomGiDo-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/TgTrh06/K5-L3A-DAY08-TenNhomGiDo-FromWorkflowsToAgents, nhánh submit

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Bùi Xuân Thành | 2A202603521 | 26ai.thanhbx@vinuni.edu.vn | KDAGRAGAS | workflow + integration |
| 2 | Phạm Tuấn Anh | 2A202603503 | 26ai.anhpt9@vinuni.edu.vn | phamtuananhhatay | single |
| 3 | Nguyễn Mạnh Quyền | 2A202603518 | 26ai.quyennm3@vinuni.edu.vn | manhquyenkma | orchestrator + handoff |
| 4 | Trịnh Thanh Tùng | 2A202603456 | 26ai.tungtt2@vinuni.edu.vn | TgTrh06 | ledger + evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Bùi Xuân Thành | workflow + integration | f55bee2 | tests/test_workflow.py |
| Phạm Tuấn Anh | single | 0ca10b7 | tests/test_single_student.py |
| Nguyễn Mạnh Quyền | orchestrator + handoff | a189b7c | tests/test_orchestrator.py |
| Trịnh Thanh Tùng | ledger + evaluation | 439db4e | tests/test_swarm_reference.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603521_BuiXuanThanh

### Phần việc phụ trách

- Phụ trách Shape A (`workflow`) và tích hợp kiểm thử qua runner/CLI và harness benchmark.

### Đóng góp cụ thể

- Hoàn thiện `src/lab8/shapes/workflow.py`: đọc claim và order qua helper an toàn, tính quote bằng `compute_compensation`, chuyển quote đầy đủ cho host xử lý approval, giới hạn hoàn theo đơn và idempotency.
- Chuyển tiếp `crash_at`, để `InjectedCrash` được harness nhận biết, ghi trace an toàn không lộ PII.
- Thêm test `src/tests/test_workflow.py::test_workflow_quotes_full_entitlement_and_host_pays_remaining_cap`.

### Bằng chứng

- Commit: `f55bee2`
- Test: `tests/test_workflow.py` (1 passed)
- Run ID dẫn chứng: `R-workflow-C-014-s11`

## 2A202603503_PhamTuanAnh

### Phần việc phụ trách

- Phụ trách Shape B — Single Agent (ReAct) tại `src/lab8/shapes/single.py`.
- Thiết kế vòng lặp ReAct có giới hạn tối đa 8 bước, phân tách quyền đọc (Model) và quyền ghi (Host).

### Đóng góp cụ thể

- Xây dựng vòng lặp ReAct qua `lab8.runtime.run_react` với hàm callback `decide(seen)`.
- Luôn trích xuất `delay_days` từ DB `order`, bỏ qua prompt injection trong `ticket` (sửa triệt để T02 seed 55).
- Đảm bảo Crash Safety: chuyển tiếp `crash_at` và re-raise `InjectedCrash`.
- Viết bộ unit test `src/tests/test_single_student.py` (8 test cases).

### Bằng chứng

- Commit: `5b65ad8`, `0ca10b7`
- Test: `tests/test_single_student.py` (8 passed)
- Run ID dẫn chứng: `R-single-C-001-s11`

## 2A202603518_NguyenManhQuyen

### Phần việc phụ trách

- Phụ trách Shape C — Orchestrator + Handoff tại `src/lab8/shapes/orchestrator.py`.
- Thiết kế giao thức Handoff an toàn, phân luồng investigator read-only và crash recovery.

### Đóng góp cụ thể

- Triển khai Shape C với cơ chế đóng gói `lab8.handoff.make_handoff` và allowlist tools đọc an toàn.
- Không lộ `parent_secret`, `raw_headers` hay PII qua ranh giới agent.
- Đảm bảo crash safety 20/20 và idempotency khi re-run cùng claim.
- Viết 18 test cases toàn diện trong `src/tests/test_orchestrator.py`.

### Bằng chứng

- Commit: `a189b7c`
- Test: `tests/test_orchestrator.py` (18 passed)
- Run ID dẫn chứng: `R-orchestrator-C-001-s11`

## 2A202603456_TrinhThanhTung

### Phần việc phụ trách

- Phụ trách đối chuẩn, đo lường độ ổn định Shape D (`swarm_reference`) và Crash Suite Evaluation.
- Quản lý benchmark trên 5 seeds (`11, 22, 33, 44, 55`).

### Đóng góp cụ thể

- Viết test mới `test_swarm_seed_divisible_by_5_overrides_delay_with_ticket` trong `src/tests/test_swarm_reference.py` kiểm tra hiện tượng seed % 5 == 0 tin nhầm ticket và ghi sự kiện `model_override`.
- Chạy đối chuẩn benchmark 5 seed và kiểm thử độ bền hệ thống `crash_test --count 20` đạt 20/20 safe.
- Đo lường chi phí mô phỏng (cost/success) và độ dao động (variance) của mô hình multi-agent phân tán.

### Bằng chứng

- Commit: `439db4e`
- Test: `tests/test_swarm_reference.py::test_swarm_seed_divisible_by_5_overrides_delay_with_ticket` (14 passed)
- Benchmark: `reports/benchmark_swarm.json`
- Crash: `reports/crash.json` (20/20 safe)
