# 📊 Graphora

**CSC180108 - Đồ án cuối kỳ môn Trực quan hóa dữ liệu**

## 📜 Giới thiệu

**Graphora** là một nền tảng trực quan hóa dữ liệu giáo dục được thiết kế nhằm phục vụ cho mục tiêu **phân tích và đánh giá toàn diện tình hình giáo dục tại Việt Nam**. Hệ thống này là đồ án cuối kỳ cho môn học CSC180108 - Trực quan hóa dữ liệu.

Ứng dụng cho phép người dùng khám phá, tương tác và rút ra những hiểu biết sâu sắc từ dữ liệu giáo dục qua các năm, cấp học và địa phương khác nhau, được xây dựng bằng Streamlit và các công cụ Python hiện đại.

## 💾 Nguồn dữ liệu

Hệ thống chủ yếu sử dụng dữ liệu công khai từ **[Tổng cục Thống kê Việt Nam (GSO)](https://www.gso.gov.vn/giao-duc/)**. Dữ liệu được lưu trữ trong thư mục `data/` và/hoặc `data_1/` của dự án. *(Lưu ý: Cần làm rõ vai trò của từng thư mục data nếu cần thiết)*.

## ✨ Tính năng chính

Graphora cung cấp các phân hệ chức năng chính sau (truy cập qua sidebar):

* **🔍 Data Wrangling**: Tải lên, làm sạch, xử lý và chuẩn hóa dữ liệu đầu vào.
* **📊 EDA (Exploratory Data Analysis)**: Khám phá dữ liệu qua thống kê mô tả và các biểu đồ phân phối cơ bản.
* **📈 Dashboard**: Các dashboard tương tác tổng quan và chi tiết theo từng cấp học (Mẫu giáo, Tiểu học, THCS, THPT).
* **🤖 AI Assistant**: Trợ lý AI thông minh cho phép hỏi đáp về dữ liệu bằng ngôn ngữ tự nhiên, tích hợp các công cụ trực quan hóa nhanh.

## 🛠️ Công nghệ sử dụng

* **Ngôn ngữ:** Python (Phiên bản được chỉ định trong `.python-version`, nên sử dụng `pyenv` để quản lý)
* **Framework Web/Dashboard:** Streamlit
* **Xử lý dữ liệu:** Pandas
* **Trực quan hóa:** Plotly Express
* **AI Integration:** Google Gemini API (`google-generativeai`)
* **Quản lý Môi trường & Gói:** UV (dựa trên sự hiện diện của `pyproject.toml` và `uv.lock`)
* **Deployment:** Docker, Fly.io (dựa trên `Dockerfile` và `fly.toml`)
* **Quản lý Biến môi trường:** `python-dotenv`

## 📁 Cấu trúc Thư Mục Dự Án

```plaintext
graphora/
├── Home.py                  # Trang chính (entry point) của ứng dụng Streamlit
│
├── pages/                   # Các trang con (tự động hiển thị trong thanh điều hướng Streamlit)
│   ├── 1_Data_Wrangling.py
│   ├── 2_EDA.py
│   ├── 3_Dashboard.py
│   └── 4_AI_Assistant.py
│
├── data/                    # Dữ liệu nguồn chính
├── data_1/                  # Dữ liệu bổ sung 
│
├── .streamlit/              # Cấu hình giao diện và menu cho Streamlit
├── .github/                 # Cấu hình CI/CD với GitHub Actions
│
├── Dockerfile               # Cấu hình Docker để build ứng dụng
├── fly.toml                 # Cấu hình deployment với Fly.io
├── pyproject.toml           # Định nghĩa metadata dự án và dependencies (UV/Poetry)
├── uv.lock                  # File lock dependencies tạo bởi UV
│
├── .env                     # Biến môi trường (ví dụ: API keys) – không commit lên Git
├── .gitignore               # Định nghĩa các file/folder cần bỏ qua trong Git
├── .dockerignore            # Định nghĩa các file/folder cần bỏ qua khi build Docker
├── .python-version          # Chỉ định phiên bản Python (cho pyenv)
└── README.md                # Mô tả tổng quan dự án
```

## ⚙️ Cài đặt và Chạy dự án

1.  **Clone repository:**
    ```bash
    git clone <your-repository-url>
    cd graphora
    ```
2.  **Cài đặt phiên bản Python yêu cầu:**
    * Đảm bảo bạn đã cài đặt `pyenv` (nếu chưa có).
    * Sử dụng `pyenv` để cài đặt phiên bản Python được chỉ định trong file `.python-version`.
    * Thiết lập phiên bản local: `pyenv local <version_from_.python-version_file>`
3.  **Cài đặt UV (nếu chưa có):** Tham khảo tài liệu cài đặt `uv` tại [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv). Ví dụ:
    ```bash
    # macOS / Linux
    curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
    # Windows
    irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex
    ```
4.  **(Khuyến nghị) Tạo môi trường ảo với UV:**
    ```bash
    # Tạo môi trường ảo tên .venv (uv sẽ tự động nhận diện)
    uv venv
    # Kích hoạt môi trường ảo
    # Windows (Command Prompt)
    .venv\Scripts\activate.bat
    # Windows (PowerShell)
    .venv\Scripts\Activate.ps1
    # macOS/Linux
    source .venv/bin/activate
    ```
5.  **Cài đặt các thư viện từ `pyproject.toml` bằng UV:**
    ```bash
    uv sync
    ```
    *(Lệnh này sẽ cài đặt chính xác các dependencies được định nghĩa trong `pyproject.toml` và `uv.lock`)*
6.  **Tạo file `.env`:**
    * Tạo file `.env` trong thư mục gốc.
    * Thêm các biến môi trường cần thiết, ví dụ:
        ```
        GEMINI_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
        ```
    * Đảm bảo file `.env` đã được thêm vào `.gitignore`.
7.  **Chuẩn bị dữ liệu:** Đặt các file dữ liệu vào thư mục `data/` hoặc `data_1/` theo cấu trúc dự án.
8.  **Chạy ứng dụng Streamlit:**
    ```bash
    streamlit run Home.py
    ```
9.  Mở trình duyệt và truy cập vào địa chỉ được cung cấp (thường là `http://localhost:8501`).

## 👥 Nhóm thực hiện

* **Nhóm 13 - Lớp 22KHDL1**
* Học kỳ 2, Năm học 2024–2025

## 🎓 Thông tin môn học

* **Môn học:** Trực quan hóa dữ liệu (CSC180108)
* **Trường:** Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM

## ©️ Bản quyền (Copyright)

Copyright (c) 2025 Group 13 - 22KHDL1. All Rights Reserved.

Mã nguồn này được cung cấp cho mục đích đánh giá trong khuôn khổ đồ án môn học. Mọi quyền được bảo lưu. Việc sao chép, phân phối, sửa đổi hoặc sử dụng mã nguồn này cho bất kỳ mục đích nào khác mà không có sự cho phép rõ ràng bằng văn bản từ nhóm tác giả đều bị nghiêm cấm.