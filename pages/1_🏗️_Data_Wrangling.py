import streamlit as st
import pandas as pd
from utils.data_loader import load_data # Import hàm load_data

st.set_page_config(page_title="Data Wrangling", layout="wide") # Cấu hình riêng cho trang này

st.title("🏗️ Data Wrangling")

# Tải dữ liệu bằng hàm đã import
# data = load_data("train_and_val.csv") # File gốc để xử lý
# raw_display_data = load_data("training.xlsx") # File khác để hiển thị raw

# --- BẮT ĐẦU CODE CỦA PHẦN data_wrangling TỪ FILE GỐC ---

# Ví dụ: giả sử file chính là 'train_and_val.csv'
data = load_data("train_and_val.csv")

if data is not None:
    st.write("Performing data wrangling steps...")

    # Drop Unnecessary Columns
    if "Region" in data.columns:
        data_processed = data.drop(columns=["Region"]) # Tạo bản copy để xử lý
    else:
        data_processed = data.copy()

    # Handle Missing Values
    if 'Model Year' in data_processed.columns:
        median_year = data_processed['Model Year'].median()
        data_processed['Model Year'].fillna(median_year, inplace=True)
        # Chỉ chuyển sang int nếu không có NaN sau khi fill
        if not data_processed['Model Year'].isnull().any():
             data_processed['Model Year'] = data_processed['Model Year'].astype(int)
        else:
             st.warning("Could not convert 'Model Year' to int due to remaining NaNs.")
    else:
        st.warning("'Model Year' column not found.")

    # Convert 'GVWR Class' to Numeric
    if "GVWR Class" in data_processed.columns:
        data_processed["GVWR Class"] = data_processed["GVWR Class"].replace({"Not Applicable": -1, "Unknown": -1})
        # Chuyển đổi an toàn hơn
        data_processed["GVWR Class"] = pd.to_numeric(data_processed["GVWR Class"], errors='coerce')
        # Có thể fillna sau khi coerce nếu cần
        # data_processed["GVWR Class"].fillna(-1, inplace=True) # Ví dụ fill NaN còn lại
    else:
        st.warning("'GVWR Class' column not found.")


    # One-Hot Encoding & Ordinal Encoding
    if "Number of Vehicles Registered at the Same Address" in data_processed.columns:
        ordinal_mapping = {'1': 1, '2': 2, '3': 3, '≥4': 4, 'Unknown': -1}
        data_processed["Number of Vehicles Registered at the Same Address"] = data_processed["Number of Vehicles Registered at the Same Address"].map(ordinal_mapping)
         # Fillna cho các giá trị không có trong mapping
        # data_processed["Number of Vehicles Registered at the Same Address"].fillna(-1, inplace=True)
    else:
        st.warning("'Number of Vehicles Registered...' column not found.")

    # Xác định các cột để one-hot encode một cách an toàn
    cols_to_encode = ["Vehicle Category", "Fuel Type", "Fuel Technology", "Electric Mile Range"]
    existing_cols_to_encode = [col for col in cols_to_encode if col in data_processed.columns]
    if existing_cols_to_encode:
         data_processed = pd.get_dummies(data_processed, columns=existing_cols_to_encode, dummy_na=True) # dummy_na=True để xử lý NaN nếu có
    else:
         st.warning("No columns found for One-Hot Encoding.")


    # Convert Date Column
    if "Date" in data_processed.columns and "Model Year" in data_processed.columns:
        # Xử lý NaN trong Date trước khi chuyển đổi
        median_date = data_processed['Date'].median() if pd.api.types.is_numeric_dtype(data_processed['Date']) else 2020 # Giả sử năm 2020 nếu không phải số
        data_processed['Date'].fillna(median_date, inplace=True)

        # Chuyển đổi sang datetime và xử lý lỗi
        data_processed['Date_temp'] = pd.to_datetime(data_processed['Date'], format='%Y', errors='coerce')
        valid_dates = data_processed['Date_temp'].notna()

        # Chỉ tính toán Vehicle Age nếu Date và Model Year hợp lệ
        if 'Model Year' in data_processed.columns and data_processed['Model Year'].notna().all():
            data_processed.loc[valid_dates, "Vehicle Age"] = data_processed.loc[valid_dates, 'Date_temp'].dt.year - data_processed.loc[valid_dates, "Model Year"]
            # Có thể fillna cho Vehicle Age nếu muốn
            # data_processed["Vehicle Age"].fillna(data_processed["Vehicle Age"].median(), inplace=True)
        else:
            st.warning("Cannot calculate 'Vehicle Age' due to issues in 'Date' or 'Model Year'.")
        data_processed.drop(columns=['Date_temp'], inplace=True) # Xóa cột tạm

    else:
         st.warning("Missing 'Date' or 'Model Year' for 'Vehicle Age' calculation.")

    # --- Các bước hiển thị giải thích code ---
    st.header("Step 1: Load and Display the Dataset")
    st.write("First, we load the dataset and display the first few rows to understand its structure.")
    code_step1 = """
import pandas as pd

# Load the dataset (adjust path as needed)
# data = pd.read_csv("data/train_and_val.csv")
# For display purposes, load the 'training.xlsx'
raw_display_data = pd.read_excel("data/training.xlsx")

# Display the first 5 rows
print(raw_display_data.head())
"""
    st.code(code_step1, language="python")
    st.write("**Explanation**: The dataset is loaded and the first 5 rows are displayed.")
    st.write("### 🔍 Raw Dataset Preview (from training.xlsx)")
    raw_display_data_loaded = load_data("training.xlsx")
    if raw_display_data_loaded is not None:
        st.dataframe(raw_display_data_loaded.head())
    else:
        st.warning("Could not load 'training.xlsx' for preview.")


    st.header("Step 2: Basic Information about the Dataset")
    # ... (code và giải thích tương tự như file gốc) ...
    code_step2 = """
# Assuming 'data' holds the loaded dataframe
print(f"Number of rows: {data.shape[0]}, Number of columns: {data.shape[1]}")
data.info()
print("\\nMissing values:")
print(data.isnull().sum())
"""
    st.code(code_step2, language="python")
    st.write("**Explanation**: Check shape, data types, and missing values.")

    st.header("Step 3: Handle Missing Values")
    # ... (code và giải thích tương tự như file gốc) ...
    code_step3 = """
# Fill missing 'Model Year' with median (example)
if 'Model Year' in data.columns:
    median_year = data['Model Year'].median()
    data['Model Year'].fillna(median_year, inplace=True)
    # Ensure type conversion happens after filling NaNs
    if not data['Model Year'].isnull().any():
        data['Model Year'] = data['Model Year'].astype(int)

# Fill missing 'GVWR Class' after handling specific strings (example)
if 'GVWR Class' in data.columns:
    data['GVWR Class'] = data['GVWR Class'].replace({"Not Applicable": -1, "Unknown": -1})
    data['GVWR Class'] = pd.to_numeric(data['GVWR Class'], errors='coerce')
    # data['GVWR Class'].fillna(-1, inplace=True) # Optional: fill NaNs created by coerce

# Fill missing categoricals with mode (example)
for col in data.select_dtypes(include=['object', 'category']).columns:
     if data[col].isnull().any():
          mode_val = data[col].mode()[0] # Calculate mode safely
          data[col].fillna(mode_val, inplace=True)
"""
    st.code(code_step3, language="python")
    st.write("**Explanation**: Fill missing numerical with median, categorical with mode.")


    st.header("Step 4: Convert Data Types")
    # ... (code và giải thích tương tự như file gốc) ...
    # Lưu ý: Việc chuyển đổi kiểu dữ liệu nên thực hiện trên data_processed
    code_step4 = """
# Convert 'Date' column (handled earlier with Vehicle Age calculation)
# Example: Convert other categoricals if needed after cleaning
categorical_columns_to_convert = [col for col in ['Vehicle Category', 'Fuel Type'] if col in data_processed.columns]
for col in categorical_columns_to_convert:
    data_processed[col] = data_processed[col].astype('category')
"""
    st.code(code_step4, language="python")
    st.write("**Explanation**: Convert relevant columns to appropriate types like 'category'.")

    st.header("Step 5: Remove Duplicates and Reset Index")
    # ... (code và giải thích tương tự như file gốc) ...
    code_step5 = """
# Perform on the processed dataframe
rows_before = data_processed.shape[0]
data_processed.drop_duplicates(inplace=True)
data_processed.reset_index(drop=True, inplace=True)
rows_after = data_processed.shape[0]
print(f"Removed {rows_before - rows_after} duplicate rows.")
"""
    st.code(code_step5, language="python")
    st.write("**Explanation**: Remove duplicate rows and reset the index.")


    # Hiển thị dữ liệu đã xử lý (tùy chọn)
    st.write("### ✨ Processed Data Preview")
    st.dataframe(data_processed.head())

    # Lưu dữ liệu đã xử lý để các trang khác sử dụng (QUAN TRỌNG)
    # Có thể lưu vào session state hoặc lưu ra file mới
    # Ví dụ lưu vào session state:
    # st.session_state['processed_data'] = data_processed
    # Ví dụ lưu ra file:
    # processed_file_path = os.path.join(DATA_DIR, 'processed_data.csv')
    # data_processed.to_csv(processed_file_path, index=False)
    # st.success(f"Processed data saved to {processed_file_path}")

else:
    st.error("Failed to load data for wrangling.")


# --- KẾT THÚC CODE CỦA PHẦN data_wrangling ---