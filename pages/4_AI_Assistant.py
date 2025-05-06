from time import sleep
import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types
import numpy as np
import os
import json
import base64  # thêm

st.set_page_config(page_title="Trợ lý AI", layout="wide")

st.title("🤖 Trợ lý AI")
st.write("### 📌 Hỏi AI về dữ liệu giáo dục Việt Nam")


# --- Filter Helper Function ---
def apply_filters(df: pd.DataFrame, filters_json: str) -> tuple[pd.DataFrame, str]:
    """
    Applies filters specified in a JSON string to the DataFrame.
    Returns the filtered DataFrame and a string describing the applied filters.
    """
    if (
        not filters_json
        or filters_json.strip() == "{}"
        or filters_json.lower() == "none"
    ):
        return df, ""  # Return original df and empty filter string

    try:
        filters = json.loads(filters_json)
        if not isinstance(filters, dict):
            st.warning(
                "Bộ lọc JSON không hợp lệ (không phải là dictionary). Bỏ qua bộ lọc.",
                icon="⚠️",
            )
            return df, ""

        filtered_df = df.copy()
        applied_filters_list = []
        for column, criteria in filters.items():
            if column not in filtered_df.columns:
                st.warning(
                    f"Cột lọc '{column}' không tồn tại trong bộ dữ liệu. Bỏ qua bộ lọc này.",
                    icon="⚠️",
                )
                continue

            try:
                original_count = len(filtered_df)
                filter_desc = ""
                if isinstance(criteria, list):
                    filtered_df = filtered_df[filtered_df[column].isin(criteria)]
                    filter_desc = f"{column} trong {criteria}"
                else:  # Assume single value equality
                    filtered_df = filtered_df[filtered_df[column] == criteria]
                    filter_desc = f"{column} == '{criteria}'"

                if len(filtered_df) < original_count:
                    applied_filters_list.append(filter_desc)

                if filtered_df.empty:
                    st.warning(
                        f"Không còn dữ liệu sau khi áp dụng bộ lọc: {filter_desc}. Kiểm tra lại tiêu chí lọc.",
                        icon="⚠️",
                    )
                    break  # Stop applying further filters if data is empty

            except Exception as filter_e:
                st.warning(
                    f"Lỗi khi áp dụng bộ lọc cho cột '{column}' với tiêu chí '{criteria}': {filter_e}. Bỏ qua bộ lọc này.",
                    icon="⚠️",
                )

        applied_filters_str = ""
        if applied_filters_list:
            applied_filters_str = " (Lọc theo: " + "; ".join(applied_filters_list) + ")"
            st.info(f"Đã áp dụng bộ lọc: {'; '.join(applied_filters_list)}.")

        return filtered_df, applied_filters_str

    except json.JSONDecodeError:
        st.warning(
            f"Chuỗi JSON bộ lọc không hợp lệ: '{filters_json}'. Bỏ qua bộ lọc.",
            icon="⚠️",
        )
        return df, ""
    except Exception as e:
        st.error(f"Lỗi không mong muốn khi áp dụng bộ lọc: {e}", icon="⚠️")
        return df, ""


# --- Chart Generation Functions (Modified) ---


def safe_get_column(df, column_name, dtype=None):
    """Safely get a column, checking existence and optionally type."""
    if column_name not in df.columns:
        st.error(f"Lỗi: Cột '{column_name}' không tìm thấy trong bộ dữ liệu.", icon="⚠️")
        return None
    col = df[column_name]
    if dtype:
        if dtype == "numeric" and not pd.api.types.is_numeric_dtype(col):
            st.error(f"Lỗi: Cột '{column_name}' không phải là số.", icon="⚠️")
            return None
        if (
            dtype == "categorical"
            and not pd.api.types.is_object_dtype(col)
            and not pd.api.types.is_categorical_dtype(col)
        ):
            st.warning(
                f"Cảnh báo: Cột '{column_name}' có thể không lý tưởng cho phân tích danh mục.",
                icon="⚠️",
            )
        if dtype == "datetime":
            if not pd.api.types.is_datetime64_any_dtype(col):
                try:
                    col = pd.to_datetime(col)
                except Exception:
                    st.error(
                        f"Lỗi: Không thể chuyển đổi cột '{column_name}' sang định dạng ngày giờ.",
                        icon="⚠️",
                    )
                    return None
    return col


def generate_histogram(
    df: pd.DataFrame, column_name: str, num_bins: int = 30, filters_json: str = None
):
    """Generates a histogram for a numeric column after applying filters."""
    df_filtered, filter_desc = apply_filters(df, filters_json)
    if df_filtered.empty:
        st.warning("Không có dữ liệu để vẽ biểu đồ sau khi lọc.")
        return None

    data_col = safe_get_column(df_filtered, column_name, dtype="numeric")
    if data_col is None:
        return None
    try:
        fig = px.histogram(
            df_filtered,
            x=column_name,
            nbins=int(num_bins),
            title=f"Phân phối của {column_name}{filter_desc}",
            template="plotly_white",
        )
        fig.update_layout(bargap=0.1)
        return fig
    except Exception as e:
        st.error(f"Lỗi tạo biểu đồ tần suất cho {column_name}: {e}", icon="⚠️")
        return None


def generate_bar_chart(
    df: pd.DataFrame, column_name: str, top_n: int = 10, filters_json: str = None
):
    """Generates a bar chart for a categorical column after applying filters."""
    df_filtered, filter_desc = apply_filters(df, filters_json)
    if df_filtered.empty:
        st.warning("Không có dữ liệu để vẽ biểu đồ sau khi lọc.")
        return None

    data_col = safe_get_column(df_filtered, column_name, dtype="categorical")
    if data_col is None:
        st.warning(
            f"Cột '{column_name}' có thể không phải là danh mục. Đang thử tạo biểu đồ cột.",
            icon="⚠️",
        )
    try:
        top_n = int(top_n)
        counts = df_filtered[column_name].value_counts().nlargest(top_n).reset_index()
        counts.columns = [column_name, "count"]
        fig = px.bar(
            counts,
            x=column_name,
            y="count",
            title=f"{top_n} Danh mục hàng đầu trong {column_name}{filter_desc}",
            template="plotly_white",
            text="count",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title=column_name, yaxis_title="Số lượng")
        return fig
    except Exception as e:
        st.error(f"Lỗi tạo biểu đồ cột cho {column_name}: {e}", icon="⚠️")
        return None


def generate_pie_chart(
    df: pd.DataFrame, column_name: str, top_n: int = 5, filters_json: str = None
):
    """Generates a pie chart for a categorical column after applying filters."""
    df_filtered, filter_desc = apply_filters(df, filters_json)
    if df_filtered.empty:
        st.warning("Không có dữ liệu để vẽ biểu đồ sau khi lọc.")
        return None

    data_col = safe_get_column(df_filtered, column_name, dtype="categorical")
    if data_col is None:
        st.warning(
            f"Cột '{column_name}' có thể không phải là danh mục. Đang thử tạo biểu đồ tròn.",
            icon="⚠️",
        )
    try:
        top_n = int(top_n)
        counts = df_filtered[column_name].value_counts().reset_index()
        counts.columns = [column_name, "count"]

        if len(counts) > top_n:
            top_df = counts.nlargest(top_n - 1, "count")
            other_sum = counts.nsmallest(len(counts) - (top_n - 1), "count")[
                "count"
            ].sum()
            if other_sum > 0:
                other_row = pd.DataFrame({column_name: ["Khác"], "count": [other_sum]})
                pie_df = pd.concat([top_df, other_row], ignore_index=True)
            else:
                pie_df = top_df
        else:
            pie_df = counts

        fig = px.pie(
            pie_df,
            names=column_name,
            values="count",
            title=f"Tỷ lệ {top_n} Danh mục hàng đầu trong {column_name}{filter_desc}",
            template="plotly_white",
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        return fig
    except Exception as e:
        st.error(f"Lỗi tạo biểu đồ tròn cho {column_name}: {e}", icon="⚠️")
        return None


def generate_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    aggregation: str = "sum",
    group_by_column: str = None,
    filters_json: str = None,
):
    """
    Generates a line chart after applying filters. Handles aggregation/grouping.
    """
    df_filtered, filter_desc = apply_filters(df, filters_json)
    if df_filtered.empty:
        st.warning("Không có dữ liệu để vẽ biểu đồ sau khi lọc.")
        return None

    x_data = safe_get_column(df_filtered, x_column)
    y_data = safe_get_column(df_filtered, y_column, dtype="numeric")
    group_data = None
    if group_by_column and group_by_column != "None" and group_by_column.strip() != "":
        group_data = safe_get_column(df_filtered, group_by_column)
        if group_data is None:
            st.warning(
                f"Cột nhóm '{group_by_column}' không hợp lệ. Sẽ bỏ qua việc nhóm.",
                icon="⚠️",
            )
            group_by_column = None  # Reset if invalid
    else:
        group_by_column = None  # Ensure it's None if empty or "None"

    if x_data is None or y_data is None:
        return None

    try:
        cols_to_use = [x_column, y_column]
        if group_by_column:
            cols_to_use.append(group_by_column)

        df_line = df_filtered[cols_to_use].copy()

        if not pd.api.types.is_numeric_dtype(
            df_line[x_column]
        ) and not pd.api.types.is_datetime64_any_dtype(df_line[x_column]):
            try:
                df_line[x_column] = pd.to_datetime(df_line[x_column])
                st.info(
                    f"Đã chuyển đổi cột '{x_column}' sang ngày giờ cho biểu đồ đường."
                )
            except Exception:
                st.warning(
                    f"Không thể chuyển đổi trục X '{x_column}' sang Ngày/Giờ. Giữ nguyên.",
                    icon="⚠️",
                )

        df_line = df_line.dropna(subset=[x_column, y_column])

        plot_title = f"Xu hướng của {y_column} theo {x_column}"
        plot_args = {
            "x": x_column,
            "y": y_column,
            "template": "plotly_white",
            "markers": True,
        }

        if group_by_column:
            df_line = df_line.sort_values(by=[group_by_column, x_column])
            plot_args["color"] = group_by_column
            plot_title += f" (Nhóm theo {group_by_column})"
            plot_data = df_line
        else:
            if df_line[x_column].duplicated().any():
                valid_aggregations = {
                    "sum": "Tổng",
                    "mean": "Trung bình",
                    "median": "Trung vị",
                }
                agg_func = aggregation.lower() if aggregation else "sum"
                if agg_func not in valid_aggregations:
                    st.warning(
                        f"Phương thức tổng hợp '{aggregation}' không hợp lệ. Sử dụng 'sum'.",
                        icon="⚠️",
                    )
                    agg_func = "sum"

                agg_label = valid_aggregations[agg_func]
                st.info(
                    f"Trục X ('{x_column}') có giá trị trùng lặp. Đang tổng hợp '{y_column}' theo '{agg_label}'."
                )
                df_agg = df_line.groupby(x_column, as_index=False).agg(
                    {y_column: agg_func}
                )
                df_agg = df_agg.sort_values(by=x_column)
                plot_title = f"Xu hướng {agg_label} của {y_column} theo {x_column}"
                plot_data = df_agg
            else:
                df_line = df_line.sort_values(by=x_column)
                plot_data = df_line

        if not plot_data.empty:
            plot_args["title"] = plot_title + filter_desc
            fig = px.line(plot_data, **plot_args)
            fig.update_layout(xaxis_title=x_column, yaxis_title=y_column)
            return fig
        else:
            st.warning(
                f"Không tìm thấy điểm dữ liệu hợp lệ cho Biểu đồ đường ({y_column} vs {x_column}).",
                icon="⚠️",
            )
            return None

    except Exception as e:
        st.error(f"Lỗi tạo biểu đồ đường ({y_column} vs {x_column}): {e}", icon="⚠️")
        return None


def generate_scatter_plot(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: str = None,
    filters_json: str = None,
):
    """Generates a scatter plot after applying filters."""
    df_filtered, filter_desc = apply_filters(df, filters_json)
    if df_filtered.empty:
        st.warning("Không có dữ liệu để vẽ biểu đồ sau khi lọc.")
        return None

    x_data = safe_get_column(df_filtered, x_column, dtype="numeric")
    y_data = safe_get_column(df_filtered, y_column, dtype="numeric")
    color_data = None
    if color_column and color_column != "None" and color_column.strip() != "":
        color_data = safe_get_column(df_filtered, color_column)
        if color_data is None:
            st.warning(
                f"Cột màu '{color_column}' không tìm thấy hoặc không hợp lệ. Biểu đồ phân tán sẽ không được tô màu.",
                icon="⚠️",
            )
            color_column = None
    else:
        color_column = None
    if x_data is None or y_data is None:
        return None
    try:
        plot_args = {
            "x": x_column,
            "y": y_column,
            "title": f"{y_column} vs {x_column}{filter_desc}",
            "template": "plotly_white",
        }
        if color_column:
            plot_args["color"] = color_column
            plot_args["title"] += f" (Tô màu theo {color_column})"

        sample_size = min(2000, df_filtered.shape[0])
        df_sample = (
            df_filtered.sample(sample_size)
            if df_filtered.shape[0] > 2000
            else df_filtered
        )

        fig = px.scatter(df_sample, **plot_args)
        return fig
    except Exception as e:
        st.error(f"Lỗi tạo biểu đồ phân tán ({y_column} vs {x_column}): {e}", icon="⚠️")
        return None


# --- Mapping function names to functions ---
AVAILABLE_FUNCTIONS = {
    "generate_histogram": generate_histogram,
    "generate_bar_chart": generate_bar_chart,
    "generate_pie_chart": generate_pie_chart,
    "generate_line_chart": generate_line_chart,
    "generate_scatter_plot": generate_scatter_plot,
}

# --- Define Tools for Gemini (Add filters_json parameter) ---
tools = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="generate_histogram",
            description="Tạo biểu đồ tần suất cho một cột số được chỉ định trong một bộ dữ liệu cụ thể, có thể lọc trước.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "dataframe_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên của bộ dữ liệu cần sử dụng (ví dụ: 'Địa phương - Tiểu học').",
                    ),
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên cột số.",
                    ),
                    "num_bins": types.Schema(
                        type=types.Type.INTEGER,
                        description="Số lượng khoảng (mặc định 30).",
                        default=30,
                    ),
                    "filters_json": types.Schema(
                        type=types.Type.STRING,
                        description='Chuỗi JSON tùy chọn để lọc dữ liệu trước khi vẽ. Ví dụ: \'{"Địa phương": "Hà Nội", "Năm": [2020, 2021]}\'.',
                        nullable=True,
                        default=None,
                    ),
                },
                required=["dataframe_name", "column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_bar_chart",
            description="Tạo biểu đồ cột cho một cột danh mục được chỉ định trong một bộ dữ liệu cụ thể, có thể lọc trước.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "dataframe_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên của bộ dữ liệu cần sử dụng.",
                    ),
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên cột danh mục.",
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Số lượng danh mục hàng đầu cần hiển thị (mặc định 10).",
                        default=10,
                    ),
                    "filters_json": types.Schema(
                        type=types.Type.STRING,
                        description='Chuỗi JSON tùy chọn để lọc dữ liệu trước khi vẽ. Ví dụ: \'{"Loại trường": "Công lập"}\'.',
                        nullable=True,
                        default=None,
                    ),
                },
                required=["dataframe_name", "column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_pie_chart",
            description="Tạo biểu đồ tròn cho một cột danh mục được chỉ định trong một bộ dữ liệu cụ thể, có thể lọc trước.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "dataframe_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên của bộ dữ liệu cần sử dụng.",
                    ),
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên cột danh mục.",
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Số lượng lát cắt (nhóm các mục khác, mặc định 5).",
                        default=5,
                    ),
                    "filters_json": types.Schema(
                        type=types.Type.STRING,
                        description="Chuỗi JSON tùy chọn để lọc dữ liệu trước khi vẽ. Ví dụ: '{\"Năm\": 2022}'.",
                        nullable=True,
                        default=None,
                    ),
                },
                required=["dataframe_name", "column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_line_chart",
            description="Tạo biểu đồ đường để hiển thị xu hướng, có thể lọc trước. Xử lý tổng hợp/nhóm nếu cần.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "dataframe_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên của bộ dữ liệu cần sử dụng.",
                    ),
                    "x_column": types.Schema(
                        type=types.Type.STRING,
                        description="Cột cho trục X (thời gian hoặc chuỗi).",
                    ),
                    "y_column": types.Schema(
                        type=types.Type.STRING,
                        description="Cột số cho trục Y.",
                    ),
                    "aggregation": types.Schema(
                        type=types.Type.STRING,
                        description="Phương thức tổng hợp Y nếu X trùng lặp (ví dụ: 'sum', 'mean', 'median'). Mặc định là 'sum'. Bỏ qua nếu group_by_column được sử dụng.",
                        nullable=True,
                        default="sum",
                    ),
                    "group_by_column": types.Schema(
                        type=types.Type.STRING,
                        description="Cột danh mục tùy chọn để nhóm dữ liệu và vẽ nhiều đường riêng biệt.",
                        nullable=True,
                        default=None,
                    ),
                    "filters_json": types.Schema(
                        type=types.Type.STRING,
                        description='Chuỗi JSON tùy chọn để lọc dữ liệu trước khi vẽ. Ví dụ: \'{"Địa phương": ["Hà Nội", "TP. Hồ Chí Minh"]}\'.',
                        nullable=True,
                        default=None,
                    ),
                },
                required=["dataframe_name", "x_column", "y_column"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_scatter_plot",
            description="Tạo biểu đồ phân tán để hiển thị mối quan hệ giữa hai cột số, có thể lọc trước.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "dataframe_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên của bộ dữ liệu cần sử dụng.",
                    ),
                    "x_column": types.Schema(
                        type=types.Type.STRING,
                        description="Cột số cho trục X.",
                    ),
                    "y_column": types.Schema(
                        type=types.Type.STRING,
                        description="Cột số cho trục Y.",
                    ),
                    "color_column": types.Schema(
                        type=types.Type.STRING,
                        description="Cột danh mục hoặc số tùy chọn để tô màu các điểm.",
                        nullable=True,
                        default=None,
                    ),
                    "filters_json": types.Schema(
                        type=types.Type.STRING,
                        description="Chuỗi JSON tùy chọn để lọc dữ liệu trước khi vẽ. Ví dụ: '{\"Năm\": 2021}'.",
                        nullable=True,
                        default=None,
                    ),
                },
                required=["dataframe_name", "x_column", "y_column"],
            ),
        ),
    ]
)


# --- Configure Gemini AI ---
client = None
config = None
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("🚨 Biến môi trường GEMINI_API_KEY chưa được đặt!")
        st.stop()
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Lỗi cấu hình Gemini AI: {e}")
    st.warning(
        "Vui lòng đảm bảo khóa API được đặt chính xác và bạn có các gói cần thiết."
    )
    client = None

# Initialize session memory
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# --- Load DataFrames ---
DATA_DIR = "data"
flat_dfs = {}
datasets_overview = "Tổng quan về các bộ dữ liệu có sẵn:\n\n"

# --- Descriptions for each dataset ---
dataset_descriptions = {
    "Địa phương - Tiểu học": "Dữ liệu chi tiết về giáo dục tiểu học theo từng địa phương (tỉnh/thành phố).",
    "Địa phương - Trung học cơ sở": "Dữ liệu chi tiết về giáo dục trung học cơ sở theo từng địa phương (tỉnh/thành phố).",
    "Địa phương - Trung học phổ thông": "Dữ liệu chi tiết về giáo dục trung học phổ thông theo từng địa phương (tỉnh/thành phố).",
    "Mẫu giáo - Địa phương": "Dữ liệu chi tiết về giáo dục mẫu giáo theo từng địa phương (tỉnh/thành phố).",
    "Mẫu giáo - Tổng quan Mẫu giáo": "Dữ liệu tổng quan chung về tình hình giáo dục mẫu giáo trên cả nước.",
    "Tổng quan - Chỉ số phát triển": "Các chỉ số phát triển giáo dục tổng hợp qua các năm.",
    "Tổng quan - Tổng quan": "Dữ liệu tổng quan chung về giáo dục Việt Nam qua các năm (có thể bao gồm nhiều cấp học).",
    "Tổng quan - Tổng quan (tất cả)": "Bộ dữ liệu tổng hợp nhất, chứa thông tin tổng quan về tất cả các cấp học qua các năm.",
}

try:
    dfs = {
        "Địa phương": {
            "Tiểu học": pd.read_csv(os.path.join(DATA_DIR, "dia-phuong/tieu-hoc.csv")),
            "Trung học cơ sở": pd.read_csv(
                os.path.join(DATA_DIR, "dia-phuong/THCS.csv")
            ),
            "Trung học phổ thông": pd.read_csv(
                os.path.join(DATA_DIR, "dia-phuong/THPT.csv")
            ),
        },
        "Mẫu giáo": {
            "Địa phương": pd.read_csv(os.path.join(DATA_DIR, "mau-giao/MG.csv")),
            "Tổng quan Mẫu giáo": pd.read_csv(
                os.path.join(DATA_DIR, "mau-giao/tong-quan-MG.csv")
            ),
        },
        "Tổng quan": {
            "Chỉ số phát triển": pd.read_csv(
                os.path.join(DATA_DIR, "tong-quan/chi-so-phat-trien.csv")
            ),
            "Tổng quan": pd.read_csv(os.path.join(DATA_DIR, "tong-quan/tong-quan.csv")),
            "Tổng quan (tất cả)": pd.read_csv(
                os.path.join(DATA_DIR, "tong-quan/tong-quan-all.csv")
            ),
        },
    }
    for category, sub_dfs in dfs.items():
        for name, df in sub_dfs.items():
            full_name = f"{category} - {name}"
            flat_dfs[full_name] = df
            description = dataset_descriptions.get(full_name, "Không có mô tả.")
            # Get column types
            try:
                col_types = df.dtypes.apply(lambda x: str(x)).to_dict()
                col_types_str = "\n".join(
                    [f"    '{k}': {v}" for k, v in col_types.items()]
                )
            except Exception:
                col_types_str = "Không thể lấy kiểu dữ liệu cột."
            # Get first 5 rows
            try:
                f5r = df.head().to_string()
            except Exception:
                f5r = "Không thể lấy 5 hàng đầu tiên."

            datasets_overview += f"- Tên: '{full_name}'\n"
            datasets_overview += f"  Mô tả: {description}\n"
            datasets_overview += f"  Cột và Kiểu dữ liệu:\n{col_types_str}\n"
            datasets_overview += f"  5 hàng đầu tiên (f5r):\n{f5r}\n\n"

except FileNotFoundError as e:
    st.error(
        f"🚨 Lỗi tải tệp dữ liệu: {e}. Vui lòng đảm bảo các tệp dữ liệu có mặt tại đường dẫn dự kiến bắt đầu từ '{DATA_DIR}'."
    )
    st.stop()
except Exception as e:
    st.error(f"🚨 Đã xảy ra lỗi không mong muốn khi tải dữ liệu: {e}")
    st.stop()

# --- Chart Analysis System Prompt ---
CHART_ANALYSIS_PROMPT = """
Bạn là một trợ lý AI chuyên phân tích biểu đồ. Dưới đây là thông tin biểu đồ:
- Hàm đã gọi: {function_name}
- Tham số: {function_args}
Bạn sẽ nhận biểu đồ dưới dạng hình ảnh PNG base64.
Hãy phân tích biểu đồ này, nêu ra các xu hướng, bất thường, và gợi ý ý nghĩa của nó.
**Trả lời bằng tiếng Việt.**

- Biểu đồ được sinh = ai với system prompt như sau, bạn hãy tham khảo để hiểu hơn về dataset:
```
{system_prompt}
```
"""

# --- Main AI Interaction Area ---
if client and flat_dfs:
    st.success(f"Sẵn sàng nhận câu hỏi về {len(flat_dfs)} bộ dữ liệu giáo dục.")

    st.write("---")
    st.subheader("💬 Hỏi AI về dữ liệu")
    st.caption(
        "Ví dụ: 'Tạo biểu đồ tần suất cho cột [tên cột] trong dữ liệu [tên bộ dữ liệu]', 'So sánh [cột 1] và [cột 2] từ [tên bộ dữ liệu]', 'Dữ liệu nào nói về chỉ số phát triển?'"
    )

    # --- List of Provinces ---
    provinces = [
        "An Giang",
        "Bà Rịa - Vũng Tàu",
        "Bắc Giang",
        "Bắc Kạn",
        "Bạc Liêu",
        "Bắc Ninh",
        "Bến Tre",
        "Bình Định",
        "Bình Dương",
        "Bình Phước",
        "Bình Thuận",
        "Cà Mau",
        "Cần Thơ",
        "Cao Bằng",
        "Đà Nẵng",
        "Đắk Lắk",
        "Đắk Nông",
        "Điện Biên",
        "Đồng Nai",
        "Đồng Tháp",
        "Gia Lai",
        "Hà Giang",
        "Hà Nam",
        "Hà Nội",
        "Hà Tĩnh",
        "Hải Dương",
        "Hải Phòng",
        "Hậu Giang",
        "Hòa Bình",
        "Hưng Yên",
        "Khánh Hòa",
        "Kiên Giang",
        "Kon Tum",
        "Lai Châu",
        "Lâm Đồng",
        "Lạng Sơn",
        "Lào Cai",
        "Long An",
        "Nam Định",
        "Nghệ An",
        "Ninh Bình",
        "Ninh Thuận",
        "Phú Thọ",
        "Phú Yên",
        "Quảng Bình",
        "Quảng Nam",
        "Quảng Ngãi",
        "Quảng Ninh",
        "Quảng Trị",
        "Sóc Trăng",
        "Sơn La",
        "Tây Ninh",
        "Thái Bình",
        "Thái Nguyên",
        "Thanh Hóa",
        "Thừa Thiên Huế",
        "Tiền Giang",
        "Trà Vinh",
        "Tuyên Quang",
        "Vĩnh Long",
        "Vĩnh Phúc",
        "Yên Bái",
        "TP.Hồ Chí Minh",
    ]
    provinces_list_str = (
        "Danh sách các giá trị 'Địa phương' có thể có (tỉnh/thành phố):\n"
        + ", ".join([f"'{p}'" for p in provinces])
        + "\n"
    )
    # --- End List of Provinces ---

    SYSTEM_PROMPT = f"""
Đây là mô tả ứng dụng của tôi:
"Graphora là một nền tảng trực quan hóa dữ liệu giáo dục được thiết kế nhằm phục vụ cho mục tiêu **phân tích và đánh giá toàn diện tình hình giáo dục tại Việt Nam"    
Bạn là một trợ lý AI cho ứng dụng này, chuyên phân tích các bộ dữ liệu CSV được cung cấp về giáo dục Việt Nam.
Mục tiêu của bạn là giúp người dùng hiểu dữ liệu của họ bằng cách trả lời các câu hỏi và tạo các trực quan hóa liên quan bằng các công cụ có sẵn.
**Hãy trả lời bằng tiếng Việt.**

{datasets_overview}
{provinces_list_str}
Hướng dẫn:
- Phân tích yêu cầu của người dùng một cách cẩn thận.
- **Xác định bộ dữ liệu (dataframe) phù hợp nhất** từ danh sách trên dựa trên câu hỏi, mô tả, danh sách cột, kiểu dữ liệu và dữ liệu mẫu (f5r) của từng bộ dữ liệu. Nếu không rõ ràng, hãy hỏi người dùng muốn sử dụng bộ dữ liệu nào.
- **Lọc dữ liệu (Filtering):** Nếu người dùng yêu cầu phân tích hoặc trực quan hóa chỉ một phần dữ liệu (ví dụ: 'chỉ ở Hà Nội', 'cho năm 2022', 'chỉ các trường công lập'), hãy sử dụng tham số `filters_json`. Tham số này nhận một chuỗi JSON.
    - Định dạng JSON: `'{{"tên_cột_1": "giá_trị", "tên_cột_2": ["giá_trị_1", "giá_trị_2"]}}'`
    - Ví dụ: Để lọc dữ liệu 'Địa phương - Tiểu học' chỉ cho 'Hà Nội' năm 2021, dùng: `filters_json='{{"Địa phương": "Hà Nội", "Năm": 2021}}'`
    - Ví dụ: Để lọc cho 'Hà Nội' và 'TP. Hồ Chí Minh', dùng: `filters_json='{{"Địa phương": ["Hà Nội", "TP. Hồ Chí Minh"]}}'`
    - Khi lọc theo 'Địa phương', hãy sử dụng tên chính xác từ danh sách được cung cấp ở trên.
    - Nếu không cần lọc, bỏ qua tham số `filters_json` hoặc đặt là `None`.
- Khi gọi một hàm công cụ (ví dụ: `generate_histogram`), **bạn BẮT BUỘC phải cung cấp tham số `dataframe_name`** với tên chính xác của bộ dữ liệu bạn đã chọn từ danh sách trên.
- Đảm bảo bạn sử dụng tên cột CHÍNH XÁC như được liệt kê cho bộ dữ liệu đã chọn, chú ý đến kiểu dữ liệu của cột khi chọn công cụ phù hợp. Không tự tạo tên cột.
- **Đối với `generate_line_chart`:**
    - Nếu người dùng muốn xem xu hướng cho các nhóm khác nhau (ví dụ: xu hướng học sinh theo từng địa phương), hãy sử dụng tham số `group_by_column` với tên cột chứa nhóm đó (ví dụ: 'Địa phương'). Áp dụng `filters_json` nếu cần lọc thêm các nhóm này.
    - Nếu người dùng muốn xem xu hướng tổng thể và cột X (ví dụ: 'Năm') có thể có nhiều giá trị Y cho mỗi X (ví dụ: nhiều địa phương trong một năm), và bạn *không* sử dụng `group_by_column`, hãy xem xét sử dụng tham số `aggregation`. Mặc định là 'sum', nhưng bạn có thể chỉ định 'mean' hoặc 'median' nếu phù hợp hơn với yêu cầu (ví dụ: 'xu hướng trung bình số học sinh qua các năm'). Áp dụng `filters_json` nếu cần lọc dữ liệu trước khi tổng hợp.
    - Nếu cột X là duy nhất hoặc bạn đang sử dụng `group_by_column`, bạn không cần chỉ định `aggregation`.
- Nếu yêu cầu yêu cầu một cột không tồn tại trong bộ dữ liệu đã chọn, hoặc sử dụng một cột sai loại cho biểu đồ được yêu cầu, hãy thông báo lỗi cho người dùng.
- Đối với các câu hỏi chung về dữ liệu (ví dụ: 'Giá trị trung bình trong [cột] của [bộ dữ liệu] là gì?'), hãy cung cấp câu trả lời trực tiếp bằng văn bản dựa trên thông tin có sẵn (bao gồm f5r). Hãy nêu rõ bạn đang phân tích bộ dữ liệu nào và có áp dụng bộ lọc nào không.
- Giữ các câu trả lời văn bản của bạn ngắn gọn và tập trung vào truy vấn của người dùng.
- Nếu người dùng yêu cầu bạn vẽ một biểu đồ ngẫu nhiên, hãy chọn một bộ dữ liệu và loại biểu đồ phù hợp dựa trên cấu trúc dữ liệu (kiểu cột, f5r), nêu rõ lựa chọn của bạn và gọi hàm công cụ với `dataframe_name` chính xác.
- **Luôn trả lời bằng tiếng Việt.**
"""

    user_query = st.chat_input(
        f"Hỏi về dữ liệu giáo dục...", key="ai_query_input_final"
    )

    chat_msg = None
    if user_query:
        st.session_state["last_call_info"] = None

        st.session_state.chat_history.append(
            types.Content(role="user", parts=[types.Part(text=user_query)])
        )
        with st.chat_message("user"):
            st.markdown(user_query)

        api_history = []
        for msg in st.session_state.chat_history:
            if isinstance(msg, dict):
                role = msg.get("role")
                parts_data = msg.get("parts")
                if role and parts_data:
                    if isinstance(parts_data, list) and isinstance(parts_data[0], str):
                        api_history.append(
                            types.Content(
                                role=role, parts=[types.Part(text=parts_data[0])]
                            )
                        )
            elif isinstance(msg, types.Content):
                api_history.append(msg)

        try:
            with st.spinner("🤖 AI đang suy nghĩ..."):
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=api_history,
                    config=types.GenerateContentConfig(
                        tools=[tools],
                        system_instruction=SYSTEM_PROMPT,
                    ),
                )

                response_content = response.candidates[0].content
                st.session_state.chat_history.append(response_content)

                chat_msg = st.chat_message("ai")

                response_part = response_content.parts[0]

                if response_part.function_call:
                    function_call = response_part.function_call
                    function_name = function_call.name
                    function_args = {
                        key: value for key, value in function_call.args.items()
                    }

                    # st.markdown(
                    #     f"_AI muốn chạy `{function_name}` với các tham số: `{function_args}`_"
                    # )

                    dataframe_name = function_args.get("dataframe_name")
                    if not dataframe_name:
                        chat_msg.error(
                            "Lỗi: AI không chỉ định `dataframe_name` để sử dụng."
                        )
                    elif dataframe_name not in flat_dfs:
                        chat_msg.error(
                            f"Lỗi: AI yêu cầu một bộ dữ liệu không tồn tại: '{dataframe_name}'. Các bộ dữ liệu có sẵn: {list(flat_dfs.keys())}"
                        )
                    elif function_name in AVAILABLE_FUNCTIONS:
                        df_to_analyze = flat_dfs[dataframe_name]
                        chart_function = AVAILABLE_FUNCTIONS[function_name]

                        plot_function_args = function_args.copy()
                        del plot_function_args["dataframe_name"]

                        function_args_with_df = {
                            "df": df_to_analyze,
                            **plot_function_args,
                        }

                        required_cols = []
                        if "column_name" in plot_function_args:
                            required_cols.append(plot_function_args["column_name"])
                        if "x_column" in plot_function_args:
                            required_cols.append(plot_function_args["x_column"])
                        if "y_column" in plot_function_args:
                            required_cols.append(plot_function_args["y_column"])
                        if (
                            "group_by_column" in plot_function_args
                            and plot_function_args["group_by_column"]
                            and plot_function_args["group_by_column"] != "None"
                        ):
                            required_cols.append(plot_function_args["group_by_column"])

                        missing_cols = [
                            col
                            for col in required_cols
                            if col not in df_to_analyze.columns
                        ]

                        if missing_cols:
                            chat_msg.error(
                                f"Lỗi: AI yêu cầu sử dụng cột không tồn tại ({', '.join(missing_cols)}) trong bộ dữ liệu '{dataframe_name}'. Các cột có sẵn: {df_to_analyze.columns.tolist()}"
                            )
                        else:
                            # fig = chart_function(**function_args_with_df)

                            # if fig:
                            # hiện chart
                            # st.plotly_chart(fig, use_container_width=True)
                            # lưu fig và thông tin để phân tích
                            # st.session_state["last_fig"] = function_args_with_df
                            st.session_state["last_call_info"] = dict(
                                # chart_function=function_name,
                                chart_args=plot_function_args,
                                function_name=function_name,
                                function_args=function_args,
                                dataframe_name=dataframe_name,
                                user_query=user_query,
                            )
                            st.session_state["need_layout"] = False
                            st.rerun()

                            # st.session_state["need_layout"] = False
                            # st.session_state.pop("chart_analysis_result", None)
                            # st.markdown(
                            #     f"OK. Đây là `{function_name.replace('_', ' ')}` bạn yêu cầu cho bộ dữ liệu '{dataframe_name}'."
                            # )
                        # else:
                        #     error_message = f"Không thể tạo biểu đồ được yêu cầu (`{function_name}`) cho bộ dữ liệu '{dataframe_name}'. Vui lòng kiểm tra lại yêu cầu hoặc các thông báo lỗi bên trên."
                        #     chat_msg.error(error_message)
                    else:
                        error_message = (
                            f"Lỗi: AI yêu cầu một hàm không xác định '{function_name}'."
                        )
                        chat_msg.error(error_message)

                elif response_part.text:
                    response_text = response_part.text
                    chat_msg.markdown(response_text)
                else:
                    chat_msg.warning("AI trả về một phản hồi trống.")

        except Exception as e:
            st.error(f"Đã xảy ra lỗi trong quá trình tương tác với AI: {e}", icon="🔥")

    # After chat and chart rendering, add analyze button + result
    if (
        "last_call_info" in st.session_state
        and st.session_state["last_call_info"] is not None
    ):
        # Always show the chart before the button and analysis result
        sleep(1)  # Optional: Add a small delay for better UX

        info = st.session_state["last_call_info"]

        # if st.session_state["need_layout"] == True:
        userMsg = st.chat_message("user")
        userMsg.markdown(info["user_query"])

        # st.session_state["need_layout"] = True

        with st.chat_message("ai"):
            st.markdown(
                f"_AI muốn chạy `{info["function_name"]}` với các tham số: `{info["function_args"]}`_"
            )

            fig = AVAILABLE_FUNCTIONS[info["function_name"]](
                flat_dfs[info["dataframe_name"]], **info["chart_args"]
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(
                    f"OK. Đây là biểu đồ bạn yêu cầu sử dụng bộ dữ liệu '{info["dataframe_name"]}'."
                )

                if st.button("🔍 Phân tích"):
                    # fig = st.session_state["last_fig"]
                    # info = st.session_state["last_call_info"]
                    img_bytes = fig.to_image(format="png")
                    with st.spinner("🤖 Đang phân tích biểu đồ..."):
                        resp = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=[
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part.from_bytes(
                                            mime_type="image/png", data=img_bytes
                                        )
                                    ],
                                ),
                            ],
                            config=types.GenerateContentConfig(
                                system_instruction=CHART_ANALYSIS_PROMPT.format(
                                    function_name=info["function_name"],
                                    function_args=info["function_args"],
                                    system_prompt=SYSTEM_PROMPT,
                                )
                            ),
                        )
                    result = resp.candidates[0].content.parts[0].text
                    # st.session_state["chart_analysis_result"] = result

                    # if "chart_analysis_result" in st.session_state:
                    st.write("**📈 Phân tích biểu đồ:**")
                    st.markdown(result)
            else:
                error_message = f"Không thể tạo biểu đồ được yêu cầu (`{function_name}`) cho bộ dữ liệu '{dataframe_name}'. Vui lòng kiểm tra lại yêu cầu hoặc các thông báo lỗi bên trên."
                st.error(error_message)

    st.write("---")
    if st.session_state.get("chat_history"):
        if st.button("Xóa lịch sử trò chuyện", key="ai_clear_history_final"):
            st.session_state["chat_history"] = []
            # st.session_state["last_fig"] = None
            st.session_state["last_call_info"] = None
            st.rerun()

elif not client:
    st.warning("Trợ lý AI yêu cầu cấu hình API và khóa API hợp lệ.")
elif not flat_dfs:
    st.error("Không thể tải bất kỳ bộ dữ liệu nào. Vui lòng kiểm tra thư mục 'data'.")
