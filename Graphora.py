import streamlit as st
from PIL import Image  # Import thư viện Pillow
import os             # Import thư viện os để xử lý đường dẫn file

# Xác định đường dẫn tuyệt đối đến file ảnh
# Giả sử app.py nằm ở thư mục gốc của dự án (data_pipeline_project/)
# và ảnh nằm trong data_pipeline_project/assets/graphora.png
try:
    # Lấy thư mục hiện tại của file app.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Đường dẫn đến file ảnh
    icon_path = os.path.join(current_dir, "assets", "graphora.png")
    # Tải ảnh bằng Pillow
    page_icon_image = Image.open(icon_path)
except FileNotFoundError:
    st.warning("Icon file 'assets/graphora.png' not found. Using default icon.")
    page_icon_image = "📊" # Icon mặc định nếu không tìm thấy file
except Exception as e:
    st.error(f"Error loading icon: {e}")
    page_icon_image = "📊" # Icon mặc định nếu có lỗi khác


# Cấu hình trang chính với icon là ảnh đã tải
st.set_page_config(
    page_title="Graphora",
    page_icon=page_icon_image, # Sử dụng đối tượng Image đã tải
    layout="wide"
)

# CSS tùy chỉnh (giữ nguyên)
st.markdown("""
    <style>
        /* ... CSS styles ... */
    </style>
""", unsafe_allow_html=True)

# --- Phần điều hướng và if/elif đã được loại bỏ ---

# Hiển thị logo trong sidebar (giữ nguyên)
try:
    sidebar_logo_path = os.path.join(current_dir, "assets", "graphora.png")
    sidebar_logo = Image.open(sidebar_logo_path)
    st.sidebar.image(sidebar_logo, width=500)
except FileNotFoundError:
    st.sidebar.warning("Sidebar logo 'assets/rice_owl_logo.png' not found.")
except Exception as e:
    st.sidebar.error(f"Error loading sidebar logo: {e}")

st.sidebar.success("Select a step from above.")

st.title("Welcome to the Graphora!")
st.write("""
Navigate through the different stages of the data preprocessing and visualization dashboard using the sidebar.
Each page represents a distinct step:
1.  **Data Wrangling:** Cleaning and preparing the raw data.
2.  **EDA:** Exploratory Data Analysis to understand patterns.
3.  **Dashboard:** Data Visualization using Interactive Dashboard.
4.  **AI Assistant:** Ask questions about your data.
""")