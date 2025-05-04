import streamlit as st

# Thiết lập giao diện trang chủ
st.set_page_config(page_title="Graphora - Nền tảng trực quan hóa giáo dục", layout="wide")

# Tiêu đề
st.title("Welcome to Graphora!")
st.markdown("""
Graphora là một nền tảng trực quan hóa dữ liệu giáo dục được thiết kế nhằm phục vụ cho mục tiêu **phân tích và đánh giá toàn diện tình hình giáo dục tại Việt Nam**.

Hệ thống sử dụng dữ liệu từ [Tổng cục Thống kê Việt Nam](https://www.nso.gov.vn/giao-duc/) để cung cấp **cái nhìn tổng quan, chi tiết và so sánh** giữa các cấp học, giai đoạn và địa phương trên cả nước.
""")

# Tổng quan mục tiêu
st.subheader("📌 Mục tiêu chính của đồ án")
st.markdown("""
- Trực quan hóa dữ liệu giáo dục theo từng **cấp học**: Mẫu giáo, Tiểu học, THCS, THPT.
- Phân tích sự **phát triển theo thời gian** về số lượng trường học, lớp học, học sinh, giáo viên.
- **So sánh giữa các địa phương**, xác định khu vực có tốc độ phát triển nhanh hoặc cần cải thiện.
- Cung cấp **tương tác động**, cho phép người dùng tự chọn biến, lọc năm, tỉnh thành và tạo biểu đồ động.
- Hỗ trợ AI Assistant để **trả lời truy vấn dữ liệu bằng ngôn ngữ tự nhiên**.
""")

# Cấu trúc các trang chính
st.subheader("🗂️ Các phân hệ chính")
st.markdown("""
- 🔍 **Data Wrangling**: Xử lý dữ liệu đầu vào (.csv/.xlsx), lọc, đổi tên cột, và chuẩn hóa định dạng.
- 📊 **EDA (Exploratory Data Analysis)**: Khám phá dữ liệu thông qua biểu đồ phân bố, thống kê mô tả, kiểm tra phân phối.
- 📈 **Dashboard**:
    - Tổng quan: KPIs, biến động theo năm, tỷ lệ giới tính, heatmap phát triển.
    - Tiểu học |THCS |THPT |Mẫu giáo: Các dashboard theo từng cấp học với biểu đồ tương tác, bản đồ, scatter, treemap.
- 🤖 **AI Assistant**: Hỏi đáp dữ liệu thông minh với trợ lý AI, hỗ trợ truy vấn bằng tiếng Việt.

""")

# Gợi ý sử dụng
st.subheader("🚀 Bắt đầu ngay")
st.markdown("""
- Chọn một mục ở thanh bên trái để bắt đầu.
- Tải dữ liệu của bạn hoặc sử dụng dữ liệu mặc định từ dự án.
- Tùy chọn các biến phân tích theo nhu cầu.
""")

# Chữ ký
st.markdown("---")
st.markdown("📘 **Đồ án môn học: Trực quan hóa dữ liệu - Đại học Khoa học Tự nhiên thành phố Hồ Chí Minh**")
st.markdown("👨‍💻 Thực hiện bởi **Nhóm 13 - 22KHDL1, HK2, năm học 2024–2025**")
