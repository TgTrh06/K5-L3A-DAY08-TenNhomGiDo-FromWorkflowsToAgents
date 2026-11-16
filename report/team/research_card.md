# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, Why Do Multi-Agent LLM Systems Fail?, Human annotation empirical study (kappa = 0.88) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | 14 failure modes trong hệ thống Multi-Agent chia làm 3 nhóm chính: System Design, Inter-agent Misalignment, và Task Verification. Tỷ lệ lỗi lớn bắt nguồn từ việc thiếu cơ chế độc lập kiểm chứng kết quả trung gian giữa các agents. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nghiên cứu giới hạn trên các bài toán cộng tác đa tác nhân phức tạp với human annotation; kết luận dựa trên giả định các agent có quyền tự chủ trao đổi thông tin không qua bước thẩm định dữ liệu gốc có cấu trúc. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu chuyển từ Swarm (có lỗ hổng tin prompt/ticket) sang Workflow (kiểm chứng bằng code qua DB), pass^5 sẽ tăng từ 0.929 lên 1.000, variance giảm từ 0.000816 về 0.000000, triệt tiêu hoàn toàn lỗi Task Verification tại case C-002 seed 55. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định MockLLM, bộ 12 claims public, 5 seeds (11, 22, 33, 44, 55), bảng giá và host validator. Biến duy nhất thay đổi: cơ chế ra quyết định số ngày trễ (Swarm dùng hội thoại agent có thể bị model_override vs Workflow đọc trực tiếp từ database). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi Task Verification (tin dữ liệu người dùng khai gian trong ticket thay vì DB tại seed 55); đo lường bằng tỷ lệ chênh lệch pass rate (0.986 vs 1.000), pass^5 (0.929 vs 1.000) và variance (0.000816 vs 0.000000). |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng hoàn toàn với Hypothesis. Số liệu thực nghiệm chứng minh:
  - `workflow`: pass rate = 1.000, pass^5 = 1.000, variance = 0.000000, cost/success = 34.29 VND.
  - `swarm`: pass rate = 0.986, pass^5 = 0.929, variance = 0.000816, cost/success = 49.57 VND (gặp lỗi `status resolved != denied x1` tại seed 55 trên claim C-002).
  - Phân tích: Swarm gặp thất bại thuộc nhóm Task Verification do thiếu rào chắn code (code gate) để xác thực chéo giữa lời khai ticket và DB đơn hàng, dẫn đến sai lệch kết quả bồi thường.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
