import os
from dotenv import load_dotenv # Cần cài đặt: pip install python-dotenv

load_dotenv() # Tải biến môi trường từ file .env (nếu có)

# Lấy API key từ biến môi trường hoặc đặt trực tiếp (không khuyến khích)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAMNpfuhJfwFw3lFv-L") # Thay YOUR_API_KEY_HERE nếu không dùng .env

# Thêm các cấu hình khác nếu cần
# DATA_FILE_PATH = "data/train_and_val.csv"