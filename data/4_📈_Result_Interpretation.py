"""""
import pandas as pd

st.set_page_config(page_title="Result Interpretation", layout="wide")

st.title("📈 Result Interpretat")
st.write("### 📌 Understanding Model Performance")

# --- BẮT ĐẦU CODE CỦA PHẦN result_interpretation TỪ FILE GỐC ---

st.write("### Model Performance Metrics")
st.markdown("Below is a table summarizing the performance metrics...")

# Dữ liệu kết quả (giữ nguyên như trong file gốc)
results_df = pd.DataFrame({
    "Model": [
        "CatBoost Only", "Base Random Forest", "Random Forest + CatBoost -> Linear Regression",
        "Two Random Forests -> Random Forest", "Two Random Forests + CatBoost -> Random Forest",
        "Tuned XGBoost"
    ],
    "Mean Absolute Error (MAE)": [2092.98, 559.86, 564.66, 559.90, 563.79, 1075.45],
    "Root Mean Squared Error (RMSE)": [5661.89, 3730.61, 3757.97, 3719.93, 3736.97, 6006.13],
    "R-squared (R2)": [0.9154, 0.9633, 0.9627, 0.9635, 0.9631, 0.9061]
})
st.dataframe(results_df) # Hiển thị dataframe

st.write("### Sample Predictions from Test Set")
st.markdown("The table below shows examples...")

# Dữ liệu sample predictions (giữ nguyên)
catboost_sample_predictions = pd.DataFrame(...)
st.write("#### CatBoost Model Predictions")
st.dataframe(catboost_sample_predictions)

rf_base_sample_predictions = pd.DataFrame(...)
st.write("#### Base Random Forest Predictions")
st.dataframe(rf_base_sample_predictions)

rf_cb_lr_sample_predictions = pd.DataFrame(...)
st.write("#### Random Forest + CatBoost -> Linear Regression Predictions")
st.dataframe(rf_cb_lr_sample_predictions)

rf_only_sample_predictions = pd.DataFrame(...)
st.write("#### Two Random Forests -> Random Forest Predictions")
st.dataframe(rf_only_sample_predictions)

xgb_sample_predictions = pd.DataFrame(...)
st.write("#### Tuned XGBoost Predictions")
st.dataframe(xgb_sample_predictions)

# --- KẾT THÚC CODE CỦA PHẦN result_interpretation ---
""""""