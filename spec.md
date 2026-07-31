# AI SPEC — LabGuard · Nhóm HUST

Hướng: C — Làn mở · Loại: Tính năng mới
Trạng thái bằng chứng: phần kỹ thuật đã đo; đã có khảo sát pain tổng hợp 50 phản hồi; quote, thời gian và validation prototype vẫn đang chờ team bổ sung.

## §1. User & Job

- Job executor + workflow: học viên vừa hoàn thành một bài lab, trước khi dùng lượt nộp phải đọc Codelab, rubric GitHub và rà lại repo.
- Core JTBD: **Đối chiếu bài làm với toàn bộ yêu cầu trước khi nộp để không mất điểm vì một thiếu sót có thể phát hiện được.**
- Problem statement: Học viên sắp nộp bài lab phải tự đối chiếu nhiều nguồn với nhiều file; một yêu cầu bị bỏ sót có thể làm mất điểm hoặc tốn một lượt nộp.
- Cách hiện tại: mở nhiều tab, tự lập checklist hoặc nhờ bạn rà; cách này vẫn được dùng vì con người hiểu ngữ cảnh tốt nhưng dễ bỏ sót và tốn thời gian.
- Evidence khảo sát Google Forms do team cung cấp ngày 31/07/2026: **n = 50** cho câu hỏi “Bạn đã từng gặp vấn đề nào khi nộp bài trên VLearn Codelabs?”.
  - Quên nộp một hoặc nhiều file: **38/50 (76%)**.
  - Thiếu nội dung được yêu cầu: **35/50 (70%)**.
  - Không biết bài đã đáp ứng đầy đủ yêu cầu chưa: **33/50 (66%)**.
  - Nộp sai đường dẫn GitHub: **31/50 (62%)**.
  - Các file trong bài không nhất quán: **29/50 (58%)**.
  - “Tùy chọn 3”: **28/50 (56%)**; nhãn chưa có ý nghĩa nên không dùng để ra quyết định.
  - Evidence không chứng minh được yêu cầu: **27/50 (54%)**.
  - “Chưa từng gặp vấn đề”: **26/50 (52%)**.
- Giới hạn evidence: đây là câu hỏi nhiều lựa chọn và có lựa chọn mâu thuẫn; ảnh tổng hợp không có dữ liệu từng người, thời gian hay quote. Vì vậy chưa thể tính “% xác nhận pain” theo rule khóa trong `validation/evidence-survey.md`.
- ≥5 quote có tên/vai: **Chưa có raw survey log để xác minh.**
- Evidence kỹ thuật không thay thế evidence pain: repo có 8 loại requirement mẫu thuộc artifact, implementation, report và security; golden set hiện có 24 case synthetic và 14 case từ team tự dùng thử.

## §2. Impact & quyết định chọn

| Ứng viên | Bao nhiêu người gặp | Tần suất | Tốn mỗi lần | Khả thi trong hackathon | Quyết định |
|---|---:|---:|---:|---|---|
| Khảo sát người dùng | 38/50 quên file; 35/50 thiếu nội dung; 33/50 không chắc đã đủ yêu cầu | Chưa đo | Chưa đo | Có: chỉ đọc repo | Chọn |
| Tóm tắt bài giảng thành flashcard | Chưa đo | Chưa đo | Chưa đo | Có | Loại: ngoài lát cắt pre-submission |

- Ứng viên chọn: LabGuard. Một pain trực tiếp đã vượt ngưỡng 50%: **38/50 (76%)** người trả lời chọn “quên nộp một hoặc nhiều file”.
- Lý do thiết kế hiện tại: một flow 5 phút, không cần quyền ghi repo, phần checker xác định kiểm lại được.

## §3. Giải pháp tương tự đã nghiên cứu

| Sản phẩm | Flow | Đáng học | Đáng né | LabGuard khác gì |
|---|---|---|---|---|
| GitHub Actions | Chạy check theo commit | Bằng chứng gắn file | Cần cấu hình trước | Rà repo public không cần cài vào repo |
| Checklist thủ công | Người đọc và tích mục | Dễ hiểu, kiểm soát cao | Dễ bỏ sót giữa nhiều nguồn | Gom nguồn thành requirement pack rồi chỉ ra rủi ro cao nhất |
| LLM chat chung | Dán yêu cầu và hỏi | Hiểu ngôn ngữ tự nhiên | Có thể nói đạt mà không dẫn chứng | Deterministic checker cho mục kiểm được; semantic item cho phép Human review |

## §4. Thiết kế

- Lát cắt MỘT CÂU: **Một học viên sắp nộp bài lab cung cấp nội dung đề và URL repo để hệ thống tạo requirement liên quan, kiểm tra bằng chứng trong repo và trả về thiếu sót ưu tiên cao nhất để học viên tự quyết định sửa.**
- Non-goals:
  1. Không chạy code không tin cậy từ repo học viên.
  2. Không sửa, commit hoặc nộp bài thay học viên.
  3. Không thay thế quyết định của TA.
  4. Chỉ tự động hóa requirement ánh xạ được vào tập checker an toàn của prototype.
- Mức prototype: **Mock**. Thật: provider được chọn qua `AI_PROVIDER/AI_MODEL` tạo pack động từ Codelab cùng README/docs của repo đề bài; GitHub API đọc repo bài làm, checker kiểm tra và xếp hạng. Hỗ trợ OpenAI, Google AI, OpenRouter và Ollama. Mock: Lab 03 mẫu có pack dự phòng; demo offline dùng repo giả. Upload chỉ nhận `.md/.txt`.
- Automation: **Conditional**. Mục deterministic được tự kiểm; mục semantic hoặc AI không chắc chuyển `needs_review`. Sai có thể làm học viên tin nhầm và mất điểm, nên hệ thống không sửa/nộp tự động và luôn hiện bằng chứng.

### §4b. Nguyên tắc HAX/PAIR

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| G1 — rõ khả năng | Màn đầu và footer nói rõ: đọc/rà, không chạy, sửa hoặc nộp |
| G2 — rõ độ tin cậy | Mỗi finding có status, confidence và file bằng chứng |
| G10 — thu hẹp khi nghi ngờ | Checker semantic trả `needs_review`; AI lỗi ở bài chưa biết thì dừng thay vì dùng sai rubric |
| G11 — giải thích vì sao | Risk card hiện yêu cầu, file, chi tiết phát hiện và impact |
| G9 — sửa dễ | User mở file GitHub, push commit rồi bấm “Kiểm tra lại” |
| PAIR Feedback + Control | Checkbox cho phép bỏ requirement; “AI đánh giá sai” chuyển finding sang Human review |

## §5. Kiểu lỗi — 4 lớp chỗ khó

| # | Tình huống | Lớp | Hành vi mong muốn | Nguyên tắc |
|---|---|---|---|---|
| 1 | AI không trích được requirement từ text | ① nguồn sự thật | Lab 03 mẫu dùng pack dự phòng; bài khác dừng với lỗi rõ ràng | G10 |
| 2 | Requirement chỉ có trong GitHub rubric | ① | Luôn hợp nhất mọi requirement có nguồn GitHub | G10, G11 |
| 3 | Không tìm thấy function `baseline` | ② mơ hồ | `needs_review`, không kết luận pass | G2, G10 |
| 4 | File Python lỗi cú pháp | ② | `needs_review` và chỉ đúng file | G10, G11 |
| 5 | User yêu cầu LabGuard sửa/nộp bài | ③ ngoài thẩm quyền | Từ chối; đưa hành động thủ công | G1, PAIR Control |
| 6 | Repo private hoặc URL không phải GitHub | ③ | Validation 422; hướng dẫn dùng repo public/demo | G1, G10 |
| 7 | Comment chứa “Action/Observation” nhưng không có loop | ④ domain | Không tính là ReAct động | G2, G11 |
| 8 | Secret nằm trong Markdown thay vì `.env` | ④ | Fail critical và yêu cầu revoke/xóa history | G2, G11 |
| 9 | GitHub rate-limit hoặc mất mạng khi demo | ① | Báo lỗi rõ; dùng demo offline làm fallback | G10 |
| 10 | User bỏ một requirement critical | ③ | Cho phép kiểm soát nhưng vẫn hiển thị severity trước khi xác nhận | PAIR Control |

## §6. Bốn đường đi của trải nghiệm

- Happy path: dán đề → AI thật chọn requirement → xác nhận → nhập repo → xem finding và hành động.
- Low-confidence: AST không xác định được semantic item → `needs_review`, học viên mở file và hỏi TA.
- Failure/không căn cứ: AI/GitHub lỗi → nhãn fallback hoặc lỗi rõ; chỉ Lab 03 mẫu dùng pack dự phòng, không giả là AI thật.
- Correction: học viên bấm “AI đánh giá sai”, finding chuyển Human review; sửa repo rồi rerun.
- Ngoài phạm vi: không nhận repo private/URL khác GitHub; không chạy hoặc sửa code.
- Domain: secret và dynamic ReAct là critical; comment/keyword đơn lẻ không được tính là implementation.

## §7. Kiểm thử

### Định nghĩa kiểm chứng được

| Chiều | Pass khi |
|---|---|
| Detection correctness | `actual status == expected status` cho từng case |
| Graceful uncertainty | Input thiếu function hoặc lỗi cú pháp trả `needs_review`, không `pass` |
| Safety | Mọi case secret trong golden set bị `fail` và repo sạch được `pass` |
| Traceability | Finding có requirement id, artifact và chi tiết kiểm tra |

- Golden set: `eval/golden-set.json`, 38 case: 24 synthetic và 14 case từ team tự dùng thử sản phẩm.
- Provenance: 14 case `O01`–`O14` từ phiên self-test ngày 2026-07-31. Chúng không thay thế yêu cầu rubric “≥10 case từ chatlog thật”; mục này chưa đạt vì workspace không có data pack.
- Quality bar đã khóa: **≥85% toàn bộ và 100% các case secret critical**.

| Lượt | Kết quả | So với bar | Failure |
|---|---:|---|---|
| Run 01 | 23/24 = 95,8% | Đạt tổng; secret đạt 100% | R04: comment có keyword bị hiểu là loop |
| Run 02 | 24/24 = 100% | Đạt | Sửa checker yêu cầu assignment và registry lookup thật |
| Run 03 | 38/38 = 100% | Đạt | Thêm 14 case từ phiên self-test |

Kết quả đầy đủ nằm tại `eval/run-01.json`, `eval/run-02.json` và `eval/run-03.json`. Con số này đo checker trên bộ synthetic/self-test, không phải bằng chứng product-market fit.

## §8. Phân công & kế hoạch

| Thành viên | Phân công |
|---|---|
| Phan Trọng Đạt | Product owner, spec và impact |
| Bùi Thu Trang | Evidence survey và validation log |
| Phạm Quốc Minh | Golden set, quality bar và phân tích eval |
| Nguyễn Thanh Hùng | Backend, AI call và GitHub checker |
| Phạm Danh Tuấn Dũng | Frontend, demo path và fallback |
| Đinh Việt Anh | Secret/data audit, slides và dry run |

- Willing users: **Chưa có tên người thật ngoài nhóm được xác minh.**
- Validation CP5: **Chưa thực hiện với người thật.**
- Multi-prototype: so hai phương án “AI tự kết luận” và “checker + Human review”; chọn phương án hai vì cost-of-error của false pass cao.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| CP2 | Chốt flow 4 bước, không chạy/sửa repo | Giữ lát cắt demo được |
| CP3 | Thêm AI extraction có nhãn mode và fallback | Pack tĩnh không đạt AI-call thật |
| CP3 | Checker ReAct yêu cầu assignment + registry lookup | Eval R04 phát hiện false positive từ comment |
| Survey | Ghi nhận biểu đồ tổng hợp 50 phản hồi | 76% chọn quên file; 70% chọn thiếu nội dung; 66% không chắc bài đã đủ |
| Dry run | Chuẩn hóa lỗi khi API trả response rỗng | D02 từng hiện lỗi `JSON.parse` thay vì thông báo hữu ích |
| Dry run | Loại checker arguments do AI tạo nhưng không hợp lệ | D04 từng tạo finding “Không tìm thấy ==” |
| CP5 | Chưa có thay đổi từ feedback người thật | V01–V05 chưa được thực hiện |
