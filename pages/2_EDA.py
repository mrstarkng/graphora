import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Phân tích EDA", layout="wide")
st.title("Phân tích Dữ liệu Khám phá (EDA)")
st.markdown("Chào mừng bạn đến với trang phân tích dữ liệu khám phá!")
st.markdown("Trang này giúp bạn phân tích dữ liệu một cách dễ dàng và nhanh chóng.")

uploaded_file = st.file_uploader("📂 Tải tệp dữ liệu (.csv hoặc .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ Dữ liệu đã được tải thành công.")
    
    # CHIA 2 TAB
    tab1, tab2 = st.tabs(["📊 Phân tích toàn bộ tập dữ liệu", "🔍 Phân tích chi tiết từng cột"])

    # ========= TAB 1 =========
    with tab1:
        ### Lọc dữ liệu
        st.sidebar.header("🔎 Bộ lọc dữ liệu")
        df_filtered = df.copy()

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                min_val, max_val = float(df[col].min()), float(df[col].max())
                selected_range = st.sidebar.slider(f"{col}", min_value=min_val, max_value=max_val, value=(min_val, max_val))
                df_filtered = df_filtered[(df_filtered[col] >= selected_range[0]) & (df_filtered[col] <= selected_range[1])]
            elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                unique_vals = df[col].dropna().unique().tolist()
                selected_vals = st.sidebar.multiselect(f"{col}", unique_vals, default=unique_vals)
                df_filtered = df_filtered[df_filtered[col].isin(selected_vals)]

        st.markdown(f"**📦 Dữ liệu sau lọc:** ({df_filtered.shape[0]} dòng)")
        st.dataframe(df_filtered.head())

        # Thống kê mô tả
        st.subheader("📈 Thống kê mô tả")
        st.dataframe(df_filtered.describe(include='all').transpose())

        # Skewness & Kurtosis
        st.subheader("📐 Skewness & Kurtosis")
        num_cols = df_filtered.select_dtypes(include=['float', 'int']).columns
        stats_df = pd.DataFrame({
            "Skewness": df_filtered[num_cols].skew(),
            "Kurtosis": df_filtered[num_cols].kurt()
        })
        st.dataframe(stats_df)

        # Outlier
        st.subheader("🚨 Phát hiện outlier")
        selected_col_outlier = st.selectbox("Cột cần phát hiện outlier", num_cols)
        Q1 = df_filtered[selected_col_outlier].quantile(0.25)
        Q3 = df_filtered[selected_col_outlier].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df_filtered[(df_filtered[selected_col_outlier] < Q1 - 1.5 * IQR) | (df_filtered[selected_col_outlier] > Q3 + 1.5 * IQR)]
        if outliers.empty:
            st.write("Không có outliers trong cột này.")
        else:
            st.write(f"Số lượng outliers trong `{selected_col_outlier}`: {outliers.shape[0]}")
            st.dataframe(outliers)

        # Heatmap
        st.subheader("🔥 Ma trận tương quan")
        if len(num_cols) >= 2:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df_filtered[num_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

        # Scatter
        st.subheader("🔁 Biểu đồ phân tán")
        if len(num_cols) >= 2:
            x_axis = st.selectbox("Trục X", num_cols)
            y_axis = st.selectbox("Trục Y", num_cols, index=1)
            color_col = st.selectbox("Màu theo cột", [None] + df_filtered.columns.tolist())
            fig3 = px.scatter(df_filtered, x=x_axis, y=y_axis, color=color_col if color_col != "None" else None)
            st.plotly_chart(fig3)

    # ========= TAB 2 =========
    with tab2:
        st.subheader("🔎 Phân tích nâng cao từng cột")

        selected_col = st.selectbox("📌 Chọn cột để phân tích", df.columns)
        col_data = df[selected_col]

        st.write("🔢 Kiểu dữ liệu:", col_data.dtype)
        st.write("📏 Tổng số dòng:", len(col_data))
        st.write("❌ Số giá trị thiếu:", col_data.isnull().sum())
        st.write("🧮 Số giá trị duy nhất:", col_data.nunique())

        if pd.api.types.is_numeric_dtype(col_data):
            st.subheader("📊 Thống kê mô tả")
            st.dataframe(col_data.describe())

            st.write("📐 **Skewness**:", col_data.skew())
            st.write("🎯 **Kurtosis**:", col_data.kurt())

            st.subheader("🚨 Outliers theo IQR")
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            outliers = col_data[(col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)]
            st.write(f"Số outliers: {outliers.shape[0]}")
            st.dataframe(outliers)

            st.subheader("📈 Histogram")
            fig = px.histogram(df, x=selected_col, nbins=30)
            st.plotly_chart(fig)

            st.subheader("📦 Boxplot")
            fig2 = px.box(df, y=selected_col)
            st.plotly_chart(fig2)

        else:
            st.subheader("📊 Phân phối giá trị phân loại")
            value_counts = col_data.value_counts().reset_index()
            value_counts.columns = [selected_col, 'Số lượng']
            st.dataframe(value_counts)
            fig = px.bar(value_counts, x=selected_col, y='Số lượng')
            st.plotly_chart(fig)

            st.write("📛 Số giá trị trống (''):", (col_data == '').sum())
