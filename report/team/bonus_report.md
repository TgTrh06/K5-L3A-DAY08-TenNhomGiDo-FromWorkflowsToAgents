# Bonus report: B3

- Topic + nguồn (tên, năm, slide): B3 · Verifier/aggregator chống khuếch đại lỗi, Google Research 2026, *Towards a Science of Scaling Agent Systems* (Slide 17, 22, 42).
- CLAIM của nguồn (1 câu): Các agent độc lập trong hệ thống multi-agent có xu hướng khuếch đại sai số lên tới 17.2×, nhưng cơ chế orchestration tập trung kết hợp verifier/evaluator có thể kìm hãm hệ số khuếch đại lỗi xuống còn 4.4×.
- BOUNDARY của nguồn (1 câu): Giả định hệ thống có thể đối chiếu các dữ kiện đầu ra trung gian của LLM với nguồn sự thật có cấu trúc (ground-truth structured database) trước khi cam kết trạng thái ghi.
- Shape nhóm đem đo: `swarm_verified` (được đăng ký qua cờ `--extra-shape swarm_verified=bonus.swarm_verified:run_claim`).

## 1. Hypothesis của nhóm trên task LogiX

Nếu bổ sung một bước **Verifier bằng code tất định** (`code-level verification gate`) ngay trước khi gọi `durability.issue_refund` nhằm đối chiếu chéo các thuộc tính quyết định bồi thường (`delay_days`, `status`, `damage_verified`) với bản ghi `orders` trong SQLite, thì:
- Pass rate của Swarm sẽ tăng từ **0.986** lên **1.000**, và $\text{pass}^5$ tăng từ **0.929** lên **1.000**.
- Hiện tượng dao động seed (variance) sẽ giảm từ **0.000816** về **0.000000** (triệt tiêu hoàn toàn lỗi Task Verification tại case C-002 seed 55).
- Đổi lại, chi phí thực thi `cost/success` sẽ tăng thêm do chi phí chạy công cụ verifier và recompute compensation.

## 2. Kết quả đo

Lệnh chạy tái lập kết quả thực nghiệm:
```bash
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark.json
```

Bảng số liệu đối chuẩn trích xuất từ `src/reports/bonus_benchmark.json`:

| Shape | Pass rate | Pass^5 | Variance | Min | Max | Cost/Success (VND) | Mean Steps | Safety counts |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `workflow` | 1.000 | 1.000 | 0.000000 | 1.000 | 1.000 | 34.29 | 4.43 | 0 leak / 0 bypass |
| `swarm` | 0.986 | 0.929 | 0.000816 | 0.929 | 1.000 | 49.57 | 2.80 | 0 leak / 0 bypass |
| `swarm_verified` | **1.000** | **1.000** | **0.000000** | **1.000** | **1.000** | **57.29** | 2.81 | 0 leak / 0 bypass |

- **Số lần Verifier can thiệp:** Trong 14 claims public × 5 seeds (70 trials), Verifier can thiệp chính xác ở các trial có `seed % 5 == 0` (đặc biệt là C-002 seed 55), ghi nhận sự kiện `verifier_override` và ngăn chặn thành công việc giải ngân sai quy định.
- **Bộ case đối kháng tự viết:** Đạt **8/8 passed** trên `src/bonus/cases.jsonl` và `src/bonus/world.json` (kiểm chứng độc lập qua `pytest tests/test_bonus_b3.py`).

## 3. Phân tích

- **Ủng hộ hay bác bỏ hypothesis:** Kết quả thực nghiệm **ủng hộ hoàn toàn** hypothesis và claim của Google Research. Bước Verifier bằng code đã chặn đứng sự lan truyền của thông tin sai lệch từ ticket (`delay_days = 5` thay vì `2`), đưa độ tin cậy của Swarm về ngang bằng với Workflow (pass^5 đạt 100%, 0 variance).
- **Chi phí đánh đổi:** Để đạt được độ tin cậy này, `swarm_verified` phải trả chi phí 57.29 VND/thành công, cao hơn Swarm gốc (49.57 VND) và cao hơn 67.1% so với Workflow (34.29 VND).
- **Giá trị còn lại của Swarm:** Khi Verifier đã kiểm soát toàn bộ các thuộc tính tài chính cốt lõi, phần cộng tác đa tác nhân của Swarm (các lượt gọi `peer`, `parse`) thực chất trở thành gánh nặng dư thừa (redundant overhead). Điều này củng cố thêm kết luận: với các bài toán quy tắc nghiệp vụ chặt chẽ, việc dùng Workflow thuần code hoặc Single Agent có guardrail ưu việt hơn hẳn việc để một mạng lưới multi-agent tự trao đổi rồi phải dựng thêm một Verifier để sửa sai.
- **Giới hạn thực nghiệm:** Thử nghiệm sử dụng MockLLM với các giá trị seed tất định và chi phí VND mô phỏng (latency `unavailable`). Trong môi trường sản xuất với LLM thương mại có tính stochastic cao hơn, sự khuếch đại lỗi của Swarm gốc có thể còn nghiêm trọng hơn.
