# Reflection — Phạm Quốc Minh · 2A202601494

- Vai trò: Golden set, quality bar và eval.
- Phần mang tên tôi: 38 case, quality bar ≥85% + 100% secret critical và ba bảng kết quả trong `eval/`.
- AI hỗ trợ: tạo scaffold case và runner Python stdlib; expected status, provenance và việc giữ nguyên quality bar cần người phụ trách kiểm lại.
- Nội dung trọng tâm: Run 01 đạt 23/24, Run 02 đạt 24/24 sau sửa R04, Run 03 đạt 38/38 sau thêm 14 self-test; 14 self-test không thay thế ≥10 case chatlog thật.
- Bài học từ R04: test regression phải giữ lại case comment chứa keyword, vì sửa bằng cách đếm từ khóa sẽ tái tạo false positive.
- Lần sau tôi sẽ lấy provenance thật trước khi mở rộng synthetic set và yêu cầu hai người chấm độc lập các case semantic.
