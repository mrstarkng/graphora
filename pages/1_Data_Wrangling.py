import streamlit as st
import pandas as pd

st.set_page_config(page_title="Xử lý dữ liệu", layout="wide")

st.title("Xử lý dữ liệu (Data Wrangling)")
st.markdown("Chao mừng bạn đến với trang xử lý dữ liệu!")
st.markdown("Trang này giúp bạn xử lý dữ liệu một cách dễ dàng và nhanh chóng.")

# Tải dữ liệu
st.subheader("📥 Tải dữ liệu")
uploaded_file = st.file_uploader("Tải tệp dữ liệu (.csv hoặc .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ Đã tải dữ liệu thành công!")
    st.dataframe(df.head())

    # Bước 2: Tổng quan dữ liệu
    st.subheader("🔍 Tổng quan tập dữ liệu")
    st.markdown(f"**Kích thước dữ liệu:** {df.shape[0]} dòng, {df.shape[1]} cột")

    st.markdown("**Thông tin cột:**")
    col_info = pd.DataFrame({
        "Tên cột": df.columns,
        "Kiểu dữ liệu": df.dtypes.values,
        "Số giá trị không null": df.notnull().sum().values,
        "Số giá trị duy nhất": df.nunique().values
    })
    st.dataframe(col_info)

    st.markdown("**Thống kê mô tả (các cột số):**")
    st.dataframe(df.describe().transpose())

    # Bước 3: Xử lý giá trị thiếu
    st.subheader("🧼 Xử lý giá trị thiếu")
    missing_info = df.isnull().sum()
    if missing_info.sum() == 0:
        st.success("✅ Không có giá trị thiếu trong dữ liệu.")
    else:
        st.warning(f"⚠️ Có {missing_info.sum()} giá trị thiếu trong dữ liệu.")
        st.markdown("**🔍 Thống kê giá trị thiếu theo cột:**")

        option = st.radio("Chọn phương pháp xử lý", ["Không xử lý", "Xoá dòng thiếu", "Điền giá trị cụ thể", "Điền theo trung bình / mode / 0"])
        if option == "Xoá dòng thiếu":
            df = df.dropna()
            st.success("✅ Đã xoá các dòng có giá trị thiếu.")
        elif option == "Điền giá trị cụ thể":
            selected_col = st.selectbox("Chọn cột", df.columns[df.isnull().any()])
            fill_value = st.text_input("Nhập giá trị thay thế")
            if st.button("Áp dụng"):
                df[selected_col] = df[selected_col].fillna(fill_value)
                st.success(f"✅ Đã điền NaN trong cột '{selected_col}' bằng '{fill_value}'")
        elif option == "Điền theo trung bình / mode / 0":
            selected_col = st.selectbox("Chọn cột", df.columns[df.isnull().any()])
            method = st.selectbox("Phương pháp", ["Trung bình", "Mode", "0"])
            if st.button("Áp dụng phương pháp"):
                try:
                    if method == "Trung bình":
                        value = df[selected_col].mean()
                    elif method == "Mode":
                        value = df[selected_col].mode()[0]
                    else:
                        value = 0
                    df[selected_col] = df[selected_col].fillna(value)
                    st.success(f"✅ Đã điền NaN trong cột '{selected_col}' bằng giá trị {method.lower()}: {value}")
                except Exception as e:
                    st.error(f"Lỗi: {e}")

    # Bước 4: Xử lý dữ liệu trùng lặp
    st.subheader("📛 Xử lý dòng trùng lặp")
    num_duplicates = df.duplicated().sum()
    if num_duplicates == 0:
        st.success("✅ Không có dòng trùng lặp.")
    else:
        st.warning(f"⚠️ Có {num_duplicates} dòng trùng lặp trong dữ liệu.")
        st.dataframe(df[df.duplicated(keep=False)])
        if num_duplicates > 0 and st.button("Xoá dòng trùng"):
            df = df.drop_duplicates()
            st.success("✅ Đã xoá dòng trùng lặp.")

    # Bước 5: Chuyển đổi kiểu dữ liệu
    st.subheader("🔁 Chuyển đổi kiểu dữ liệu")
    col_to_convert = st.selectbox("Chọn cột cần chuyển", df.columns)
    target_type = st.selectbox("Kiểu dữ liệu muốn chuyển", ["int", "float", "str"])
    if st.button("Chuyển đổi kiểu dữ liệu"):
        try:
            if target_type == "int":
                df[col_to_convert] = df[col_to_convert].astype(int)
            elif target_type == "float":
                df[col_to_convert] = df[col_to_convert].astype(float)
            else:
                df[col_to_convert] = df[col_to_convert].astype(str)
            st.success(f"✅ Đã chuyển '{col_to_convert}' sang kiểu {target_type}.")
        except Exception as e:
            st.error(f"❌ Lỗi khi chuyển kiểu dữ liệu: {e}")

    # Bước 6: Tải dữ liệu sau xử lý
    st.subheader("💾 Tải dữ liệu đã xử lý")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Tải xuống dữ liệu CSV", csv, "processed-data.csv", mime="text/csv")
