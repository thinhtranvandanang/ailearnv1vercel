# Hướng Dẫn Triển Khai EduNexia Lên Vercel

Hướng dẫn này sẽ giúp bạn triển khai ứng dụng EduNexia (Frontend React + Backend FastAPI) lên nền tảng đám mây Vercel.

## Tổng Quan Kiến Trúc Triển Khai

Việc triển khai lên Vercel bao gồm 3 phần chính cần được cấu hình:

1.  **Frontend (React)**: Được Vercel build tự động và phục vụ như một Static Site. Vercel sẽ đảm nhận việc routing cho Single Page Application (SPA).
2.  **Backend (FastAPI)**: Được chuyển đổi thành **Serverless Functions**. Thay vì chạy một server liên tục (như `uvicorn` trên VPS), Vercel sẽ khởi động function khi có request đến API.
3.  **Cơ Sở Dữ Liệu (PostgreSQL)**: Vercel không lưu trữ database trực tiếp. Bạn cần sử dụng dịch vụ database bên ngoài (Vercel Postgres, Supabase, Neon, v.v.) và kết nối qua biến môi trường.

## Các File Cấu Hình Quan Trọng

- `vercel.json`: Điều hướng request. Request bắt đầu bằng `/api/` sẽ vào Serverless Function, các request khác sẽ vào Frontend.
- `api/index.py`: Điểm nhập (entry point) cho Vercel biết cách khởi chạy Backend.
- `requirements.txt`: Danh sách thư viện Python cần thiết cho Serverless Function.

## Quy Trình Triển Khai Chi Tiết

### Bước 1: Chuẩn Bị Code (Đã Thực Hiện)
Chúng ta đã tạo các file cần thiết:
- `vercel.json` đã được cấu hình rewrite.
- `api/index.py` đã được tạo để expose `app`.

### Bước 2: Đẩy Code Lên GitHub
Đảm bảo code mới nhất của bạn đã được push lên repository GitHub của bạn.

### Bước 3: Tạo Project Trên Vercel
1.  Truy cập [Vercel Dashboard](https://vercel.com/dashboard) và đăng nhập.
2.  Nhấn **"Add New..."** -> **"Project"**.
3.  Chọn repository **EduNexia** từ GitHub của bạn và nhấn **Import**.

### Bước 4: Cấu Hình Project
Trong màn hình "Configure Project":
1.  **Framework Preset**: Chọn **Vite**.
2.  **Root Directory**: Để mặc định `./` (nếu code nằm ngay thư mục gốc).
3.  **Build Command**: `vite build` (Mặc định).
4.  **Output Directory**: `dist` (Mặc định).
5.  **Environment Variables**: Khai báo các biến môi trường sau:

    | Tên Biến | Giá Trị Ví Dụ / Mô Tả |
    | :--- | :--- |
    | `DATABASE_URL` | `postgresql://user:pass@host:5432/db` (Lấy từ nhà cung cấp DB) |
    | `SECRET_KEY` | Chuỗi bí mật ngẫu nhiên (Xem cách tạo bên dưới) |
    | `ALGORITHM` | `HS256` (Thuật toán mã hóa JWT) |
    | `GEMINI_API_KEY` | API Key của Gemini AI |
    | `ENVIRONMENT` | `production` |
    | `BACKEND_CORS_ORIGINS` | `https://your-project-name.vercel.app` |

### Cách tạo `SECRET_KEY` bảo mật
Bạn nên sử dụng một chuỗi ngẫu nhiên dài và phức tạp. Có 2 cách đơn giản để tạo:

**Cách 1: Dùng Python (Khuyên dùng)**
Chạy lệnh này trong terminal của bạn:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Nó sẽ in ra một chuỗi như `_u5Y8Xp9jR...`. Hãy copy chuỗi đó làm `SECRET_KEY`.

**Cách 2: Dùng OpenSSL (Nếu có cài đặt)**
```bash
openssl rand -hex 32
```

### Tại sao dùng `HS256`?
`HS256` (HMAC with SHA-256) là thuật toán tiêu chuẩn và phổ biến nhất cho JWT. Nó sử dụng một khóa bí mật duy nhất (`SECRET_KEY`) để cả ký và xác thực token. Đây là cấu hình mặc định trong code Backend của bạn.

> [!IMPORTANT]
> **Lưu ý về Database**: Bạn có thể tạo **Vercel Postgres** ngay trong tab **Storage** của project Vercel và nó sẽ tự động điền `DATABASE_URL` cho bạn.

### Bước 5: Deploy
Nhấn nút **Deploy**. Vercel sẽ tiến hành build frontend và cài đặt dependencies cho backend.
Quá trình này mất khoảng 2-5 phút.

### Bước 6: Kiểm Tra
Sau khi deploy thành công:
1.  Truy cập URL project (vd: `https://edunexia.vercel.app`).
2.  Kiểm tra trang chủ có load không.
3.  Kiểm tra gọi API (ví dụ: đăng nhập) xem có hoạt động không.

---

## Xử Lý Sự Cố Thường Gặp

**Lỗi 404 trên các trang con khi reload**:
- Nguyên nhân: Routing SPA chưa đúng.
- Giải pháp: Kiểm tra `vercel.json`, đảm bảo có rewrite `source: "/(.*)"` về `/index.html`.

**Lỗi 500 khi gọi API**:
- Nguyên nhân: Lỗi code Backend hoặc kết nối Database.
- Giải pháp: Vào tab **Logs** trên Vercel, chọn Filter là **Functions** để xem chi tiết lỗi Python.

**Lỗi "Module not found" ở Backend**:
- Nguyên nhân: Thiếu thư viện trong `requirements.txt`.
- Giải pháp: Bổ sung tên thư viện vào file và push lại code.
