# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Đạt | Dùng cho đánh giá tone; không thay code grader cho tiền/approval |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không đạt (κ, recall) | Loại khỏi gate |

`tone_ok`: confusion matrix = TP 24, FP 4, FN 6, TN 66. Tỷ lệ FAIL judge quan sát là 0.28; sau Rogan–Gladen là 0.30.

`helpful`: confusion matrix = TP 9, FP 0, FN 21, TN 70. Tỷ lệ FAIL judge quan sát là 0.09; sau Rogan–Gladen là 0.30. Precision hoàn hảo ở đây không đủ: judge chỉ đánh FAIL khi rất chắc chắn và bỏ lọt 70% lỗi thật.

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | H-008 (tone) | PASS | FAIL | Người | `em`/`nha` quá suồng sã với khách; thêm ví dụ cấm kiểu xưng hô này vào rubric judge. |
| 2 | H-017 (tone) | PASS | FAIL | Người | Judge nhầm `bạn ơi`/`rồi nha` là thân thiện; rubric phải tách “thân thiện” khỏi tôn xưng phù hợp. |
| 3 | H-029 (tone) | PASS | FAIL | Người | Cụm “không cần nhắn thêm” mang tính ra lệnh; thêm nhóm hành vi dismissive/commanding vào rubric. |
| 4 | H-042 (tone) | FAIL | PASS | Người | Reply ngắn nhưng đủ lịch sự; judge đã tự đòi “xin lỗi” ngoài rubric. Bỏ yêu cầu xin lỗi bắt buộc. |
| 5 | H-051 (tone) | FAIL | PASS | Người | Từ `refund` được CS LogiX cho phép; thêm lexical allowlist hoặc ví dụ chấp nhận từ này. |
| 6 | HL-015 (helpful) | PASS | FAIL | Người | Reply lịch sự nhưng nói 55.000đ thay vì ledger 40.000đ; helpful judge không có fact để kiểm chứng số tiền. Không dùng judge này cho outcome. |
| 7 | HL-016 (helpful) | PASS | FAIL | Người | Lời xin lỗi dài che sai số tiền 55.000đ/35.000đ; cần code grader reply-vs-ledger ở M3. |
| 8 | HL-020 (helpful) | PASS | FAIL | Người | Reply nói 90.000đ, ledger 120.000đ; đây là false negative có tác động tiền trực tiếp. |
| 9 | HL-028 (helpful) | PASS | FAIL | Người | Văn phong rất lịch sự nhưng số tiền 50.000đ sai so với ledger 35.000đ; style không chứng minh helpful/outcome đúng. |
| 10 | HL-035 (helpful) | PASS | FAIL | Người | Lời xin lỗi không bù được fact sai: 50.000đ so với ledger 35.000đ. Giữ human label và loại judge. |

## Kết luận
- `tone_ok` đạt cả ba floor (κ=0.757, P=0.857, R=0.800), nên có thể dùng như một tín hiệu phụ cho tone. Các lỗi còn lại được xử lý bằng rubric rõ hơn, nhưng không dùng tone judge để quyết định tiền hoặc approval.
- `helpful` bị loại: κ=0.375 và recall=0.300, thấp hơn floor tương ứng 0.600 và 0.700. Ma trận có 21 false negative; phần lớn là reply lịch sự nhưng nói sai số tiền, nên gate dựa vào judge này sẽ cho merge lỗi hệ trọng.
- M3 phải dùng code grader đọc ledger/approval cho mọi lỗi tiền và approval; không cố sửa prompt để “làm đẹp” calibration của `helpful`.
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật.
