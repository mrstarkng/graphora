import streamlit as st

# Các thư viện phụ
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# Cấu hình trang
st.set_page_config(page_title="📊 Dashboard Giáo dục", layout="wide")
st.title("DASHBOARD")

# Tabs chính
tabs = st.tabs(["📘 Tổng quan", "🏫 Tiểu học", "📚 THCS", "🎓 THPT", "👶 Mẫu giáo"])

# Load dữ liệu chung
@st.cache_data
def load_data():
    return {
        "tong_quan": pd.read_csv("data/tong-quan/tong-quan.csv"),
        "tong_quan_ts": pd.read_csv("data/tong-quan/tong-quan-all.csv"),
        "chi_so": pd.read_csv("data/tong-quan/chi-so-phat-trien.csv"),
        "tieu_hoc": pd.read_csv("data/dia-phuong/tieu-hoc.csv"),
        "thcs": pd.read_csv("data/dia-phuong/THCS.csv"),
        "thpt": pd.read_csv("data/dia-phuong/THPT.csv"),
        "mau_giao": pd.read_csv("data/mau-giao/MG.csv"),
        "mau_giao_tq": pd.read_csv("data/mau-giao/tong-quan-MG.csv"),
    }

data = load_data()

coords_data = [
    {"Địa phương": "An Giang", "Lat": 10.521, "Lon": 105.125},
    {"Địa phương": "Bà Rịa - Vũng Tàu", "Lat": 10.541, "Lon": 107.242},
    {"Địa phương": "Bắc Giang", "Lat": 21.281, "Lon": 106.197},
    {"Địa phương": "Bắc Kạn", "Lat": 22.145, "Lon": 105.834},
    {"Địa phương": "Bạc Liêu", "Lat": 9.2941, "Lon": 105.727},
    {"Địa phương": "Bắc Ninh", "Lat": 21.186, "Lon": 106.076},
    {"Địa phương": "Bến Tre", "Lat": 10.243, "Lon": 106.375},
    {"Địa phương": "Bình Định", "Lat": 14.166, "Lon": 108.905},
    {"Địa phương": "Bình Dương", "Lat": 11.125, "Lon": 106.655},
    {"Địa phương": "Bình Phước", "Lat": 11.750, "Lon": 106.883},
    {"Địa phương": "Bình Thuận", "Lat": 11.100, "Lon": 108.100},
    {"Địa phương": "Cà Mau", "Lat": 9.1796, "Lon": 105.150},
    {"Địa phương": "Cần Thơ", "Lat": 10.045, "Lon": 105.746},
    {"Địa phương": "Cao Bằng", "Lat": 22.665, "Lon": 106.261},
    {"Địa phương": "Đà Nẵng", "Lat": 16.047, "Lon": 108.206},
    {"Địa phương": "Đắk Lắk", "Lat": 12.710, "Lon": 108.237},
    {"Địa phương": "Đắk Nông", "Lat": 12.001, "Lon": 107.700},
    {"Địa phương": "Điện Biên", "Lat": 21.397, "Lon": 103.023},
    {"Địa phương": "Đồng Nai", "Lat": 10.960, "Lon": 106.830},
    {"Địa phương": "Đồng Tháp", "Lat": 10.472, "Lon": 105.629},
    {"Địa phương": "Gia Lai", "Lat": 13.983, "Lon": 108.000},
    {"Địa phương": "Hà Giang", "Lat": 22.825, "Lon": 104.983},
    {"Địa phương": "Hà Nam", "Lat": 20.544, "Lon": 105.922},
    {"Địa phương": "Hà Nội", "Lat": 21.0285, "Lon": 105.8542},
    {"Địa phương": "Hà Tĩnh", "Lat": 18.355, "Lon": 105.887},
    {"Địa phương": "Hải Dương", "Lat": 20.939, "Lon": 106.330},
    {"Địa phương": "Hải Phòng", "Lat": 20.844, "Lon": 106.688},
    {"Địa phương": "Hậu Giang", "Lat": 9.7570, "Lon": 105.641},
    {"Địa phương": "Hòa Bình", "Lat": 20.857, "Lon": 105.337},
    {"Địa phương": "Hưng Yên", "Lat": 20.646, "Lon": 106.051},
    {"Địa phương": "Khánh Hòa", "Lat": 12.253, "Lon": 109.190},
    {"Địa phương": "Kiên Giang", "Lat": 10.008, "Lon": 105.080},
    {"Địa phương": "Kon Tum", "Lat": 14.349, "Lon": 107.986},
    {"Địa phương": "Lai Châu", "Lat": 22.396, "Lon": 103.459},
    {"Địa phương": "Lâm Đồng", "Lat": 11.935, "Lon": 108.439},
    {"Địa phương": "Lạng Sơn", "Lat": 21.847, "Lon": 106.761},
    {"Địa phương": "Lào Cai", "Lat": 22.485, "Lon": 103.970},
    {"Địa phương": "Long An", "Lat": 10.543, "Lon": 106.413},
    {"Địa phương": "Nam Định", "Lat": 20.437, "Lon": 106.162},
    {"Địa phương": "Nghệ An", "Lat": 19.234, "Lon": 104.920},
    {"Địa phương": "Ninh Bình", "Lat": 20.250, "Lon": 105.974},
    {"Địa phương": "Ninh Thuận", "Lat": 11.573, "Lon": 108.988},
    {"Địa phương": "Phú Thọ", "Lat": 21.399, "Lon": 105.232},
    {"Địa phương": "Phú Yên", "Lat": 13.088, "Lon": 109.092},
    {"Địa phương": "Quảng Bình", "Lat": 17.489, "Lon": 106.599},
    {"Địa phương": "Quảng Nam", "Lat": 15.539, "Lon": 108.019},
    {"Địa phương": "Quảng Ngãi", "Lat": 15.120, "Lon": 108.800},
    {"Địa phương": "Quảng Ninh", "Lat": 21.005, "Lon": 107.292},
    {"Địa phương": "Quảng Trị", "Lat": 16.747, "Lon": 107.188},
    {"Địa phương": "Sóc Trăng", "Lat": 9.603, "Lon": 105.979},
    {"Địa phương": "Sơn La", "Lat": 21.316, "Lon": 103.914},
    {"Địa phương": "Tây Ninh", "Lat": 11.365, "Lon": 106.103},
    {"Địa phương": "Thái Bình", "Lat": 20.451, "Lon": 106.336},
    {"Địa phương": "Thái Nguyên", "Lat": 21.593, "Lon": 105.844},
    {"Địa phương": "Thanh Hóa", "Lat": 19.807, "Lon": 105.776},
    {"Địa phương": "Thừa Thiên Huế", "Lat": 16.467, "Lon": 107.595},
    {"Địa phương": "Tiền Giang", "Lat": 10.361, "Lon": 106.355},
    {"Địa phương": "Trà Vinh", "Lat": 9.812, "Lon": 106.299},
    {"Địa phương": "Tuyên Quang", "Lat": 21.823, "Lon": 105.214},
    {"Địa phương": "Vĩnh Long", "Lat": 10.253, "Lon": 105.973},
    {"Địa phương": "Vĩnh Phúc", "Lat": 21.308, "Lon": 105.604},
    {"Địa phương": "Yên Bái", "Lat": 21.704, "Lon": 104.887},
    {"Địa phương": "TP.Hồ Chí Minh", "Lat": 10.7626, "Lon": 106.6602}
]

with tabs[0]:
    st.header("📘 TỔNG QUAN GIÁO DỤC")

    df = data["tong_quan"]
    chi_so = data["chi_so"]
    df_tong = data["tong_quan_ts"]

    # ========== Bộ lọc ==========
    col_start, col_end = st.columns(2)
    with col_start:
        start_year = st.number_input("Năm bắt đầu", min_value=int(df["Năm học"].min()), max_value=int(df["Năm học"].max()), value=2004)
    with col_end:
        end_year = st.number_input("Năm kết thúc", min_value=int(df["Năm học"].min()), max_value=int(df["Năm học"].max()), value=2021)

    if start_year > end_year:
        st.error("❌ Năm bắt đầu phải nhỏ hơn hoặc bằng năm kết thúc.")
        st.stop()
    df_filtered = df[df["Năm học"].between(start_year, end_year)]

    custom_color = {
        "Tiểu học": "lightgreen",
        "Trung học cơ sở": "orange",
        "Trung học phổ thông": "crimson"
    }

    # ========== Thống kê KPIs năm mới nhất ==========
    latest_year = df_filtered["Năm học"].max()
    latest_df = df_filtered[df_filtered["Năm học"] == latest_year]
    st.subheader(f"📊 Thống kê năm {latest_year}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎓 Học sinh", f'{latest_df["Học sinh (nghìn)"].sum():,.1f}K')
    col2.metric("👩‍🏫 Giáo viên", f'{latest_df["Giáo viên (nghìn)"].sum():,.1f}K')
    col3.metric("🏫 Trường", f'{latest_df["Trường"].sum():,.0f}')
    col4.metric("📚 Lớp", f'{latest_df["Lớp (nghìn)"].sum():,.1f}K')

    # ========== Biểu đồ thay đổi theo năm - Tách riêng theo chỉ số ==========
    with st.container():
        st.subheader("📈 Biểu đồ thay đổi số lượng theo năm")

        all_metrics = ["Trường", "Lớp (nghìn)", "Giáo viên (nghìn)", "Học sinh (nghìn)"]
        selected_metrics = st.multiselect("📌 Chọn chỉ số cần hiển thị:", all_metrics, default=all_metrics)

        df_line = df_tong[df_tong["Cấp học"] == "Tổng số"].copy()
        df_line["Năm học"] = pd.to_numeric(df_line["Năm học"], errors="coerce")
        df_line = df_line.sort_values("Năm học")

        color_map = {
            "Trường": "#e6c910",
            "Lớp (nghìn)": "#e69b10",
            "Giáo viên (nghìn)": "#d65875",
            "Học sinh (nghìn)": "#8088d1"
        }

        if selected_metrics:
            # Chia đều các biểu đồ theo hàng ngang 2 cột
            for i in range(0, len(selected_metrics), 2):
                row_metrics = selected_metrics[i:i+2]
                cols = st.columns(len(row_metrics))
                for idx, metric in enumerate(row_metrics):
                    fig_single = px.line(
                        df_line,
                        x="Năm học",
                        y=metric,
                        title=f"📊 {metric}",
                        markers=True,
                        color_discrete_sequence=[color_map.get(metric, "#636EFA")]
                    )
                    fig_single.update_layout(
                        yaxis_title="Số lượng",
                        xaxis_title="Năm học",
                        height=300
                    )
                    with cols[idx]:
                        st.plotly_chart(fig_single, use_container_width=True)
        else:
            st.info("🔍 Vui lòng chọn ít nhất một chỉ số để hiển thị.")

    # ========== Biểu đồ Pie theo cấp học ==========
    st.subheader("📌 Tỷ lệ trường và học sinh theo cấp học")
    cap_ratio = latest_df.groupby("Cấp học")[["Học sinh (nghìn)", "Trường"]].sum().reset_index()
    pie1, pie2 = st.columns(2, gap="large")
    fig_pie_school = px.pie(
        cap_ratio, names="Cấp học", values="Trường",
        title="🎯 Tỷ lệ trường theo cấp",
        color="Cấp học", color_discrete_map=custom_color
    )
    fig_pie_student = px.pie(
        cap_ratio, names="Cấp học", values="Học sinh (nghìn)",
        title="👥 Tỷ lệ học sinh theo cấp",
        color="Cấp học", color_discrete_map=custom_color
    )
    with pie1:
        st.plotly_chart(fig_pie_school, use_container_width=True)
    with pie2:
        st.plotly_chart(fig_pie_student, use_container_width=True)

    # ========== Tỷ lệ giới tính & Sĩ số lớp nằm cạnh ==========
    st.subheader("📊 Tỷ lệ giới tính và sĩ số lớp")

    col_gender, col_classsize = st.columns(2)

    # Tỷ lệ giới tính
    df["Học sinh nam"] = df["Học sinh (nghìn)"] - df["Học sinh nữ (nghìn)"]
    gender_df = df[df["Năm học"].between(start_year, end_year)]
    gender_sum = gender_df.groupby("Năm học")[["Học sinh nữ (nghìn)", "Học sinh nam"]].sum().reset_index()
    gender_sum["Tổng"] = gender_sum["Học sinh nữ (nghìn)"] + gender_sum["Học sinh nam"]
    gender_sum["% Nam"] = gender_sum["Học sinh nam"] / gender_sum["Tổng"] * 100
    gender_sum["% Nữ"] = gender_sum["Học sinh nữ (nghìn)"] / gender_sum["Tổng"] * 100

    df_stacked = gender_sum[["Năm học", "% Nam", "% Nữ"]].rename(columns={"% Nam": "Nam", "% Nữ": "Nữ"})
    df_stacked = df_stacked.melt(id_vars="Năm học", var_name="Giới tính", value_name="Tỷ lệ (%)")

    fig_gender = px.bar(
        df_stacked, x="Năm học", y="Tỷ lệ (%)", color="Giới tính",
        color_discrete_map={"Nam": "deepskyblue", "Nữ": "pink"},
        text="Tỷ lệ (%)", title="Tỷ lệ học sinh nam và nữ theo năm"
    )
    fig_gender.update_layout(barmode="stack", yaxis_range=[0, 100])
    fig_gender.update_traces(texttemplate="%{text:.1f}%", textposition="inside")

    with col_gender:
        st.plotly_chart(fig_gender, use_container_width=True)

    # Sĩ số HS/Lớp
    if "HS/Lớp" not in df.columns:
        df["HS/Lớp"] = df["Học sinh (nghìn)"] / df["Lớp (nghìn)"]

    fig_hs_lop = px.line(
        df,
        x="Năm học",
        y="HS/Lớp",
        color="Cấp học",
        markers=True,
        title="📚 Sĩ số trung bình mỗi lớp (HS/Lớp) theo từng năm và cấp học",
        labels={"HS/Lớp": "Học sinh / lớp", "Năm học": "Năm học"},
        color_discrete_map={
            "Tiểu học": "lightgreen",
            "Trung học cơ sở": "orange",
            "Trung học phổ thông": "crimson"
        }
    )
    fig_hs_lop.update_layout(
        yaxis_title="Học sinh / lớp",
        xaxis=dict(dtick=1),
        legend_title="Cấp học"
    )

    with col_classsize:
        st.plotly_chart(fig_hs_lop, use_container_width=True)

    # ========== Biểu đồ heatmap đưa xuống dưới ==========
    st.subheader("📈 Biến động chỉ số qua các năm (%)")

    chi_so["Năm học"] = pd.to_numeric(chi_so["Năm học"], errors="coerce")
    chi_so_total = chi_so[chi_so["Cấp học"] == "Tổng số"].sort_values("Năm học")

    cols = ["Năm học", "Trường", "Lớp", "Giáo viên", "Học sinh"]
    df_mat = chi_so_total[cols].copy()

    df_delta = df_mat.set_index("Năm học").pct_change() * 100
    df_delta = df_delta.round(1).iloc[1:]
    text_matrix = df_delta.astype(str) + "%"
    z = df_delta.fillna(0).values
    if len(z.shape) == 1:
        z = [z]
        text_matrix = [text_matrix.tolist()]

    colorscale = [
        [0.0, "red"],
        [0.5, "white"],
        [1.0, "limegreen"]
    ]

    max_abs_change = max(abs(df_delta.max().max()), abs(df_delta.min().min()))

    fig_matrix = ff.create_annotated_heatmap(
        z=z,
        x=df_delta.columns.tolist(),
        y=df_delta.index.astype(str).tolist(),
        annotation_text=text_matrix.values,
        colorscale=[  # Màu đỏ - trắng - xanh
            [0.0, "red"],     # Giảm mạnh nhất
            [0.5, "white"],   # Không thay đổi
            [1.0, "green"]    # Tăng mạnh nhất
        ],
        showscale=True,
        zmin=-max_abs_change,
        zmax=max_abs_change
    )

    fig_matrix.update_layout(
        xaxis_title="Chỉ số",
        yaxis_title="Năm học",
        margin=dict(l=50, r=20, t=50, b=50),
        title="📉 Biến động (%) so với năm trước"
    )

    st.plotly_chart(fig_matrix, use_container_width=True)

with tabs[1]:
    st.header("🏫 THỐNG KÊ GIÁO DỤC TIỂU HỌC")

    # ======= 1. Bộ lọc tương tác =======
    df_th = data["tieu_hoc"].copy()
    
    # Chuyển thành DataFrame
    coords_df = pd.DataFrame(coords_data)

    # Gộp vào bảng chính
    df_th = df_th.merge(coords_df, on="Địa phương", how="left")
    df_th["Năm"] = pd.to_numeric(df_th["Năm"], errors="coerce")
    provinces = sorted(df_th["Địa phương"].dropna().unique())
    years = sorted(df_th["Năm"].dropna().unique())

    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("📅 Chọn năm học", years, index=len(years)-1)
    with col2:
        selected_province = st.selectbox("📍 Chọn địa phương", ["Tất cả"] + provinces)

    df_filtered = df_th[df_th["Năm"] == selected_year]
    if selected_province != "Tất cả":
        df_filtered = df_filtered[df_filtered["Địa phương"] == selected_province]

    # ======= 2. KPIs tổng quan =======
    st.subheader("📊 Thống kê tổng quan")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("🏬 Trường", f'{df_filtered["Trường"].sum():,.0f}')
    kpi2.metric("📚 Lớp", f'{df_filtered["Lớp"].sum():,.0f}')
    kpi3.metric("👩‍🏫 Giáo viên", f'{df_filtered["Giáo viên"].sum():,.0f}')
    kpi4.metric("👦 Học sinh", f'{df_filtered["Học sinh"].sum():,.0f}')
    kpi5.metric("🧒 HS dân tộc thiểu số", f'{df_filtered["Học sinh dân tộc thiểu số"].sum():,.0f}')

    # ======= 3. Biểu đồ line theo năm (nếu chọn 1 tỉnh) =======
    if selected_province != "Tất cả":
        df_line = df_th[df_th["Địa phương"] == selected_province]
        st.subheader(f"📈 Biến động tại {selected_province} theo năm")

        color_map = {
            "Trường": "#e6c910",
            "Lớp": "#e69b10",
            "Giáo viên": "#d65875",
            "Học sinh": "#8088d1"
        }

        line_cols = st.columns(2)
        for i, column in enumerate(["Trường", "Lớp", "Giáo viên", "Học sinh"]):
            fig = px.line(
                df_line,
                x="Năm",
                y=column,
                markers=True,
                title=f"{column} qua các năm",
                color_discrete_sequence=[color_map[column]]
            )
            fig.update_layout(
                xaxis_title="Năm học",
                yaxis_title=column
            )
            with line_cols[i % 2]:
                st.plotly_chart(fig, use_container_width=True)

    # ======= 4. Biểu đồ bar ngang theo tỉnh =======
    if selected_province == "Tất cả":
        st.subheader("📌 So sánh giữa các địa phương")

        top_hs = df_filtered.sort_values("Học sinh", ascending=False).head(10)
        top_hs = top_hs.sort_values("Học sinh", ascending=True)
        top_hs["Địa phương"] = pd.Categorical(
            top_hs["Địa phương"], categories=top_hs["Địa phương"], ordered=True
        )
        fig_bar = px.bar(
            top_hs,
            y="Địa phương",
            x="Học sinh",
            orientation="h",
            title="🏆 Top 10 địa phương có số học sinh tiểu học cao nhất",
            color="Học sinh",
            color_continuous_scale="Blues"
        )
        fig_bar.update_layout(
            yaxis_title="Địa phương",
            xaxis_title="Số học sinh"
        )

        top_school = df_filtered.sort_values("Trường", ascending=False).head(10)
        top_school = top_school.sort_values("Trường", ascending=True)
        top_school["Địa phương"] = pd.Categorical(
            top_school["Địa phương"], categories=top_school["Địa phương"], ordered=True
        )
        fig_school_bar = px.bar(
            top_school,
            y="Địa phương",
            x="Trường",
            orientation="h",
            title="🏫 Top 10 địa phương có nhiều trường tiểu học nhất",
            color="Trường",
            color_continuous_scale="YlOrRd"
        )
        fig_school_bar.update_layout(
            yaxis_title="Địa phương",
            xaxis_title="Số trường"
        )

        col_bar1, col_bar2 = st.columns(2)
        with col_bar1:
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_bar2:
            st.plotly_chart(fig_school_bar, use_container_width=True)

    # ======= 5. Bản đồ Scatter Mapbox =======
    if "Lat" in df_filtered.columns and "Lon" in df_filtered.columns:
        st.subheader("📍 Phân bố theo địa phương")

        color_scale_students = [
            [0.0, "#a6cee3"],
            [0.2, "#66b2d6"],
            [0.5, "#1f78b4"],
            [1.0, "#08306b"]
        ]

        fig_map_students = px.scatter_mapbox(
            df_filtered,
            lat="Lat",
            lon="Lon",
            size="Học sinh",
            color="Học sinh",
            hover_name="Địa phương",
            size_max=30,
            zoom=4,
            mapbox_style="carto-positron",
            title="🗺️ Học sinh theo địa phương",
            color_continuous_scale=color_scale_students
        )

        fig_map_schools = px.scatter_mapbox(
            df_filtered,
            lat="Lat",
            lon="Lon",
            size="Trường",
            color="Trường",
            color_continuous_scale="YlOrRd",
            hover_name="Địa phương",
            size_max=20,
            zoom=4,
            mapbox_style="carto-positron",
            title="📏 Trường học theo địa phương"
        )

        col_map1, col_map2 = st.columns(2)
        with col_map1:
            st.plotly_chart(fig_map_students, use_container_width=True)
        with col_map2:
            st.plotly_chart(fig_map_schools, use_container_width=True)
    
    # ========== BIỂU ĐỒ TỈ LỆ GIỚI TÍNH HỌC SINH VÀ GIÁO VIÊN ==========
    st.subheader("Tỉ lệ giới tính học sinh và giáo viên")
    gender_col1, gender_col2 = st.columns(2)

    with gender_col1:
        fig_students = px.pie(
            names=["Nam", "Nữ"],
            values=[
                df_filtered["Học sinh"].sum() - df_filtered["Học sinh nữ"].sum(),
                df_filtered["Học sinh nữ"].sum()
            ],
            hole=0.4,
            title="Tỉ lệ học sinh nam - nữ",
            color_discrete_sequence=["deepskyblue", "pink"]
        )
        st.plotly_chart(fig_students, use_container_width=True)

    with gender_col2:
        fig_teachers = px.pie(
            names=["Nam", "Nữ"],
            values=[
                df_filtered["Giáo viên"].sum() - df_filtered["Giáo viên nữ"].sum(),
                df_filtered["Giáo viên nữ"].sum()
            ],
            hole=0.4,
            title="Tỉ lệ giáo viên nam - nữ",
            color_discrete_sequence=["deepskyblue", "pink"]
        )
        st.plotly_chart(fig_teachers, use_container_width=True)
        
    # ======= Biểu đồ Scatter: Tùy chọn 2 biến để xem tương quan =======
    st.subheader("📌 Mối tương quan giữa các chỉ số")

    available_vars = ["Trường", "Lớp", "Giáo viên", "Học sinh"]
    scatter_x = st.selectbox("📎 Chọn biến trục X", available_vars, index=1)
    scatter_y = st.selectbox("📎 Chọn biến trục Y", available_vars, index=3)

    fig_scatter = px.scatter(
        df_filtered,
        x=scatter_x,
        y=scatter_y,
        size=scatter_y,
        color="Địa phương",
        hover_name="Địa phương",
        title=f"🎯 Tương quan giữa {scatter_x} và {scatter_y} theo địa phương"
    )
    fig_scatter.update_layout(
        xaxis_title=scatter_x,
        yaxis_title=scatter_y
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tabs[2]:
    st.header("📚 THỐNG KÊ GIÁO DỤC TRUNG HỌC CƠ SỞ")

    df_thcs = data["thcs"].copy()
    coords_df = pd.DataFrame(coords_data)
    df_thcs = df_thcs.merge(coords_df, on="Địa phương", how="left")
    df_thcs["Năm"] = pd.to_numeric(df_thcs["Năm"], errors="coerce")
    provinces = sorted(df_thcs["Địa phương"].dropna().unique())
    years = sorted(df_thcs["Năm"].dropna().unique())

    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("📅 Chọn năm học", years, index=len(years)-1, key="thcs_year")
    with col2:
        selected_province = st.selectbox("📍 Chọn địa phương", ["Tất cả"] + provinces, key="thcs_prov")

    df_filtered = df_thcs[df_thcs["Năm"] == selected_year]
    if selected_province != "Tất cả":
        df_filtered = df_filtered[df_filtered["Địa phương"] == selected_province]

    st.subheader("📊 Thống kê tổng quan")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("🏫 Trường", f'{df_filtered["Trường"].sum():,.0f}')
    kpi2.metric("📚 Lớp", f'{df_filtered["Lớp"].sum():,.0f}')
    kpi3.metric("👩‍🏫 Giáo viên", f'{df_filtered["Giáo viên"].sum():,.0f}')
    kpi4.metric("👦 Học sinh", f'{df_filtered["Học sinh"].sum():,.0f}')
    kpi5.metric("🧒 HS dân tộc thiểu số", f'{df_filtered["Học sinh dân tộc thiểu số"].sum():,.0f}')
    
    # ======= 3. Biểu đồ line theo năm (nếu chọn 1 tỉnh) =======
    if selected_province != "Tất cả":
        df_line = df_thcs[df_thcs["Địa phương"] == selected_province]
        st.subheader(f"📈 Biến động tại {selected_province} theo năm")

        color_map = {
            "Trường": "#e6c910",
            "Lớp": "#e69b10",
            "Giáo viên": "#d65875",
            "Học sinh": "#8088d1"
        }

        line_cols = st.columns(2)
        for i, column in enumerate(["Trường", "Lớp", "Giáo viên", "Học sinh"]):
            fig = px.line(
                df_line,
                x="Năm",
                y=column,
                markers=True,
                title=f"{column} qua các năm",
                color_discrete_sequence=[color_map[column]]
            )
            fig.update_layout(
                xaxis_title="Năm học",
                yaxis_title=column
            )
            with line_cols[i % 2]:
                st.plotly_chart(fig, use_container_width=True)

    # ======= 4. Biểu đồ bar ngang theo tỉnh =======
    if selected_province == "Tất cả":
        st.subheader("📌 So sánh giữa các địa phương")

        top_hs = df_filtered.sort_values("Học sinh", ascending=False).head(10)
        top_hs = top_hs.sort_values("Học sinh", ascending=True)
        top_hs["Địa phương"] = pd.Categorical(
            top_hs["Địa phương"], categories=top_hs["Địa phương"], ordered=True
        )
        fig_bar = px.bar(
            top_hs,
            y="Địa phương",
            x="Học sinh",
            orientation="h",
            title="🏆 Top 10 địa phương có số học sinh THCS cao nhất",
            color="Học sinh",
            color_continuous_scale="Blues"
        )
        fig_bar.update_layout(
            yaxis_title="Địa phương",
            xaxis_title="Số học sinh"
        )

        top_school = df_filtered.sort_values("Trường", ascending=False).head(10)
        top_school = top_school.sort_values("Trường", ascending=True)
        top_school["Địa phương"] = pd.Categorical(
            top_school["Địa phương"], categories=top_school["Địa phương"], ordered=True
        )
        fig_school_bar = px.bar(
            top_school,
            y="Địa phương",
            x="Trường",
            orientation="h",
            title="🏫 Top 10 địa phương có nhiều trường THCS nhất",
            color="Trường",
            color_continuous_scale="YlOrRd"
        )
        fig_school_bar.update_layout(
            yaxis_title="Địa phương",
            xaxis_title="Số trường"
        )

        col_bar1, col_bar2 = st.columns(2)
        with col_bar1:
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_bar2:
            st.plotly_chart(fig_school_bar, use_container_width=True)

    # ======= 5. Bản đồ Scatter Mapbox =======
    if "Lat" in df_filtered.columns and "Lon" in df_filtered.columns:
        st.subheader("📍 Phân bố theo địa phương")

        color_scale_students = [
            [0.0, "#a6cee3"],
            [0.2, "#66b2d6"],
            [0.5, "#1f78b4"],
            [1.0, "#08306b"]
        ]

        fig_map_students = px.scatter_mapbox(
            df_filtered,
            lat="Lat",
            lon="Lon",
            size="Học sinh",
            color="Học sinh",
            hover_name="Địa phương",
            size_max=30,
            zoom=4,
            mapbox_style="carto-positron",
            title="🗺️ Học sinh theo địa phương",
            color_continuous_scale=color_scale_students
        )

        fig_map_schools = px.scatter_mapbox(
            df_filtered,
            lat="Lat",
            lon="Lon",
            size="Trường",
            color="Trường",
            color_continuous_scale="YlOrRd",
            hover_name="Địa phương",
            size_max=20,
            zoom=4,
            mapbox_style="carto-positron",
            title="📏 Trường học theo địa phương"
        )

        col_map1, col_map2 = st.columns(2)
        with col_map1:
            st.plotly_chart(fig_map_students, use_container_width=True)
        with col_map2:
            st.plotly_chart(fig_map_schools, use_container_width=True)
            
    # ========== BIỂU ĐỒ TỈ LỆ GIỚI TÍNH HỌC SINH VÀ GIÁO VIÊN ==========
    st.subheader("👩‍🎓👨‍🎓 Tỉ lệ giới tính học sinh và giáo viên")
    gender_col1, gender_col2 = st.columns(2)

    with gender_col1:
        fig_students = px.pie(
            names=["Nam", "Nữ"],
            values=[
                df_filtered["Học sinh"].sum() - df_filtered["Học sinh nữ"].sum(),
                df_filtered["Học sinh nữ"].sum()
            ],
            hole=0.4,
            title="Tỉ lệ học sinh nam - nữ",
            color_discrete_sequence=["deepskyblue", "pink"]
        )
        st.plotly_chart(fig_students, use_container_width=True)

    with gender_col2:
        fig_teachers = px.pie(
            names=["Nam", "Nữ"],
            values=[
                df_filtered["Giáo viên"].sum() - df_filtered["Giáo viên nữ"].sum(),
                df_filtered["Giáo viên nữ"].sum()
            ],
            hole=0.4,
            title="Tỉ lệ giáo viên nam - nữ",
            color_discrete_sequence=["deepskyblue", "pink"]
        )
        st.plotly_chart(fig_teachers, use_container_width=True)

    st.subheader("📌 Mối tương quan giữa các chỉ số")
    available_vars = ["Trường", "Lớp", "Giáo viên", "Học sinh"]
    scatter_x = st.selectbox("📎 Chọn biến trục X", available_vars, index=1, key="thcs_x")
    scatter_y = st.selectbox("📎 Chọn biến trục Y", available_vars, index=3, key="thcs_y")

    fig_scatter = px.scatter(
        df_filtered,
        x=scatter_x,
        y=scatter_y,
        size=scatter_y,
        color="Địa phương",
        hover_name="Địa phương",
        title=f"🎯 Tương quan giữa {scatter_x} và {scatter_y} theo địa phương"
    )
    fig_scatter.update_layout(
        xaxis_title=scatter_x,
        yaxis_title=scatter_y
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


with tabs[3]:
    st.header("🎓 THỐNG KÊ GIÁO DỤC TRUNG HỌC PHỔ THÔNG")

    df_thpt = data["thpt"].copy()
    coords_df = pd.DataFrame(coords_data)
    df_thpt = df_thpt.merge(coords_df, on="Địa phương", how="left")
    df_thpt["Năm"] = pd.to_numeric(df_thpt["Năm"], errors="coerce")
    provinces = sorted(df_thpt["Địa phương"].dropna().unique())
    years = sorted(df_thpt["Năm"].dropna().unique())

    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("📅 Chọn năm học", years, index=len(years)-1, key="thpt_year")
    with col2:
        selected_province = st.selectbox("📍 Chọn địa phương", ["Tất cả"] + provinces, key="thpt_prov")

    df_filtered = df_thpt[df_thpt["Năm"] == selected_year]
    if selected_province != "Tất cả":
        df_filtered = df_filtered[df_filtered["Địa phương"] == selected_province]

    st.subheader("📊 Thống kê tổng quan")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("🏫 Trường", f'{df_filtered["Trường"].sum():,.0f}')
    kpi2.metric("📚 Lớp", f'{df_filtered["Lớp"].sum():,.0f}')
    kpi3.metric("👩‍🏫 Giáo viên", f'{df_filtered["Giáo viên"].sum():,.0f}')
    kpi4.metric("👦 Học sinh", f'{df_filtered["Học sinh"].sum():,.0f}')
    kpi5.metric("🧒 HS dân tộc thiểu số", f'{df_filtered["Học sinh dân tộc thiểu số"].sum():,.0f}')

    # ======= 3. Biểu đồ line theo năm (nếu chọn 1 tỉnh) =======
    if selected_province != "Tất cả":
        df_line = df_thpt[df_thpt["Địa phương"] == selected_province]
        st.subheader(f"📈 Biến động tại {selected_province} theo năm")

        color_map = {
            "Trường": "#e6c910",
            "Lớp": "#e69b10",
            "Giáo viên": "#d65875",
            "Học sinh": "#8088d1"
        }

        line_cols = st.columns(2)
        for i, column in enumerate(["Trường", "Lớp", "Giáo viên", "Học sinh"]):
            fig = px.line(
                df_line,
                x="Năm",
                y=column,
                markers=True,
                title=f"{column} qua các năm",
                color_discrete_sequence=[color_map[column]]
            )
            fig.update_layout(
                xaxis_title="Năm học",
                yaxis_title=column
            )
            with line_cols[i % 2]:
                st.plotly_chart(fig, use_container_width=True)

    # ======= 4. Biểu đồ bar ngang theo tỉnh =======
    if selected_province == "Tất cả":
        st.subheader("📌 So sánh giữa các địa phương")

        top_hs = df_filtered.sort_values("Học sinh", ascending=False).head(10)
        top_hs = top_hs.sort_values("Học sinh", ascending=True)
        top_hs["Địa phương"] = pd.Categorical(
            top_hs["Địa phương"], categories=top_hs["Địa phương"], ordered=True
        )
        fig_bar = px.bar(
            top_hs,
            y="Địa phương",
            x="Học sinh",
            orientation="h",
            title="🏆 Top 10 địa phương có số học sinh THPT cao nhất",
            color="Học sinh",
            color_continuous_scale="Blues"
        )
        fig_bar.update_layout(
            yaxis_title="Địa phương",
            xaxis_title="Số học sinh"
        )

        top_school = df_filtered.sort_values("Trường", ascending=False).head(10)
        top_school = top_school.sort_values("Trường", ascending=True)
        top_school["Địa phương"] = pd.Categorical(
            top_school["Địa phương"], categories=top_school["Địa phương"], ordered=True
        )
        fig_school_bar = px.bar(
            top_school,
            y="Địa phương",
            x="Trường",
            orientation="h",
            title="🏫 Top 10 địa phương có nhiều trường THPT nhất",
            color="Trường",
            color_continuous_scale="YlOrRd"
        )
        fig_school_bar.update_layout(
            yaxis_title="Địa phương",
            xaxis_title="Số trường"
        )

        col_bar1, col_bar2 = st.columns(2)
        with col_bar1:
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_bar2:
            st.plotly_chart(fig_school_bar, use_container_width=True)

    # ======= 5. Bản đồ Scatter Mapbox =======
    if "Lat" in df_filtered.columns and "Lon" in df_filtered.columns:
        st.subheader("📍 Phân bố theo địa phương")

        color_scale_students = [
            [0.0, "#a6cee3"],
            [0.2, "#66b2d6"],
            [0.5, "#1f78b4"],
            [1.0, "#08306b"]
        ]

        fig_map_students = px.scatter_mapbox(
            df_filtered,
            lat="Lat",
            lon="Lon",
            size="Học sinh",
            color="Học sinh",
            hover_name="Địa phương",
            size_max=30,
            zoom=4,
            mapbox_style="carto-positron",
            title="🗺️ Học sinh theo địa phương",
            color_continuous_scale=color_scale_students
        )

        fig_map_schools = px.scatter_mapbox(
            df_filtered,
            lat="Lat",
            lon="Lon",
            size="Trường",
            color="Trường",
            color_continuous_scale="YlOrRd",
            hover_name="Địa phương",
            size_max=20,
            zoom=4,
            mapbox_style="carto-positron",
            title="📏 Trường học theo địa phương"
        )

        col_map1, col_map2 = st.columns(2)
        with col_map1:
            st.plotly_chart(fig_map_students, use_container_width=True)
        with col_map2:
            st.plotly_chart(fig_map_schools, use_container_width=True)
            
    # ========== BIỂU ĐỒ TỈ LỆ GIỚI TÍNH HỌC SINH VÀ GIÁO VIÊN ==========
    st.subheader("👩‍🎓👨‍🎓 Tỉ lệ giới tính học sinh và giáo viên")
    gender_col1, gender_col2 = st.columns(2)

    with gender_col1:
        fig_students = px.pie(
            names=["Nam", "Nữ"],
            values=[
                df_filtered["Học sinh"].sum() - df_filtered["Học sinh nữ"].sum(),
                df_filtered["Học sinh nữ"].sum()
            ],
            hole=0.4,
            title="Tỉ lệ học sinh nam - nữ",
            color_discrete_sequence=["deepskyblue", "pink"]
        )
        st.plotly_chart(fig_students, use_container_width=True)

    with gender_col2:
        fig_teachers = px.pie(
            names=["Nam", "Nữ"],
            values=[
                df_filtered["Giáo viên"].sum() - df_filtered["Giáo viên nữ"].sum(),
                df_filtered["Giáo viên nữ"].sum()
            ],
            hole=0.4,
            title="Tỉ lệ giáo viên nam - nữ",
            color_discrete_sequence=["deepskyblue", "pink"]
        )
        st.plotly_chart(fig_teachers, use_container_width=True)

    st.subheader("📌 Mối tương quan giữa các chỉ số")
    available_vars = ["Trường", "Lớp", "Giáo viên", "Học sinh"]
    scatter_x = st.selectbox("📎 Chọn biến trục X", available_vars, index=1, key="thpt_x")
    scatter_y = st.selectbox("📎 Chọn biến trục Y", available_vars, index=3, key="thpt_y")

    fig_scatter = px.scatter(
        df_filtered,
        x=scatter_x,
        y=scatter_y,
        size=scatter_y,
        color="Địa phương",
        hover_name="Địa phương",
        title=f"🎯 Tương quan giữa {scatter_x} và {scatter_y} theo địa phương"
    )
    fig_scatter.update_layout(
        xaxis_title=scatter_x,
        yaxis_title=scatter_y
    )
    st.plotly_chart(fig_scatter, use_container_width=True)  
    
with tabs[4]:
    st.header("👶 THỐNG KÊ GIÁO DỤC MẪU GIÁO")

    df_mg = data["mau_giao"].copy()
    df_mg_tq = data["mau_giao_tq"].copy()
    coords_df = pd.DataFrame(coords_data)
    df_mg = df_mg.merge(coords_df, on="Địa phương", how="left")
    df_mg["Năm"] = pd.to_numeric(df_mg["Năm"], errors="coerce")

    provinces = sorted(df_mg["Địa phương"].dropna().unique())
    years = sorted(df_mg["Năm"].dropna().unique())

    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("📅 Chọn năm học", years, index=len(years)-1)
    with col2:
        selected_province = st.selectbox("📍 Chọn địa phương", ["Tất cả"] + provinces)

    df_filtered = df_mg[df_mg["Năm"] == selected_year]
    if selected_province != "Tất cả":
        df_filtered = df_filtered[df_filtered["Địa phương"] == selected_province]

    # KPIs
    st.subheader("📊 Thống kê tổng quan")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("🏫 Trường", f'{df_filtered["Trường học"].sum():,.0f}')
    kpi2.metric("📚 Lớp", f'{df_filtered["Lớp học"].sum():,.0f}')
    kpi3.metric("👩‍🏫 Giáo viên", f'{df_filtered["Giáo viên"].sum():,.0f}')
    kpi4.metric("🧒 Học sinh", f'{df_filtered["Học sinh"].sum():,.0f}')

    # Line Chart: học sinh & giáo viên theo năm (tách thành 2 biểu đồ)
    st.subheader("📈 Số lượng học sinh và giáo viên qua các năm")
    df_mg_tq["Năm"] = pd.to_numeric(df_mg_tq["Năm"], errors="coerce")
    df_mg_tq = df_mg_tq.sort_values("Năm")

    col_line1, col_line2 = st.columns(2)

    with col_line1:
        fig_student = px.line(
            df_mg_tq, x="Năm", y="Học sinh",
            title="👶 Số lượng học sinh mẫu giáo qua các năm",
            markers=True,
            labels={"Học sinh": "Học sinh (nghìn)", "Năm": "Năm"},
            color_discrete_sequence=["#1f78b4"]
        )
        st.plotly_chart(fig_student, use_container_width=True)

    with col_line2:
        fig_teacher = px.line(
            df_mg_tq, x="Năm", y="Giáo viên",
            title="👩‍🏫 Số lượng giáo viên mẫu giáo qua các năm",
            markers=True,
            labels={"Giáo viên": "Giáo viên (nghìn)", "Năm": "Năm"},
            color_discrete_sequence=["#e6c910"]
        )
        st.plotly_chart(fig_teacher, use_container_width=True)

    # TreeMap
    st.subheader("🏆 Các địa phương có nhiều học sinh và trường mẫu giáo nhất")
    col_treemap1, col_treemap2 = st.columns(2)

    # Treemap học sinh
    with col_treemap1:
        df_top_students = df_filtered.sort_values("Học sinh", ascending=False).head(15)
        fig_tree_students = px.treemap(
            df_top_students,
            path=["Địa phương"],
            values="Học sinh",
            title="👶 Top 15 địa phương có nhiều học sinh mẫu giáo nhất"
        )
        fig_tree_students.update_traces(textinfo="label+value")
        st.plotly_chart(fig_tree_students, use_container_width=True)

    # Treemap trường
    with col_treemap2:
        df_top_schools = df_filtered.sort_values("Trường học", ascending=False).head(15)
        fig_tree_schools = px.treemap(
            df_top_schools,
            path=["Địa phương"],
            values="Trường học",
            title="🏫 Top 15 địa phương có nhiều trường mẫu giáo nhất"
        )
        fig_tree_schools.update_traces(textinfo="label+value")
        st.plotly_chart(fig_tree_schools, use_container_width=True)

    # Bản đồ
    st.subheader("🗺️ Phân bố theo địa phương")
    col_map1, col_map2 = st.columns(2)
    with col_map1:
        fig_map_students = px.scatter_mapbox(
            df_filtered, lat="Lat", lon="Lon", size="Học sinh", color="Học sinh",
            hover_name="Địa phương", zoom=4, mapbox_style="carto-positron",
            title="🧒 Số học sinh theo địa phương",
            color_continuous_scale="Blues", size_max=30
        )
        st.plotly_chart(fig_map_students, use_container_width=True)
    with col_map2:
        fig_map_schools = px.scatter_mapbox(
            df_filtered, lat="Lat", lon="Lon", size="Trường học", color="Trường học",
            hover_name="Địa phương", zoom=4, mapbox_style="carto-positron",
            title="🏫 Số trường theo địa phương",
            color_continuous_scale="YlOrRd", size_max=30
        )
        st.plotly_chart(fig_map_schools, use_container_width=True)

    # Heatmap phát triển
    st.subheader("🔥 Chỉ số phát triển theo năm")

    # Chọn cột và đổi tên ngắn gọn
    df_pct = df_mg_tq[[
        "Năm",
        "Chỉ số phát triển (%) - Trường học",
        "Chỉ số phát triển (%) - Lớp học",
        "Chỉ số phát triển (%) - Giáo viên",
        "Chỉ số phát triển (%) - Học sinh",
        "Chỉ số phát triển (%) - Số học sinh bình quân một giáo viên",
        "Chỉ số phát triển (%) - Số học sinh bình quân một lớp học"
    ]].rename(columns={
        "Chỉ số phát triển (%) - Trường học": "Trường",
        "Chỉ số phát triển (%) - Lớp học": "Lớp",
        "Chỉ số phát triển (%) - Giáo viên": "Giáo viên",
        "Chỉ số phát triển (%) - Học sinh": "Học sinh",
        "Chỉ số phát triển (%) - Số học sinh bình quân một giáo viên": "HS/GV",
        "Chỉ số phát triển (%) - Số học sinh bình quân một lớp học": "HS/Lớp"
    })

    # Tính phần trăm thay đổi so với năm trước
    df_pct_change = df_pct.set_index("Năm").pct_change().dropna() * 100
    df_pct_change = df_pct_change.round(1)

    # Chuẩn bị dữ liệu cho heatmap
    z = df_pct_change.values
    text_matrix = df_pct_change.astype(str) + "%"

    fig_matrix = ff.create_annotated_heatmap(
        z=z,
        x=df_pct_change.columns.tolist(),
        y=df_pct_change.index.astype(str).tolist(),
        annotation_text=text_matrix.values,
        showscale=True,
        colorscale=[[0, "red"], [0.5, "white"], [1, "green"]]
    )

    fig_matrix.update_layout(title="📉 Biến động (%) so với năm trước")

    st.plotly_chart(fig_matrix, use_container_width=True)

    # Scatter chart tương quan
    st.subheader("📌 Mối tương quan giữa các chỉ số")
    options = ["Trường học", "Lớp học", "Giáo viên", "Học sinh"]
    x_var = st.selectbox("Biến trục X", options, index=0)
    y_var = st.selectbox("Biến trục Y", options, index=3)
    fig_scatter = px.scatter(
        df_filtered, x=x_var, y=y_var, color="Địa phương", size=y_var,
        hover_name="Địa phương", title=f"Tương quan giữa {x_var} và {y_var}"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
