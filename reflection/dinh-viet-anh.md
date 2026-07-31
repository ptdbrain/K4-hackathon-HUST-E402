# Reflection — Đinh Việt Anh · 2A202601516

- Vai trò: Secret/data audit, slide và dry run.
- Phần mang tên tôi: checker secret, quy tắc không commit `.env`/data pack, fallback demo và checklist trước push.
- AI hỗ trợ: rà pattern secret, build và browser flow; AI không được biến placeholder hoặc output tự tạo thành bằng chứng người thật.
- Nội dung trọng tâm: secret trong `.env`, source hoặc Markdown đều phải fail critical; tên biến `GOOGLE_API_KEY` không có giá trị không được báo nhầm.
- Bài học từ dry run: frontend và backend cần được khởi động độc lập, provider thật có thể chậm, và file slide phải được kiểm tra tồn tại thay vì tin mô tả trong README.
- Lần sau tôi sẽ chạy checklist artifact + secret scan + demo timer trước CP5; hiện `demo-slides.pdf` cần được khôi phục trong workspace.
