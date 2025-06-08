# 🤖 Deepfake Detector API

Đây là backend API cho ứng dụng phát hiện hình ảnh deepfake, được xây dựng bằng **FastAPI** và **PyTorch**.

---

## 🔗 Liên kết quan trọng

- 🌐 **API Demo:** [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- 📄 **Tài liệu Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
> ⚠️ *Lưu ý: Dịch vụ miễn phí có thể mất 30-60 giây để khởi động trong lần truy cập đầu tiên.*

---

## 🚀 Cài đặt & Chạy tại Local

### 🧩 Yêu cầu hệ thống

- Python 3.10 hoặc 3.11  
- Docker Desktop *(khuyến nghị cho môi trường giống production)*  
- Tài khoản MongoDB Atlas  
- Tài khoản Cloudinary  

---

### ⚙️ Các bước thực hiện

```bash
# 1. Clone project
git clone https://github.com/minhnion/RealFake_Detector.git
cd RealFake_Detector

# 2. Tạo và kích hoạt môi trường ảo
python -m venv venv
# Trên Windows:
.\venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate

# 3. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 4. Chạy ứng dụng (chọn 1 trong 2 cách bên dưới)

# 👉 Cách 1: Chạy bằng Uvicorn (phục vụ phát triển)
uvicorn api.main:app --reload
# API chạy tại: http://127.0.0.1:8000

# 👉 Cách 2: Dùng Docker (mô phỏng production)
docker build -t realfake-detector .
docker run -d -p 8000:10000 --env-file api/.env --name realfake-container realfake-detector
# API chạy tại: http://127.0.0.1:8000
