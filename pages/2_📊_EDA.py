import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.data_loader import load_data # Import hàm load_data
from sklearn.model_selection import train_test_split # Import nếu cần thực hiện split ở đây
import os # Để làm việc với đường dẫn file

st.set_page_config(page_title="Exploratory Data Analysis", layout="wide")

st.title("📊 Exploratory Data Analysis")

# Tải dữ liệu gốc để thực hiện EDA (hoặc tải dữ liệu đã xử lý nếu muốn)
# data = load_data("train_and_val.csv")
# Hoặc tải dữ liệu đã xử lý từ bước trước (nếu đã lưu)
# processed_file_path = os.path.join('data', 'processed_data.csv')
# if os.path.exists(processed_file_path):
#    data = pd.read_csv(processed_file_path)
# else:
#    st.warning("Processed data file not found. Loading raw data instead.")
#    data = load_data("train_and_val.csv")

# Giả sử EDA thực hiện trên dữ liệu gốc như trong code ban đầu
data = load_data("train_and_val.csv")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')


if data is not None:
    # --- BẮT ĐẦU CODE CỦA PHẦN eda TỪ FILE GỐC ---

    # Step 6: Feature Engineering (Tính toán lại Vehicle Age nếu cần cho EDA)
    st.header("Step 6: Feature Engineering")
    st.write("We create a new feature called 'Vehicle Age'.")
    code_step6 = """
# Create 'Vehicle Age' feature (ensure Date and Model Year exist and are clean)
if "Date" in data.columns and "Model Year" in data.columns:
    # Basic cleaning for calculation
    data["Date_temp"] = data["Date"].fillna(2020) # Handle missing dates
    data["Date_temp"] = pd.to_datetime(data["Date_temp"], format='%Y', errors='coerce').dt.year
    data["Model Year_temp"] = data["Model Year"].fillna(data["Model Year"].median())
    if not data["Model Year_temp"].isnull().any():
        data["Model Year_temp"] = data["Model Year_temp"].astype(int)

    # Calculate age where possible
    valid_age_calc = data['Date_temp'].notna() & data['Model Year_temp'].notna()
    data.loc[valid_age_calc, "Vehicle Age"] = data.loc[valid_age_calc, "Date_temp"] - data.loc[valid_age_calc, "Model Year_temp"]
    # Drop temporary columns
    # data.drop(columns=['Date_temp', 'Model Year_temp'], inplace=True)
else:
    print("Cannot create 'Vehicle Age': Missing 'Date' or 'Model Year'.")

print(data[['Date', 'Model Year', 'Vehicle Age']].head())
"""
    st.code(code_step6, language="python")
    st.write("**Explanation**: The 'Vehicle Age' feature is created.")

    # Thực hiện tính toán Vehicle Age trên dataframe data
    if "Date" in data.columns and "Model Year" in data.columns:
        data["Date_temp"] = data["Date"].fillna(2020)
        data["Date_temp"] = pd.to_datetime(data["Date_temp"], format='%Y', errors='coerce').dt.year
        data["Model Year_temp"] = data["Model Year"].fillna(data["Model Year"].median())
        if not data["Model Year_temp"].isnull().any():
            data["Model Year_temp"] = data["Model Year_temp"].astype(int)
        valid_age_calc = data['Date_temp'].notna() & data['Model Year_temp'].notna()
        data.loc[valid_age_calc, "Vehicle Age"] = data.loc[valid_age_calc, "Date_temp"] - data.loc[valid_age_calc, "Model Year_temp"]
        # Không drop cột tạm để dùng cho plot nếu cần
    else:
        st.error("❌ Missing 'Model Year' or 'Date' columns. Cannot compute 'Vehicle Age'.")


    # Step 7: Visualize Data
    st.header("Step 7: Visualize Data")
    st.write("Visualize the relationship between 'Vehicle Age' and 'Vehicle Population'.")
    code_step7 = """
import matplotlib.pyplot as plt
import seaborn as sns

# Scatter plot: Vehicle Age vs. Vehicle Population
if "Vehicle Age" in data.columns and "Vehicle Population" in data.columns:
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="Vehicle Age", y="Vehicle Population", data=data)
    plt.title("Vehicle Age vs. Vehicle Population")
    plt.xlabel("Vehicle Age")
    plt.ylabel("Vehicle Population")
    plt.grid(True)
    # plt.show() # Use st.pyplot(plt) in Streamlit
    st.pyplot(plt) # Display plot in Streamlit
else:
    print("Cannot plot: Missing 'Vehicle Age' or 'Vehicle Population'.")
"""
    st.code(code_step7, language="python")
    st.write("**Explanation**: A scatter plot visualizes the relationship.")

    # Vẽ biểu đồ thực tế
    if "Vehicle Age" in data.columns and "Vehicle Population" in data.columns:
        st.write("### 🔍 Vehicle Age vs. Population")
        fig, ax = plt.subplots(figsize=(10, 6)) # Tạo figure và axes
        sns.scatterplot(x="Vehicle Age", y="Vehicle Population", data=data, color="darkblue", ax=ax)
        ax.set_title("Vehicle Age vs. Vehicle Population") # Thêm tiêu đề
        ax.set_xlabel("Vehicle Age")
        ax.set_ylabel("Vehicle Population")
        ax.grid(True) # Thêm lưới
        ax.set_facecolor("#f2f9fa") # Màu nền
        st.pyplot(fig) # Hiển thị plot
    else:
        st.warning("⚠️ Cannot generate plots. Ensure 'Vehicle Age' and 'Vehicle Population' exist.")

    st.write("### 📌 Insights")
    st.write("The Vehicle Population is highest for newer vehicles...") # Giữ nguyên insight


    # Step 8: Split Data into Training and Validation Sets (Chỉ hiển thị code, không thực thi split ở đây)
    # Việc split thực sự nên thực hiện một lần (có thể offline hoặc trong bước Wrangling)
    # và lưu lại để Model Selection sử dụng.
    st.header("Step 8: Split Data into Training and Validation Sets")
    st.write("Split the dataset into training and validation sets for modeling.")
    code_step8 = """
from sklearn.model_selection import train_test_split

# Assume 'data_processed' is the final cleaned dataframe from Wrangling
# Assume 'Vehicle Population' is the target variable
if 'data_processed' in locals() and 'Vehicle Population' in data_processed.columns:
    X = data_processed.drop(columns=["Vehicle Population"])
    y = data_processed["Vehicle Population"]

    # Split into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Data split completed.")
    print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
    print(f"X_val shape: {X_val.shape}, y_val shape: {y_val.shape}")

    # ---- IMPORTANT ----
    # In a real pipeline, save these split dataframes to files
    # X_train.to_csv('data/X_train.csv', index=False)
    # y_train.to_csv('data/y_train.csv', index=False)
    # X_val.to_csv('data/X_val.csv', index=False) # Or X_test if this is the final test set
    # y_val.to_csv('data/y_val.csv', index=False) # Or y_test
    # -----------------

else:
    print("Cannot perform split. Ensure 'data_processed' DataFrame exists and has 'Vehicle Population'.")
"""
    st.code(code_step8, language="python")
    st.write("**Explanation**: The dataset is split using `train_test_split()`. **Note:** In this multi-page app, the actual split data should be loaded in the 'Model Selection' page, not re-split here.")


    # Step 9: Final Check for Missing Values (Trên dữ liệu gốc hoặc đã xử lý)
    st.header("Step 9: Final Check for Missing Values")
    st.write("Perform a final check for missing values.")
    code_step9 = """
# Check missing values on the original loaded data for EDA purposes
print("Missing values check on loaded data:")
print(data.isnull().sum())
"""
    st.code(code_step9, language="python")
    st.write("**Explanation**: Final check for missing values.")


    # Conclusion
    st.header("Conclusion")
    st.write("EDA process included feature engineering and visualization...")

    st.write("### 📌 Processed Dataset Preview (Example from X_train.csv)")
    # Tải thử X_train để preview
    x_train_preview = load_data("X_train.csv") # Sử dụng lại hàm load_data
    if x_train_preview is not None:
        st.dataframe(x_train_preview.head())
    else:
        st.warning("Could not load 'X_train.csv' for preview.")

    # --- KẾT THÚC CODE CỦA PHẦN eda ---
else:
    st.error("Failed to load data for EDA.")