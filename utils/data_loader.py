import streamlit as st
import pandas as pd
import os

# Xác định đường dẫn tương đối đến thư mục data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Lấy thư mục gốc của dự án
DATA_DIR = os.path.join(BASE_DIR, 'data')

@st.cache_data # Sử dụng cache để tăng tốc độ tải lại
def load_data(file_name="train_and_val.csv"):
    """Loads data from the data directory."""
    file_path = os.path.join(DATA_DIR, file_name)
    try:
        with st.spinner(f"📥 Loading {file_name}... Please wait!"):
            if file_name.endswith('.csv'):
                return pd.read_csv(file_path)
            elif file_name.endswith('.xlsx'):
                 # Cần cài đặt openpyxl: pip install openpyxl
                return pd.read_excel(file_path)
            else:
                st.error(f"Unsupported file format: {file_name}")
                return None
    except FileNotFoundError:
        st.error(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading {file_name}: {e}")
        return None

# Thêm các hàm load dữ liệu khác nếu cần (ví dụ load X_train, y_train...)
@st.cache_data
def load_split_data():
    """Loads pre-split training and testing data."""
    try:
        X_train = pd.read_csv(os.path.join(DATA_DIR, 'X_train.csv')) # Giả sử có file này
        y_train = pd.read_csv(os.path.join(DATA_DIR, 'y_train.csv')) # Giả sử có file này
        X_test = pd.read_csv(os.path.join(DATA_DIR, 'X_test.csv'))   # Giả sử có file này
        y_test = pd.read_csv(os.path.join(DATA_DIR, 'y_test.csv'))   # Giả sử có file này
        # Lưu ý: y thường là Series, cần điều chỉnh nếu file csv chỉ có 1 cột
        y_train = y_train.iloc[:, 0] # Lấy cột đầu tiên làm Series
        y_test = y_test.iloc[:, 0]   # Lấy cột đầu tiên làm Series
        return X_train, X_test, y_train, y_test
    except FileNotFoundError as e:
        st.error(f"Error loading split data: {e}. Please ensure pre-split files exist.")
        return None, None, None, None
    except Exception as e:
        st.error(f"An error occurred loading split data: {e}")
        return None, None, None, None