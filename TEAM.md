# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Tuấn Anh | 2A202603503 | pta070707123@gmail.com | phamtuananhhatay | single |
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Tuấn Anh | single | 5b65ad8, 0ca10b7 | tests/test_single_student.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603503_PhamTuanAnh

### Phần việc phụ trách

- Phụ trách toàn diện Shape B — Single ReAct Agent (`src/lab8/shapes/single.py`).

### Đóng góp cụ thể

- Triển khai hàm `run_claim` với vòng lặp ReAct `run_react` (tối đa 8 bước), ranh giới bảo mật Host-Agent và xử lý độ bền / crash safety T11, T12.
- Viết 8 test cases trong `src/tests/test_single_student.py` kiểm thử luồng ReAct, tính bất biến trước prompt injection từ ticket và an toàn bí mật trace.

### Bằng chứng

- Commit: `5b65ad8`, `0ca10b7`.
- File báo cáo cá nhân: `report/team/2A202603503_PhamTuanAnh.md`.
- Kết quả test: 62/62 test ma trận student pass, 8/8 unit test mới pass.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
