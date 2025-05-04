import streamlit as st
import pandas as pd
import numpy as np
import math
# Import các thư viện ML cần thiết
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV, train_test_split # GridSearchCV nếu dùng, train_test_split nếu cần split lại
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.utils import shuffle
from catboost import CatBoostRegressor # Cần cài đặt: pip install catboost
# from xgboost import XGBRegressor # Cần cài đặt: pip install xgboost
from tqdm import tqdm # Cần cài đặt: pip install tqdm

from utils.data_loader import load_split_data # Import hàm tải dữ liệu đã split

st.set_page_config(page_title="Model Selection", layout="wide")

st.title("📈 Dashboard")

st.warning("""📌 Intuition: We aim to predict vehicle population... (giữ nguyên)""")

# --- Tải dữ liệu đã được split ---
# X_train, X_test, y_train, y_test = load_split_data()
# Lưu ý: Code gốc có vẻ dùng nhiều bộ dữ liệu khác nhau (X_val, X_test, X_train_cat, X_test_cat...)
# Cần đảm bảo các file dữ liệu này tồn tại và được load đúng cách.
# Giả định đơn giản là có X_train, y_train, X_test, y_test từ load_split_data
X_train, X_test, y_train, y_test = load_split_data()

# Giả định các biến thể khác (ví dụ _cat) được tạo từ đây hoặc load riêng
# Ví dụ: Tạo X_train_cat, X_test_cat nếu cần cho CatBoost
categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist() # Xác định cột categorical
X_train_cat = X_train.copy()
X_test_cat = X_test.copy()
y_train_full = y_train.copy() # Sử dụng y_train gốc
y_test_cat = y_test.copy()   # Sử dụng y_test gốc

if X_train is not None and y_train is not None and X_test is not None and y_test is not None:
    st.success("Split data loaded successfully.")

    # --- BẮT ĐẦU CODE CỦA PHẦN model_selection TỪ FILE GỐC ---

    # --- Random Forest ---
    st.header("Random Forest") # Dùng header thay vì title

    st.write("### Step 1: Train Random Forest Model")
    st.markdown("Train a basic Random Forest model...")
    code1 = '''
import math
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.utils import shuffle

# Assume X_train, y_train, X_test, y_test are loaded
# Use X_test as validation set for consistency with code snippet
X_val, y_val = X_test, y_test # Using test set as validation here based on snippet logic

# Train Random Forest model
random_forest_model = RandomForestRegressor(random_state=28)
random_forest_model.fit(X_train, y_train)

# Shuffle test data (as done in snippet)
X_test_shuffled, y_test_shuffled = shuffle(X_test, y_test, random_state=42)

# Evaluate on Validation Set (using original X_test/y_test as X_val/y_val)
y_pred_val = random_forest_model.predict(X_val)
print("VALIDATION SET (using Test Set)")
print("Mean Absolute Error (MAE):", mean_absolute_error(y_val, y_pred_val))
print("Root Mean Squared Error (RMSE):", math.sqrt(mean_squared_error(y_val, y_pred_val)))
print("R-squared (R2):", r2_score(y_val, y_pred_val))

# Evaluate on (Shuffled) Test Set
y_pred_test = random_forest_model.predict(X_test_shuffled)
print("\\nTEST SET (Shuffled)")
print("Mean Absolute Error (MAE):", mean_absolute_error(y_test_shuffled, y_pred_test))
print("Root Mean Squared Error (RMSE):", math.sqrt(mean_squared_error(y_test_shuffled, y_pred_test)))
print("R-squared (R2):", r2_score(y_test_shuffled, y_pred_test))
'''
    st.code(code1, language="python")
    # (Optionally run and display results if needed, requires executing the model training)

    st.write("### Step 2: Hyperparameter Tuning with GridSearchCV")
    st.markdown("Tune hyperparameters using **GridSearchCV**.")
    code2 = '''
from sklearn.model_selection import GridSearchCV
import math

# Define smaller grid for faster demo if needed
param_grid = {
    "n_estimators": [50, 100], # Reduced options
    "max_depth": [10, 20],    # Reduced options
    "min_samples_split": [5, 10],
    "min_samples_leaf": [2, 4],
    # "max_features": ["sqrt", "log2"], # Use default or specify one
    # "bootstrap": [True, False]
}

# Assume random_forest_model is initialized
# grid_search = GridSearchCV(estimator=random_forest_model, param_grid=param_grid, cv=3, # Reduced CV folds
#                         scoring="neg_mean_squared_error", n_jobs=-1, verbose=1) # Reduced verbosity

# grid_search.fit(X_train, y_train)
# print(f"Best Parameters: {grid_search.best_params_}")
# print(f"Best RMSE from GridSearchCV: {math.sqrt(-grid_search.best_score_)}")
print("GridSearchCV execution skipped in this view for brevity.")
print("Best Parameters (example): {'max_depth': 20, 'min_samples_leaf': 2, 'min_samples_split': 5, 'n_estimators': 100}")
print("Best RMSE from GridSearchCV (example): 4000.0")
'''
    st.code(code2, language="python")

    st.write("### Step 3: Random State Tuning")
    st.markdown("Experiment with random states.")
    code3 = '''
from tqdm import tqdm
import math

list_rmse = []
min_rmse = float('inf')
best_state = -1

# print("Running Random State Tuning (may take time)...")
# for i in tqdm(range(1, 10)): # Reduced range for demo
#     rf = RandomForestRegressor(random_state=i, n_estimators=50) # Use fewer estimators for speed
#     rf.fit(X_train, y_train)
#     y_pred = rf.predict(X_test) # Use original test set
#     rmse_now = math.sqrt(mean_squared_error(y_test, y_pred))
#     if rmse_now < min_rmse:
#         min_rmse = rmse_now
#         best_state = i
#         # print(f"New Min RMSE: {min_rmse} at state {i}") # Reduce printing inside loop
#     list_rmse.append({"state": i, "rmse": rmse_now})

# print(f"\\nOverall Min RMSE: {min_rmse} found at state {best_state}")
# top_5_rmse = sorted(list_rmse, key=lambda x: x['rmse'])[:5]
# print("\\nTop 5 Random States:")
# for top_rmse in top_5_rmse:
#     print(f"State: {top_rmse['state']}, RMSE: {top_rmse['rmse']}")

print("Random State Tuning skipped in this view for brevity.")
print("Example Result: Min RMSE 3700.0 at state 42")
print("Top 5 States (example): [(42, 3700.0), (28, 3710.5), ...]")

'''
    st.code(code3, language="python")


    # --- CatBoost ---
    st.header("CatBoost")

    st.write("### Step 1: Train CatBoost Model")
    st.markdown("Train a CatBoost model and evaluate.")
    code4 = '''
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import math
import numpy as np

# Assume X_train_cat, y_train_full, X_test_cat, y_test_cat are loaded/defined
# Assume categorical_cols list is defined

best_params_catboost = { # Example parameters
    'iterations': 500, 'learning_rate': 0.1, 'depth': 8, 'l2_leaf_reg': 3,
    'verbose': False, 'random_state': 42
}

catboost_model = CatBoostRegressor(**best_params_catboost)

# print("Training CatBoost...")
# catboost_model.fit(X_train_cat, y_train_full, cat_features=categorical_cols)

# print("Predicting with CatBoost...")
# catboost_preds = catboost_model.predict(X_test_cat)

# print("Evaluating CatBoost...")
# catboost_mae = mean_absolute_error(y_test_cat, catboost_preds)
# catboost_rmse = np.sqrt(mean_squared_error(y_test_cat, catboost_preds))
# catboost_r2 = r2_score(y_test_cat, catboost_preds)

# print("*" * 50)
# print("CATBOOST TEST SET RESULTS")
# print(f"Mean Absolute Error (MAE): {catboost_mae}")
# print(f"Root Mean Squared Error (RMSE): {catboost_rmse}")
# print(f"R-squared (R2): {catboost_r2}")

print("CatBoost Training/Evaluation skipped for brevity.")
print("Example Results:")
print("MAE: 2092.98")
print("RMSE: 5661.89")
print("R2: 0.9154")
'''
    st.code(code4, language="python")

    st.write("### Step 2: Hyperparameter Tuning (CatBoost)")
    st.markdown("Fine-tune CatBoost hyperparameters.")
    # Hiển thị code GridSearchCV cho CatBoost (tương tự RF)
    code5_catboost_tuning = '''
# Define parameter grid (example)
param_grid_catboost = {
    'iterations': [500, 1000],
    'learning_rate': [0.05, 0.1],
    'depth': [6, 8],
    # ... other params
    'verbose': [False]
}

# Initialize CatBoost
# catboost_model_tune = CatBoostRegressor(random_state=42, cat_features=categorical_cols)

# Perform GridSearchCV
# grid_search_catboost = GridSearchCV(catboost_model_tune, param_grid_catboost, cv=2, n_jobs=-1, scoring='neg_root_mean_squared_error')
# grid_search_catboost.fit(X_train_cat, y_train_full)

# best_params_catboost = grid_search_catboost.best_params_
# print("Best parameters found by GridSearchCV:", best_params_catboost)

# Train the model with the best parameters
# best_catboost_model = grid_search_catboost.best_estimator_
# Evaluate...

print("CatBoost GridSearchCV skipped for brevity.")
print("Example Best Params: {'depth': 8, 'iterations': 1000, 'learning_rate': 0.1}")
'''
    st.code(code5_catboost_tuning, language="python")


    # --- Stacking ---
    st.header("Stacking Multiple Models")
    st.warning("📌 Intuition: Leveraging strengths...") # Giữ nguyên

    st.write("### Method 1: Stacking RF and CatBoost -> Linear Regression")
    st.markdown("Combine RF and CatBoost predictions using Linear Regression as meta-model.")
    code_stack_1 = '''
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

# Assume random_forest_model and best_catboost_model are trained models
# Assume X_train, X_train_cat, X_test, X_test_cat, y_train, y_test are available

# print("Generating base model predictions for stacking (Method 1)...")
# rf_preds_train = random_forest_model.predict(X_train)
# cb_preds_train = best_catboost_model.predict(X_train_cat)
# rf_preds_test = random_forest_model.predict(X_test)
# cb_preds_test = best_catboost_model.predict(X_test_cat)

# stacked_features_train = np.column_stack((rf_preds_train, cb_preds_train))
# stacked_features_test = np.column_stack((rf_preds_test, cb_preds_test))

# print("Training Linear Regression meta-model...")
# meta_model_lr = LinearRegression()
# meta_model_lr.fit(stacked_features_train, y_train)

# print("Predicting with stacked model (LR)...")
# stacked_preds_lr_test = meta_model_lr.predict(stacked_features_test)
# stacked_preds_lr_test = np.maximum(stacked_preds_lr_test, 0) # Ensure non-negative

# print("Evaluating stacked model (LR)...")
# rmse_stacked_lr = np.sqrt(mean_squared_error(y_test, stacked_preds_lr_test))
# mae_stacked_lr = mean_absolute_error(y_test, stacked_preds_lr_test)
# r2_stacked_lr = r2_score(y_test, stacked_preds_lr_test)

# print("\\nSTACKING METHOD 1 (LR Meta-Model) RESULTS")
# print(f"Mean Absolute Error (MAE): {mae_stacked_lr}")
# print(f"Root Mean Squared Error (RMSE): {rmse_stacked_lr}")
# print(f"R-squared (R2): {r2_stacked_lr}")

print("Stacking Method 1 skipped for brevity.")
print("Example Results:")
print("MAE: 564.66")
print("RMSE: 3757.97")
print("R2: 0.9627")
'''
    st.code(code_stack_1, language="python")

    st.write("### Method 2: Stacking Two RFs and CatBoost -> Random Forest (BEST)")
    st.markdown("Stack predictions using Random Forest as meta-model.")
    code_stack_2 = '''
from sklearn.ensemble import RandomForestRegressor

# Assume random_forest_model, random_forest_model_2, best_catboost_model are trained
# Assume necessary data splits are available

# print("Generating base model predictions for stacking (Method 2)...")
# rf1_preds_train = random_forest_model.predict(X_train)
# rf2_preds_train = random_forest_model_2.predict(X_train) # Requires a second RF model
# cb_preds_train = best_catboost_model.predict(X_train_cat)

# rf1_preds_test = random_forest_model.predict(X_test)
# rf2_preds_test = random_forest_model_2.predict(X_test)
# cb_preds_test = best_catboost_model.predict(X_test_cat)

# Stack features (example with 2 RF + CB)
# stacked_features_train_rf_cb = np.column_stack((rf1_preds_train, rf2_preds_train, cb_preds_train))
# stacked_features_test_rf_cb = np.column_stack((rf1_preds_test, rf2_preds_test, cb_preds_test))

# print("Training Random Forest meta-model...")
# meta_model_rf = RandomForestRegressor(random_state=28)
# meta_model_rf.fit(stacked_features_train_rf_cb, y_train)

# print("Predicting with stacked model (RF)...")
# stacked_preds_rf_cb_test = meta_model_rf.predict(stacked_features_test_rf_cb)
# stacked_preds_rf_cb_test = np.maximum(stacked_preds_rf_cb_test, 0)

# print("Evaluating stacked model (RF)...")
# rmse_stacked_rf_cb = np.sqrt(mean_squared_error(y_test, stacked_preds_rf_cb_test))
# mae_stacked_rf_cb = mean_absolute_error(y_test, stacked_preds_rf_cb_test)
# r2_stacked_rf_cb = r2_score(y_test, stacked_preds_rf_cb_test)

# print("\\nSTACKING METHOD 2 (RF Meta-Model) RESULTS")
# print(f"Mean Absolute Error (MAE): {mae_stacked_rf_cb}")
# print(f"Root Mean Squared Error (RMSE): {rmse_stacked_rf_cb}")
# print(f"R-squared (R2): {r2_stacked_rf_cb}")

print("Stacking Method 2 skipped for brevity.")
print("Example Results (Two RF + CB -> RF):")
print("MAE: 563.79")
print("RMSE: 3736.97")
print("R2: 0.9631")

print("\nExample Results (Two RF -> RF):") # From result table
print("MAE: 559.90")
print("RMSE: 3719.93")
print("R2: 0.9635")
'''
    st.code(code_stack_2, language="python")

    # --- KẾT THÚC CODE CỦA PHẦN model_selection ---
else:
    st.error("Failed to load split data. Cannot proceed with model selection.")