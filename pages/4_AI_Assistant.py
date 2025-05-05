import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types
import numpy as np
import os
import json

st.set_page_config(page_title="Trợ lý AI", layout="wide")

st.title("🤖 Trợ lý AI")
st.write("### 📌 Chọn dữ liệu, trực quan hóa và hỏi AI")

# --- Chart Generation Functions (Copied from ai.py) ---


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


def generate_histogram(df: pd.DataFrame, column_name: str, num_bins: int = 30):
    """Generates a histogram for a numeric column."""
    data_col = safe_get_column(df, column_name, dtype="numeric")
    if data_col is None:
        return None
    try:
        fig = px.histogram(
            df,
            x=column_name,
            nbins=int(num_bins),
            title=f"Phân phối của {column_name}",
            template="plotly_white",
        )
        fig.update_layout(bargap=0.1)
        return fig
    except Exception as e:
        st.error(f"Lỗi tạo biểu đồ tần suất cho {column_name}: {e}", icon="⚠️")
        return None


def generate_bar_chart(df: pd.DataFrame, column_name: str, top_n: int = 10):
    """Generates a bar chart for a categorical column."""
    data_col = safe_get_column(df, column_name, dtype="categorical")
    if data_col is None:
        st.warning(
            f"Cột '{column_name}' có thể không phải là danh mục. Đang thử tạo biểu đồ cột.",
            icon="⚠️",
        )
    try:
        top_n = int(top_n)
        counts = df[column_name].value_counts().nlargest(top_n).reset_index()
        counts.columns = [column_name, "count"]
        fig = px.bar(
            counts,
            x=column_name,
            y="count",
            title=f"{top_n} Danh mục hàng đầu trong {column_name}",
            template="plotly_white",
            text="count",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title=column_name, yaxis_title="Số lượng")
        return fig
    except Exception as e:
        st.error(f"Lỗi tạo biểu đồ cột cho {column_name}: {e}", icon="⚠️")
        return None


def generate_pie_chart(df: pd.DataFrame, column_name: str, top_n: int = 5):
    """Generates a pie chart for a categorical column, grouping smaller slices."""
    data_col = safe_get_column(df, column_name, dtype="categorical")
    if data_col is None:
        st.warning(
            f"Cột '{column_name}' có thể không phải là danh mục. Đang thử tạo biểu đồ tròn.",
            icon="⚠️",
        )
    try:
        top_n = int(top_n)
        counts = df[column_name].value_counts().reset_index()
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
            title=f"Tỷ lệ {top_n} Danh mục hàng đầu trong {column_name}",
            template="plotly_white",
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        return fig
    except Exception as e:
        st.error(f"Lỗi tạo biểu đồ tròn cho {column_name}: {e}", icon="⚠️")
        return None


def generate_line_chart(df: pd.DataFrame, x_column: str, y_column: str):
    """Generates a line chart for trends over time or sequence."""
    x_data = safe_get_column(df, x_column)
    y_data = safe_get_column(df, y_column, dtype="numeric")
    if x_data is None or y_data is None:
        return None
    try:
        df_line = df[[x_column, y_column]].copy()
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
        df_line = df_line.sort_values(by=x_column).dropna(subset=[x_column, y_column])
        if not df_line.empty:
            fig = px.line(
                df_line,
                x=x_column,
                y=y_column,
                title=f"Xu hướng của {y_column} theo {x_column}",
                template="plotly_white",
                markers=True,
            )
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
    df: pd.DataFrame, x_column: str, y_column: str, color_column: str = None
):
    """Generates a scatter plot between two numeric columns, optionally colored by a third."""
    x_data = safe_get_column(df, x_column, dtype="numeric")
    y_data = safe_get_column(df, y_column, dtype="numeric")
    color_data = None
    if color_column and color_column != "None" and color_column.strip() != "":
        color_data = safe_get_column(df, color_column)
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
            "title": f"{y_column} vs {x_column}",
            "template": "plotly_white",
        }
        if color_column:
            plot_args["color"] = color_column
            plot_args["title"] += f" (Tô màu theo {color_column})"

        sample_size = min(2000, df.shape[0])
        df_sample = df.sample(sample_size) if df.shape[0] > 2000 else df

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

# --- Define Tools for Gemini (Copied from ai.py) ---
tools = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="generate_histogram",
            description="Tạo biểu đồ tần suất cho một cột số được chỉ định để hiển thị phân phối của nó.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên cột số.",
                    ),
                    "num_bins": types.Schema(
                        type=types.Type.INTEGER,
                        description="Số lượng khoảng (mặc định 30).",
                        default=30,
                    ),
                },
                required=["column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_bar_chart",
            description="Tạo biểu đồ cột cho một cột danh mục được chỉ định để hiển thị số lượng các danh mục hàng đầu.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên cột danh mục.",
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Số lượng danh mục hàng đầu cần hiển thị (mặc định 10).",
                        default=10,
                    ),
                },
                required=["column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_pie_chart",
            description="Tạo biểu đồ tròn cho một cột danh mục được chỉ định để hiển thị tỷ lệ của các danh mục hàng đầu.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="Tên cột danh mục.",
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Số lượng lát cắt (nhóm các mục khác, mặc định 5).",
                        default=5,
                    ),
                },
                required=["column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_line_chart",
            description="Tạo biểu đồ đường để hiển thị xu hướng của một cột số theo một cột số hoặc ngày giờ khác (trục X).",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "x_column": types.Schema(
                        type=types.Type.STRING,
                        description="Cột cho trục X (thời gian hoặc chuỗi).",
                    ),
                    "y_column": types.Schema(
                        type=types.Type.STRING,
                        description="Cột số cho trục Y.",
                    ),
                },
                required=["x_column", "y_column"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_scatter_plot",
            description="Tạo biểu đồ phân tán để hiển thị mối quan hệ giữa hai cột số. Tùy chọn tô màu các điểm theo cột thứ ba.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
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
                        description="Cột danh mục hoặc số tùy chọn để tô màu các điểm. Sử dụng 'None' hoặc bỏ qua nếu không tô màu.",
                        nullable=True,
                        default=None,
                    ),
                },
                required=["x_column", "y_column"],
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
if "selected_df_name" not in st.session_state:
    st.session_state["selected_df_name"] = None
if "selected_df" not in st.session_state:
    st.session_state["selected_df"] = None

# --- Load DataFrames ---
DATA_DIR = "data"
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
    flat_dfs = {}
    for category, sub_dfs in dfs.items():
        for name, df in sub_dfs.items():
            flat_dfs[f"{category} - {name}"] = df

except FileNotFoundError as e:
    st.error(
        f"🚨 Lỗi tải tệp dữ liệu: {e}. Vui lòng đảm bảo các tệp dữ liệu có mặt tại đường dẫn dự kiến bắt đầu từ '{DATA_DIR}'."
    )
    st.stop()
except Exception as e:
    st.error(f"🚨 Đã xảy ra lỗi không mong muốn khi tải dữ liệu: {e}")
    st.stop()


# --- DataFrame Selection ---
st.sidebar.header("Chọn Dữ liệu để Phân tích")
available_df_names = list(flat_dfs.keys())
selected_df_key = st.sidebar.selectbox(
    "Chọn một bộ dữ liệu:",
    options=available_df_names,
    index=(
        available_df_names.index(st.session_state["selected_df_name"])
        if st.session_state["selected_df_name"] in available_df_names
        else 0
    ),
    key="df_selector",
)

if selected_df_key != st.session_state["selected_df_name"]:
    st.session_state["selected_df_name"] = selected_df_key
    st.session_state["selected_df"] = flat_dfs[selected_df_key]
    st.session_state["chat_history"] = []
    st.rerun()

df_to_analyze = st.session_state.get("selected_df")
analysis_target_name = st.session_state.get("selected_df_name")

if df_to_analyze is not None and client and analysis_target_name:
    st.header(f"Đang phân tích: {analysis_target_name}")
    st.success(
        f"Sẵn sàng phân tích: **{analysis_target_name}** ({df_to_analyze.shape[0]} hàng, {df_to_analyze.shape[1]} cột)"
    )

    try:
        numeric_columns = df_to_analyze.select_dtypes(
            include=np.number
        ).columns.tolist()
        categorical_columns = df_to_analyze.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        datetime_columns = df_to_analyze.select_dtypes(
            include="datetime"
        ).columns.tolist()
        potential_dt_cols = []
        for col in df_to_analyze.select_dtypes(include="object").columns:
            if (
                df_to_analyze[col]
                .astype(str)
                .str.match(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}")
                .any()
            ):
                potential_dt_cols.append(col)

        column_info_prompt = f"""
Các cột có sẵn trong bộ dữ liệu '{analysis_target_name}':
- Cột số: {numeric_columns if numeric_columns else 'Không có'}
- Cột danh mục: {categorical_columns if categorical_columns else 'Không có'}
- Cột ngày giờ (Đã phát hiện): {datetime_columns if datetime_columns else 'Không có'}
- Cột có thể là ngày giờ (kiểu object): {potential_dt_cols if potential_dt_cols else 'Không có'}

Sử dụng các công cụ được cung cấp để tạo trực quan hóa dựa trên các cột này khi được yêu cầu.
Yêu cầu làm rõ nếu yêu cầu không rõ ràng về tên hoặc loại cột.
Cung cấp câu trả lời bằng văn bản cho các câu hỏi chung về dữ liệu.
Khi sử dụng generate_line_chart, hãy thử chuyển đổi các cột ngày giờ tiềm năng nếu được chỉ định làm trục x.
Khi sử dụng generate_scatter_plot, cột màu (color_column) có thể là số hoặc danh mục.
"""
    except Exception as e:
        st.warning(f"Không thể tự động xác định tất cả các loại cột: {e}")
        column_info_prompt = f"Việc phát hiện loại cột có thể chưa hoàn chỉnh. Các cột có sẵn trong '{analysis_target_name}': {df_to_analyze.columns.tolist()}\nSử dụng các công cụ dựa trên yêu cầu của người dùng và tên cột."

    with st.expander("📊 Tổng quan nhanh về dữ liệu", expanded=False):
        st.markdown("#### Thông tin cơ bản & Dữ liệu mẫu")
        col_info, col_sample = st.columns([1, 2])
        with col_info:
            st.metric("Tổng số hàng", df_to_analyze.shape[0])
            st.metric("Tổng số cột", df_to_analyze.shape[1])
            st.text("Loại cột:")
            try:
                st.json(
                    df_to_analyze.dtypes.apply(lambda x: str(x)).to_dict(),
                    expanded=False,
                )
            except Exception as json_e:
                st.text(f"Không thể hiển thị loại cột dưới dạng JSON: {json_e}")
                st.text(df_to_analyze.dtypes)

        with col_sample:
            st.text("Dữ liệu mẫu (5 hàng đầu tiên):")
            st.dataframe(df_to_analyze.head())

        st.markdown("#### Tóm tắt số liệu")
        if numeric_columns:
            st.dataframe(df_to_analyze[numeric_columns].describe())
        else:
            st.caption("Không tìm thấy cột số nào cho thống kê tóm tắt.")

    st.write("---")
    st.subheader("💬 Hỏi AI về dữ liệu này")
    st.caption(
        f"Ví dụ: 'Hiển thị phân phối của [tên cột số]', 'So sánh [cột số 1] và [cột số 2]', 'Các danh mục phổ biến nhất trong [tên cột danh mục] là gì?' sử dụng các cột từ '{analysis_target_name}'."
    )

    SYSTEM_PROMPT = f"""
Đây là mô tả ứng dụng của tôi:
"Graphora là một nền tảng trực quan hóa dữ liệu giáo dục được thiết kế nhằm phục vụ cho mục tiêu **phân tích và đánh giá toàn diện tình hình giáo dục tại Việt Nam"    
Bạn là một trợ lý AI cho ứng dụng này, chuyên phân tích dữ liệu CSV được cung cấp có tên '{analysis_target_name}'.
Mục tiêu của bạn là giúp người dùng hiểu dữ liệu của họ bằng cách trả lời các câu hỏi và tạo các trực quan hóa liên quan bằng các công cụ có sẵn.
**Hãy trả lời bằng tiếng Việt.**

Bối cảnh dữ liệu cho '{analysis_target_name}':
{column_info_prompt}
5 hàng đầu tiên của dữ liệu:
{df_to_analyze.head().to_string()}

Hướng dẫn:
- Phân tích yêu cầu của người dùng một cách cẩn thận, xem xét bối cảnh của bộ dữ liệu '{analysis_target_name}'.
- Nếu yêu cầu yêu cầu một trực quan hóa phù hợp với một trong các công cụ của bạn (biểu đồ tần suất, biểu đồ cột, biểu đồ tròn, biểu đồ đường, biểu đồ phân tán), hãy sử dụng lệnh gọi hàm công cụ thích hợp với tên cột chính xác dựa trên Bối cảnh dữ liệu được cung cấp ở trên.
- Đảm bảo bạn sử dụng tên cột CHÍNH XÁC như được liệt kê trong Bối cảnh dữ liệu. Không tự tạo tên cột.
- Nếu yêu cầu không rõ ràng, yêu cầu một cột không tồn tại hoặc sử dụng một cột sai loại cho biểu đồ được yêu cầu, hãy yêu cầu người dùng làm rõ. Cung cấp các tùy chọn cụ thể nếu có thể.
- Đối với các câu hỏi chung về dữ liệu (ví dụ: 'Giá trị trung bình trong [cột] là gì?', 'Có bao nhiêu giá trị duy nhất trong [cột]?'), hãy cung cấp câu trả lời trực tiếp bằng văn bản dựa trên bối cảnh dữ liệu nếu có thể, hoặc giải thích nếu thông tin không có sẵn.
- Giữ các câu trả lời văn bản của bạn ngắn gọn và tập trung vào truy vấn của người dùng.
- Nếu người dùng yêu cầu bạn vẽ một biểu đồ ngẫu nhiên, hãy suy luận về dữ liệu và tự động gọi hàm thích hợp để tạo biểu đồ mà không cần hỏi thêm người dùng.
- Khi đề xuất, hãy tập trung vào việc đề xuất mục đích của biểu đồ thay vì chi tiết của nó.
- **Luôn trả lời bằng tiếng Việt.**
"""

    user_query = st.chat_input(
        f"Hỏi về '{analysis_target_name}'...", key="ai_query_input_final"
    )

    if user_query:
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

                with st.chat_message("model"):
                    response_part = response_content.parts[0]

                    if response_part.function_call:
                        function_call = response_part.function_call
                        function_name = function_call.name
                        function_args = {
                            key: value for key, value in function_call.args.items()
                        }

                        st.markdown(
                            f"_AI muốn chạy `{function_name}` với các tham số: `{function_args}`_"
                        )

                        if function_name in AVAILABLE_FUNCTIONS:
                            chart_function = AVAILABLE_FUNCTIONS[function_name]
                            function_args_with_df = {
                                "df": df_to_analyze,
                                **function_args,
                            }

                            fig = chart_function(**function_args_with_df)

                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                                st.markdown(
                                    f"OK. Đây là `{function_name.replace('_', ' ')}` bạn yêu cầu cho '{analysis_target_name}'."
                                )
                            else:
                                error_message = f"Không thể tạo biểu đồ được yêu cầu (`{function_name}`). Vui lòng kiểm tra tên cột và loại được đề cập trong lỗi ở trên hoặc thử một yêu cầu khác."
                                st.error(error_message)
                                st.session_state.chat_history.append(
                                    types.Content(
                                        role="model",
                                        parts=[types.Part(text=error_message)],
                                    )
                                )

                        else:
                            error_message = f"Lỗi: AI yêu cầu một hàm không xác định '{function_name}'."
                            st.error(error_message)
                            st.session_state.chat_history.append(
                                types.Content(
                                    role="model", parts=[types.Part(text=error_message)]
                                )
                            )

                    elif response_part.text:
                        response_text = response_part.text
                        st.markdown(response_text)
                    else:
                        st.warning("AI trả về một phản hồi trống.")

        except Exception as e:
            st.error(f"Đã xảy ra lỗi trong quá trình tương tác với AI: {e}", icon="🔥")
            st.session_state.chat_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text=f"Lỗi trong quá trình xử lý: {e}")],
                )
            )
            st.rerun()

    st.write("---")
    if st.session_state.get("chat_history"):
        if st.button("Xóa lịch sử trò chuyện", key="ai_clear_history_final"):
            st.session_state["chat_history"] = []
            st.rerun()

elif not client:
    st.warning("Trợ lý AI yêu cầu cấu hình API và khóa API hợp lệ.")
elif df_to_analyze is None:
    st.info("☝️ Chọn một bộ dữ liệu từ thanh bên để bắt đầu.")
