# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Case đã audit — FM-03 ticket trust

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`; report `E-seeded_regression-20261117-5908` |
| Triệu chứng | Lab 8 fail `status resolved != denied`; ledger hoàn 20.000đ, trong khi label yêu cầu refund 0. |
| Bước sai đầu tiên | Event 3, `model_override`: `{"delay_days": 5}` ghi đè delay DB 2 ngày bằng con số trong ticket. |
| Vì sao là bước *đầu tiên* | Event 1 handoff chỉ giới hạn tool đọc; event 2 investigator lấy order O-202 từ DB. Chỉ event 3 mới thay fact đã xác minh. |
| Failure mode | FM-03 `ticket_trust` trong `docs/failure_taxonomy.md`. |
| Đối chứng | `fixed C-002@11`: không có `model_override`; event 3 quote là 0/no_entitlement, reply denied, ledger 0 đúng label. |
| Regression test | `tests/test_lab9_graders.py::test_override_event_breaks_db_fact`; `DbFactKept` fail trên event override và pass trên trial sạch. |
| Chưa chắc chắn | Trace chứng minh override và hậu quả ở C-002, nhưng không tự chứng minh mọi wording ticket có cùng mức rủi ro; v2 thêm C-101/C-102 để mở rộng coverage. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
