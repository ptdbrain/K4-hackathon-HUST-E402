# Reflection — Nguyễn Thanh Hùng · 2A202601808

- Vai trò: Backend, AI provider và GitHub checker.
- Phần mang tên tôi: structured extraction cho OpenAI/Google/OpenRouter/Ollama, validation Pydantic, GitHub reader, AST/regex checker và fallback có nhãn.
- AI hỗ trợ: viết bản nháp code và test; tôi phải giải thích được trust boundary, giới hạn file, timeout, schema validation và lý do không chạy code trong repo.
- Nội dung trọng tâm: trace thật dùng Ollama `qwen2.5:7b-instruct-q3_K_S`; provider lỗi thì Lab 03 mới dùng pack dự phòng, bài khác dừng để tránh kiểm sai rubric.
- Bài học từ R04: regex tìm `Action/Observation` không đủ; checker phải yêu cầu assignment, registry lookup và Observation động.
- Lần sau tôi sẽ đo latency provider sớm hơn và chuẩn bị model nhỏ/fallback vì dry run ghi nhận bước extraction gần chạm timeout 90 giây.
