# Prototype validation

Validation người thật chưa được thực hiện. Không có tên/vai, quan sát hoặc quote để ghi nhận.

## Dry run kỹ thuật — 31/07/2026

| ID | Cách kiểm tra | Quan sát | Xử lý |
|---|---|---|---|
| D01 | Playwright, flow Codelab mẫu → AI extraction → xác nhận → repo demo | Flow đi hết 4 bước và hiện `NOT READY`; AI thật được gắn nhãn `OLLAMA · qwen2.5:7b-instruct-q3_K_S` | Giữ đường demo repo offline |
| D02 | Tắt backend khi frontend đang chạy | UI từng hiện lỗi kỹ thuật `JSON.parse: unexpected end of data` | `request()` nay chuyển lỗi response rỗng thành “Không thể xử lý yêu cầu.” |
| D03 | Đo bước AI extraction | Provider mất gần 90 giây mới trả kết quả | Giữ timeout/fallback; dùng trace đã lưu nếu provider không ổn định khi demo |
| D04 | Kiểm tra requirement do AI tạo | AI từng trả `python_symbol` với symbol `==`, dẫn tới finding vô nghĩa | Pydantic nay loại checker arguments không hợp lệ trước khi phân tích repo |

Các dòng D01–D04 là kiểm tra kỹ thuật, không phải validation người thật.
