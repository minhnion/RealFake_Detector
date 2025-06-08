# Dockerfile

# Giai đoạn 1: Sử dụng một base image nhẹ nhàng
FROM python:3.11-slim-buster

# Đặt thư mục làm việc bên trong container
WORKDIR /app

# Copy file requirements trước để tận dụng caching của Docker
# Nếu file này không thay đổi, layer này sẽ không cần build lại
COPY requirements.txt .

# Cài đặt các thư viện
# --no-cache-dir giúp giảm kích thước image
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ thư mục dự án vào container
COPY . .

# Gunicorn sẽ lắng nghe trên port này. Render sẽ tự động map nó.
EXPOSE 10000 

# Lệnh để chạy ứng dụng khi container khởi động
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--chdir", "api", "main:app", "--bind", "0.0.0.0:10000"]