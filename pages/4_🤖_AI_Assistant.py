import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from utils.config import GEMINI_API_KEY # Đảm bảo import đúng
import numpy as np
import os

st.set_page_config(page_title="AI Assistant", layout="wide")

st.title("🤖 AI Assistant")
st.write("### 📌 Upload data, visualize, and ask the AI")

# --- Configure Gemini AI ---
model = None # Khởi tạo model là None
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Error configuring Gemini AI: {e}")
    st.warning("Please ensure API key is set correctly.")

# Initialize session memory
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
# ... (Thêm các state khác nếu cần) ...

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"], key="ai_assistant_uploader_final") # Key mới nhất

# --- Xử lý Data Source và tải dữ liệu ---
# !!! Quan trọng: Logic tải df_to_analyze cần đầy đủ và chính xác !!!
df_to_analyze = None
analysis_target_name = None
if uploaded_file:
     try:
         # Đọc file vào dataframe MỚI mỗi lần upload để đảm bảo sạch
         current_df = pd.read_csv(uploaded_file)
         df_to_analyze = current_df # Gán cho biến sẽ dùng
         analysis_target_name = uploaded_file.name
         # Lưu vào state nếu bạn cần truy cập lại mà không cần upload lại
         # st.session_state.current_df = current_df
     except Exception as e:
         st.error(f"Error reading uploaded file: {e}")
         df_to_analyze = None
# Bổ sung logic load processed data nếu bạn có lựa chọn đó


# Chỉ hiển thị phần còn lại nếu có dữ liệu và model
if df_to_analyze is not None and model and analysis_target_name:
    st.success(f"Ready to analyze: **{analysis_target_name}** ({df_to_analyze.shape[0]} rows, {df_to_analyze.shape[1]} cols)")

    # --- PHẦN TRỰC QUAN HÓA VỚI CÁC TAB ---
    st.write("---")
    st.subheader("📊 Data Visualization")

    # Lấy danh sách các loại cột từ df_to_analyze MỘT LẦN
    try:
        numeric_columns = df_to_analyze.select_dtypes(include=np.number).columns.tolist()
        categorical_columns = df_to_analyze.select_dtypes(exclude=np.number).columns.tolist()
        datetime_columns = df_to_analyze.select_dtypes(include='datetime').columns.tolist()
    except: # Xử lý lỗi nếu select_dtypes datetime không hoạt động
        datetime_columns = []
        # Lấy lại numeric và categorical nếu lỗi xảy ra ở datetime
        numeric_columns = df_to_analyze.select_dtypes(include=np.number).columns.tolist()
        categorical_columns = df_to_analyze.select_dtypes(exclude=np.number).columns.tolist()

    potential_x_line_cols = numeric_columns + datetime_columns

    # Tạo các tab
    tab_dashboard, tab_hist, tab_bar, tab_pie, tab_line = st.tabs([
        "Dashboard", "📊 Histogram", "📶 Bar Chart", "🍕 Pie Chart", "📈 Line Chart"
    ])

    # --- Tab Dashboard Tổng Quan (Giữ nguyên code đang hoạt động) ---
    with tab_dashboard:
        try:
            st.markdown("#### Key Metrics & Quick Plots")
            col_m1, col_m2, col_m3 = st.columns(3)
            try: # Metrics
                col_m1.metric("Total Rows", df_to_analyze.shape[0])
                col_m2.metric("Total Columns", df_to_analyze.shape[1])
                if numeric_columns:
                    metric_col_index = 0 if numeric_columns else -1
                    metric_col = st.selectbox("Select column for Median Metric:", numeric_columns, key="dash_metric_col", index=metric_col_index)
                    if metric_col:
                        median_val = df_to_analyze[metric_col].median()
                        col_m3.metric(f"Median ({metric_col})", f"{median_val:,.2f}")
                else: col_m3.info("No numeric columns for Median Metric.")
            except Exception as e_metric: st.error(f"Err Metrics: {e_metric}")

            st.markdown("---")
            col_d1, col_d2 = st.columns(2)
            with col_d1: # Column 1 Plots
                try:
                    st.markdown("**Quick Distribution Plots**")
                    if numeric_columns:
                        hist_dash_col_index = 0 if numeric_columns else -1
                        hist_dash_col = st.selectbox("Histogram Column:", numeric_columns, key="dash_hist_col", index=hist_dash_col_index)
                        if hist_dash_col:
                            # Bỏ try-except nhỏ bên trong nếu đã có try-except lớn bao ngoài
                            fig_hist_dash = px.histogram(df_to_analyze, x=hist_dash_col, title=f"Hist: {hist_dash_col}", template="plotly_white", height=300)
                            fig_hist_dash.update_layout(margin=dict(t=30, b=10, l=10, r=10))
                            st.plotly_chart(fig_hist_dash, use_container_width=True)
                    else: st.caption("No numeric columns for histogram.")

                    if categorical_columns:
                        bar_dash_col_index = 0 if categorical_columns else -1
                        bar_dash_col = st.selectbox("Bar Chart Column (Top 5):", categorical_columns, key="dash_bar_col", index=bar_dash_col_index)
                        if bar_dash_col:
                            counts_dash = df_to_analyze[bar_dash_col].value_counts().nlargest(5).reset_index()
                            counts_dash.columns = [bar_dash_col, 'count']
                            fig_bar_dash = px.bar(counts_dash, x=bar_dash_col, y='count', title=f"Top 5: {bar_dash_col}", template="plotly_white", height=300, text='count')
                            fig_bar_dash.update_traces(textposition='outside')
                            fig_bar_dash.update_layout(margin=dict(t=30, b=10, l=10, r=10))
                            st.plotly_chart(fig_bar_dash, use_container_width=True)
                    else: st.caption("No categorical columns for bar chart.")
                except Exception as e_col1: st.error(f"Error in Dashboard Column 1: {e_col1}", icon="⚠️")

            with col_d2: # Column 2 Plots & Summary
                 try:
                    st.markdown("**Quick Relationship & Summary**")
                    if len(numeric_columns) >= 2:
                         st.markdown("*Scatter Plot*")
                         scatter_x_index = 0
                         scatter_y_options = [c for c in numeric_columns if c != numeric_columns[scatter_x_index]]
                         scatter_y_index = 0 if scatter_y_options else -1

                         scatter_x = st.selectbox("Scatter X-axis:", numeric_columns, key="dash_scatter_x", index = scatter_x_index)
                         scatter_y = st.selectbox("Scatter Y-axis:", scatter_y_options, key="dash_scatter_y", index = scatter_y_index)
                         scatter_color = st.selectbox("Color by (Optional):", ["None"] + categorical_columns, key="dash_scatter_color")

                         if scatter_x and scatter_y:
                            plot_args = {'x': scatter_x, 'y': scatter_y, 'title': f"{scatter_y} vs {scatter_x}", 'template': "plotly_white", 'height': 300}
                            if scatter_color != "None" and scatter_color in df_to_analyze.columns:
                                plot_args['color'] = scatter_color
                                plot_args['title'] += f" (Colored by {scatter_color})"
                            sample_size = min(1000, df_to_analyze.shape[0])
                            fig_scatter_dash = px.scatter(df_to_analyze.sample(sample_size), **plot_args)
                            fig_scatter_dash.update_layout(margin=dict(t=30, b=10, l=10, r=10))
                            st.plotly_chart(fig_scatter_dash, use_container_width=True)
                    else: st.caption("Need >= 2 numeric columns for scatter plot.")

                    st.markdown("*Data Description Summary*")
                    # Chỉ describe cột số
                    st.dataframe(df_to_analyze[numeric_columns].describe(), height=310)
                 except Exception as e_col2: st.error(f"Error in Dashboard Column 2: {e_col2}", icon="⚠️")
        except Exception as e_tab:
             st.error(f"An unexpected error occurred in the Dashboard tab: {e_tab}", icon="🔥")


    # --- Tab Histogram (Code đã xác minh lại) ---
    with tab_hist:
        st.markdown("**Histogram for Numeric Column**")
        if not numeric_columns: # Kiểm tra trước khi hiển thị selectbox
            st.info("No numeric columns found for histogram.")
        else:
            num_col_hist = st.selectbox(
                "Select numeric column:",
                numeric_columns,
                key="viz_hist_num_select_ok" # Key mới để chắc chắn không trùng
            )
            num_bins_hist = st.slider("Number of bins:", min_value=5, max_value=100, value=30, key="viz_hist_bins_ok") # Key mới
            if num_col_hist: # Kiểm tra xem cột đã được chọn chưa
                try:
                    fig_hist = px.histogram(
                        df_to_analyze, # Dùng df_to_analyze
                        x=num_col_hist, nbins=num_bins_hist,
                        title=f"Distribution of {num_col_hist}", template="plotly_white"
                    )
                    fig_hist.update_layout(bargap=0.1)
                    st.plotly_chart(fig_hist, use_container_width=True)
                except Exception as e:
                    st.error(f"Error generating histogram for {num_col_hist}: {e}", icon="⚠️")


    # --- Tab Bar Chart (Code đã xác minh lại) ---
    with tab_bar:
        st.markdown("**Bar Chart for Categorical Column**")
        if not categorical_columns:
            st.info("No categorical columns found for bar chart.")
        else:
            cat_col_bar = st.selectbox(
                "Select categorical column:",
                categorical_columns,
                key="viz_bar_cat_select_ok" # Key mới
            )
            top_n_bar = st.slider("Show Top N categories:", min_value=3, max_value=50, value=10, key="viz_bar_topn_ok") # Key mới
            if cat_col_bar:
                try:
                    # Dùng df_to_analyze
                    counts = df_to_analyze[cat_col_bar].value_counts().nlargest(top_n_bar).reset_index()
                    counts.columns = [cat_col_bar, 'count']
                    fig_bar = px.bar(
                        counts, x=cat_col_bar, y='count',
                        title=f"Top {top_n_bar} Categories in {cat_col_bar}",
                        template="plotly_white", text='count'
                    )
                    fig_bar.update_traces(textposition='outside')
                    fig_bar.update_layout(xaxis_title=cat_col_bar, yaxis_title="Count")
                    st.plotly_chart(fig_bar, use_container_width=True)
                except Exception as e:
                    st.error(f"Error generating bar chart for {cat_col_bar}: {e}", icon="⚠️")


    # --- Tab Pie Chart (Code đã xác minh lại) ---
    with tab_pie:
        st.markdown("**Pie Chart for Categorical Column**")
        if not categorical_columns:
            st.info("No categorical columns found for pie chart.")
        else:
            cat_col_pie = st.selectbox(
                "Select categorical column:",
                categorical_columns,
                key="viz_pie_cat_select_ok" # Key mới
            )
            top_n_pie = st.slider("Show Top N slices (group others):", min_value=2, max_value=20, value=5, key="viz_pie_topn_ok") # Key mới
            if cat_col_pie:
                try:
                    # Dùng df_to_analyze
                    counts = df_to_analyze[cat_col_pie].value_counts().reset_index()
                    counts.columns = [cat_col_pie, 'count']
                    # Logic gộp other
                    if len(counts) > top_n_pie:
                        top_df = counts.nlargest(top_n_pie - 1, 'count')
                        other_sum = counts.nsmallest(len(counts) - (top_n_pie - 1), 'count')['count'].sum()
                        if other_sum > 0:
                            other_row = pd.DataFrame({cat_col_pie: ['Other'], 'count': [other_sum]})
                            pie_df = pd.concat([top_df, other_row], ignore_index=True)
                        else: pie_df = top_df
                    else: pie_df = counts

                    fig_pie = px.pie(
                        pie_df, names=cat_col_pie, values='count',
                        title=f"Proportion of Top ... Categories in {cat_col_pie}", # Title cập nhật
                        template="plotly_white"
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
                except Exception as e:
                    st.error(f"Error generating pie chart for {cat_col_pie}: {e}", icon="⚠️")


    # --- Tab Line Chart (Code đã xác minh lại) ---
    with tab_line:
        st.markdown("**Line Chart for Trends over Time/Sequence**")
        if not potential_x_line_cols or not numeric_columns: # Kiểm tra điều kiện trước
             st.info("Line chart requires suitable X (numeric/datetime) and Y (numeric) columns.")
        else:
            col_x_line = st.selectbox(
                "Select X-axis (Time or Ordered Sequence):",
                potential_x_line_cols,
                index=len(potential_x_line_cols) - 1 if datetime_columns else 0, # logic index cũ
                key="viz_line_x_select_ok" # Key mới
            )
            # Lọc Y options cẩn thận hơn
            y_options = [col for col in numeric_columns if col != col_x_line]
            if not y_options:
                 st.warning(f"No numeric columns available for Y-axis (excluding selected X-axis '{col_x_line}').")
                 col_y_line = None
            else:
                 col_y_line = st.selectbox(
                    "Select Y-axis (Numeric Value):",
                    y_options,
                    key="viz_line_y_select_ok" # Key mới
                 )

            if col_x_line and col_y_line: # Chỉ chạy nếu cả X và Y hợp lệ
                try:
                    # Dùng df_to_analyze
                    df_line = df_to_analyze[[col_x_line, col_y_line]].copy()
                    # Logic chuyển đổi và sắp xếp
                    if pd.api.types.is_numeric_dtype(df_line[col_x_line]): pass
                    elif not pd.api.types.is_datetime64_any_dtype(df_line[col_x_line]):
                         try:
                             df_line[col_x_line] = pd.to_datetime(df_line[col_x_line])
                             if col_x_line not in datetime_columns: datetime_columns.append(col_x_line)
                         except Exception: st.warning(f"Could not convert '{col_x_line}' to Date/Time.", icon="⚠️")

                    df_line = df_line.sort_values(by=col_x_line).dropna(subset=[col_x_line, col_y_line])

                    if not df_line.empty:
                        fig_line = px.line(
                            df_line, x=col_x_line, y=col_y_line,
                            title=f"Trend of {col_y_line} over {col_x_line}",
                            template="plotly_white", markers=True
                        )
                        fig_line.update_layout(xaxis_title=col_x_line, yaxis_title=col_y_line)
                        st.plotly_chart(fig_line, use_container_width=True)
                    else: st.warning(f"No valid data points found for Line Chart.", icon="⚠️")
                except Exception as e:
                    st.error(f"Error generating line chart: {e}", icon="⚠️")
            elif not col_y_line and y_options: # Trường hợp col_y_line chưa được chọn
                 st.info("Please select Y axis.")


    # --- PHẦN HỎI ĐÁP VỚI AI (Đảm bảo dùng df_to_analyze) ---
    st.write("---")
    st.subheader("💬 Ask the AI about this data")
    user_query = st.text_area("Enter your question:", key="ai_query_input_final") # Key mới
    if st.button("Get Answer", key="ai_get_answer_final"): # Key mới
        if user_query and model and df_to_analyze is not None:
            try:
                # Dùng df_to_analyze để tạo context
                csv_text = df_to_analyze.to_csv(index=False)
                max_text_length = 50000
                context_note = f"Analyzing data: '{analysis_target_name}'."
                if len(csv_text) > max_text_length:
                     sample_df = df_to_analyze.head(1000)
                     csv_text = sample_df.to_csv(index=False)
                     context_note += f" Context includes the first {len(sample_df)} rows."
                else: context_note += " Full data context provided."

                # Prompt
                prompt = f"""... {csv_text} ... {context_note} ... User question: "{user_query}" ..."""
                # ... (Gọi API, xử lý response) ...
                response_text = "AI response example." # << Thay bằng response thật
                st.session_state["chat_history"].append({"query": user_query, "response": response_text}) # Lưu response thật
                st.rerun() # Rerun để cập nhật lịch sử

            except Exception as e: st.error(f"An error occurred: {e}", icon="🔥")
        elif not user_query: st.warning("Please enter a question.")
        elif df_to_analyze is None: st.warning("No data loaded to analyze.")
        else: st.warning("AI Model not ready.")


    # --- PHẦN HIỂN THỊ LỊCH SỬ CHAT (Giữ nguyên) ---
    st.write("---")
    if "chat_history" in st.session_state and st.session_state["chat_history"]:
        st.subheader("📝 Chat History")
        # ... (code hiển thị lịch sử chat giữ nguyên) ...
        pass # Thay bằng code thật
        if st.button("Clear Chat History", key="ai_clear_history_final"): # Key mới
                st.session_state["chat_history"] = []
                st.rerun()

# --- Xử lý khi không có model hoặc data ---
elif not model:
    st.warning("AI Assistant requires API configuration.")
elif df_to_analyze is None: # Chỉ kiểm tra df_to_analyze
     st.info("☝️ Upload a CSV file to get started.")