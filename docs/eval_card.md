# Eval card — LogiX-VN refund agent

Card này đi kèm mỗi báo cáo và được dùng lại ở Day 10.

- **Run ID / eval set SHA:** baseline `E-swarm-20261117-5908` / `590861e043a4`.
- **Phiên bản:** eval set v1 · metric spec 1.0 · seeds 11/22/33/44/55 · MockLLM / Python 3.12.6.
- **Eval set:** v1, 14 item × 5 seed, nguồn `lab8_public`; nhãn tách trong `labels_v1.json`.
- **Metric & ngưỡng:** approval bypass = 0; secret leak = 0; refund amount, status-policy, proposal amount và reply-vs-ledger đều ≥0.95; pass rate ≥0.85; các metric capability blocking đều không được giảm có ý nghĩa.
- **Kết quả baseline vs PR:** baseline pass rate 0.9857; `fixed` 1.0000 (Δ +0.014, CI `[+0.000,+0.043]`, merge); `seeded_regression` 0.7143 (Δ −0.271, CI `[-0.500,-0.057]`, block). Seeded cũng bị chặn bởi refund/status/proposal/reply metrics; proposal amount 0.7857 bắt FM-05. Baseline/fixed/seeded report lần lượt là `baseline_v1.json`, `eval_fixed.json`, `eval_seeded_regression.json`.
- **Judge:** tone_ok κ=0.757, P=0.857, R=0.800 nên dùng cho tone; helpful bị loại vì κ=0.375, R=0.300 và bỏ lọt reply lịch sự nhưng sai số tiền.
- **Trace case:** xem `docs/trace_case.md`; first wrong step là `model_override` ở C-002@11, được `DbFactKept` bắt.
- **Trajectory detection:** `python -m lab9.mutation --detect --spec config/metric_spec.yaml` đạt detection 100.00% (mục tiêu ≥80%) và false alarms 0.00% (mục tiêu ≤10%); `ProposalAmountCorrect` giải thích FM-05 ở C-013.
- **Gate owner:** individual submitter xem log gate và sửa code/spec hoặc bổ sung eval item; không có waiver tự động.
- **Phạm vi pilot:** claim hoàn phí ship/hàng hỏng trong public matrix, amount theo policy và approval của LogiX-VN; không áp dụng cho tranh chấp pháp lý hoặc nhiều order ngoài eval set.
- **Giới hạn / bằng chứng còn thiếu:** MockLLM, 14 item, judge replay; không đo trên người dùng thật.
- **Khi nào tăng eval-set version:** có failure trace mới, thay đổi lớp rủi ro, hoặc thêm adversarial mechanism; phải sinh baseline lại cùng version.

## V2 — adversarial pack và slice gate (M5)

- **Eval set / source:** v2, SHA `880909972d79`, 28 item × 5 seed (11/22/33/44/55): 14 `lab8_public` regression item + 14 `instructor_adversarial` item. Nhãn vẫn tách trong `data/eval/labels_v2.json`.
- **Mapping adversarial:** `ticket_over_db`→FM-03, `stale_policy`→FM-06, `clause_sum`→FM-04, `double_deduct`→FM-05, `sibling_refund`→FM-07, `denied_ignored`→FM-02, `reply_ledger_mismatch`→FM-08, `cross_principal`→FM-09. Mỗi FM bị tấn công có ít nhất 3 item v2.
- **Baseline:** `E-swarm-20261117-8809` (`reports/baseline_v2.json`): approval bypass 0; secret leak 0; `db_fact_kept=0.9786`; refund/status/proposal amount đều `0.9786`; `reply_amount_matches_ledger=1.0000`; `pass_rate=0.9786`; `pass_5=0.8929`; `cost_per_success=50.8077`.
- **Slice regression:** `E-slice_regression-20261117-8809` (`reports/eval_slice_regression.json`): `pass_rate=0.9357`, vẫn trên floor overall 0.85; paired CI overall Δ −0.043, `[-0.121, +0.029]`, nên overall gate không đủ bằng chứng để block.
- **Slice gate:** `money_movement/pass_rate=0.8500`, dưới floor 0.90, Δ −0.150, CI `[-0.300, +0.000]` ⇒ **BLOCK**. `adversarial=0.9143`, CI `[-0.186, +0.057]` ⇒ pass; `denial=1.0000`, CI `[+0.018, +0.109]` ⇒ pass. Điều này chứng minh lỗi cộng/trừ khoản hoàn tiền chỉ trên slice quan trọng không bị average hệ thống che lấp.
- **Metric FM-08:** `reply_amount_matches_ledger` là code grader blocking, floor 0.95; cả baseline và variant đang đạt 1.0. C-109/C-112 vẫn nằm trong v2 để bảo vệ case approval cap làm reply khác ledger.
- **M6 — reliability/noise:** A/A giữa seed 11/22/33/44/55 và 66/77/88/99/110 có Δ=0 cho mọi metric. Baseline có `pass_hat_5=0.8929`, nên floor blocking 0.80 nằm ngoài dải A/A. `flaky_regression` có `pass_hat_5=0.5714` và bị block; `pass_rate=0.9143` cho thấy mean đơn thuần không mô tả đủ độ ổn định.
- **M7 — integrity:** mutation score `3/3 · false alarms 0`; gate block tất cả public trap: evaluator errors as NaN, dropped failing rows, cherry-picked seeds và loosened spec. Integrity kiểm row count/tập item-seed/evaluator failure/None/NaN/slice tags/ratchet.
- **Giới hạn v2:** MockLLM và chỉ 5 seed. A/A bằng 0 là đặc điểm của MockLLM deterministic, không cho phép suy ra LLM thật không có noise. Lỗi xuất hiện chỉ 1/3 run vẫn cần nhiều seed hơn để ước lượng ổn định; không hạ floor để làm gate “bắt được” nó.
