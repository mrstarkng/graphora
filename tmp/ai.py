import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types

# from google.generativeai.types import GenerationConfig, FunctionDeclaration, Tool
import utils.load_env
import numpy as np
import os
import json

st.set_page_config(page_title="AI Assistant", layout="wide")

st.title("🤖 AI Assistant")
st.write("### 📌 Upload data, visualize, and ask the AI")

# --- Chart Generation Functions ---


def safe_get_column(df, column_name, dtype=None):
    """Safely get a column, checking existence and optionally type."""
    if column_name not in df.columns:
        st.error(f"Error: Column '{column_name}' not found in the dataset.", icon="⚠️")
        return None
    col = df[column_name]
    if dtype:
        if dtype == "numeric" and not pd.api.types.is_numeric_dtype(col):
            st.error(f"Error: Column '{column_name}' is not numeric.", icon="⚠️")
            return None
        if (
            dtype == "categorical"
            and not pd.api.types.is_object_dtype(col)
            and not pd.api.types.is_categorical_dtype(col)
        ):
            st.warning(
                f"Warning: Column '{column_name}' might not be ideal for categorical analysis.",
                icon="⚠️",
            )
        if dtype == "datetime":
            if not pd.api.types.is_datetime64_any_dtype(col):
                try:
                    col = pd.to_datetime(col)
                except Exception:
                    st.error(
                        f"Error: Could not convert column '{column_name}' to datetime.",
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
            title=f"Distribution of {column_name}",
            template="plotly_white",
        )
        fig.update_layout(bargap=0.1)
        return fig
    except Exception as e:
        st.error(f"Error generating histogram for {column_name}: {e}", icon="⚠️")
        return None


def generate_bar_chart(df: pd.DataFrame, column_name: str, top_n: int = 10):
    """Generates a bar chart for a categorical column."""
    data_col = safe_get_column(df, column_name, dtype="categorical")
    if data_col is None:
        st.warning(
            f"Column '{column_name}' might not be categorical. Attempting bar chart.",
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
            title=f"Top {top_n} Categories in {column_name}",
            template="plotly_white",
            text="count",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(xaxis_title=column_name, yaxis_title="Count")
        return fig
    except Exception as e:
        st.error(f"Error generating bar chart for {column_name}: {e}", icon="⚠️")
        return None


def generate_pie_chart(df: pd.DataFrame, column_name: str, top_n: int = 5):
    """Generates a pie chart for a categorical column, grouping smaller slices."""
    data_col = safe_get_column(df, column_name, dtype="categorical")
    if data_col is None:
        st.warning(
            f"Column '{column_name}' might not be categorical. Attempting pie chart.",
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
                other_row = pd.DataFrame({column_name: ["Other"], "count": [other_sum]})
                pie_df = pd.concat([top_df, other_row], ignore_index=True)
            else:
                pie_df = top_df
        else:
            pie_df = counts

        fig = px.pie(
            pie_df,
            names=column_name,
            values="count",
            title=f"Proportion of Top {top_n} Categories in {column_name}",
            template="plotly_white",
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        return fig
    except Exception as e:
        st.error(f"Error generating pie chart for {column_name}: {e}", icon="⚠️")
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
            except Exception:
                st.warning(
                    f"Could not convert X-axis '{x_column}' to Date/Time. Treating as is.",
                    icon="⚠️",
                )
        df_line = df_line.sort_values(by=x_column).dropna(subset=[x_column, y_column])
        if not df_line.empty:
            fig = px.line(
                df_line,
                x=x_column,
                y=y_column,
                title=f"Trend of {y_column} over {x_column}",
                template="plotly_white",
                markers=True,
            )
            fig.update_layout(xaxis_title=x_column, yaxis_title=y_column)
            return fig
        else:
            st.warning(
                f"No valid data points found for Line Chart ({y_column} vs {x_column}).",
                icon="⚠️",
            )
            return None
    except Exception as e:
        st.error(
            f"Error generating line chart ({y_column} vs {x_column}): {e}", icon="⚠️"
        )
        return None


def generate_scatter_plot(
    df: pd.DataFrame, x_column: str, y_column: str, color_column: str = None
):
    """Generates a scatter plot between two numeric columns, optionally colored by a third."""
    x_data = safe_get_column(df, x_column, dtype="numeric")
    y_data = safe_get_column(df, y_column, dtype="numeric")
    color_data = None
    if color_column and color_column != "None":
        color_data = safe_get_column(df, color_column)
        if color_data is None:
            st.warning(
                f"Color column '{color_column}' not found or invalid. Scatter plot will not be colored.",
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
            plot_args["title"] += f" (Colored by {color_column})"
        sample_size = min(2000, df.shape[0])
        df_sample = df.sample(sample_size) if df.shape[0] > 2000 else df
        fig = px.scatter(df_sample, **plot_args)
        return fig
    except Exception as e:
        st.error(
            f"Error generating scatter plot ({y_column} vs {x_column}): {e}", icon="⚠️"
        )
        return None


# --- Mapping function names to functions ---
AVAILABLE_FUNCTIONS = {
    "generate_histogram": generate_histogram,
    "generate_bar_chart": generate_bar_chart,
    "generate_pie_chart": generate_pie_chart,
    "generate_line_chart": generate_line_chart,
    "generate_scatter_plot": generate_scatter_plot,
}

# --- Define Tools for Gemini ---
tools = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="generate_histogram",
            description="Create a histogram for a specified numeric column to show its distribution.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="The numeric column name.",
                    ),
                    "num_bins": types.Schema(
                        type=types.Type.INTEGER,
                        description="Number of bins (default 30).",
                        default=30,
                    ),
                },
                required=["column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_bar_chart",
            description="Create a bar chart for a specified categorical column to show counts of top categories.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="The categorical column name.",
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Number of top categories to show (default 10).",
                        default=10,
                    ),
                },
                required=["column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_pie_chart",
            description="Create a pie chart for a specified categorical column to show the proportion of top categories.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "column_name": types.Schema(
                        type=types.Type.STRING,
                        description="The categorical column name.",
                    ),
                    "top_n": types.Schema(
                        type=types.Type.INTEGER,
                        description="Number of slices (group others, default 5).",
                        default=5,
                    ),
                },
                required=["column_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_line_chart",
            description="Create a line chart to show the trend of a numeric column over another numeric or datetime column (X-axis).",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "x_column": types.Schema(
                        type=types.Type.STRING,
                        description="The column for the X-axis (time or sequence).",
                    ),
                    "y_column": types.Schema(
                        type=types.Type.STRING,
                        description="The numeric column for the Y-axis.",
                    ),
                },
                required=["x_column", "y_column"],
            ),
        ),
        types.FunctionDeclaration(
            name="generate_scatter_plot",
            description="Create a scatter plot to show the relationship between two numeric columns. Optionally color points by a third column.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "x_column": types.Schema(
                        type=types.Type.STRING,
                        description="The numeric column for the X-axis.",
                    ),
                    "y_column": types.Schema(
                        type=types.Type.STRING,
                        description="The numeric column for the Y-axis.",
                    ),
                    "color_column": types.Schema(
                        type=types.Type.STRING,
                        description="Optional categorical column to color points by.",
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
        st.error("🚨 GEMINI_API_KEY environment variable not set!")
        st.stop()
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig(tools=[tools])
    # model = genai.GenerativeModel(model_name="gemini-1.5-flash", tools=[tools])
    # genai_client = genai
except Exception as e:
    st.error(f"Error configuring Gemini AI: {e}")
    st.warning(
        "Please ensure API key is set correctly and you have the necessary packages."
    )
    client = None

# Initialize session memory
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "current_df_display" not in st.session_state:
    st.session_state["current_df_display"] = None
if "analysis_target_name" not in st.session_state:
    st.session_state["analysis_target_name"] = None

# File uploader
uploaded_file = st.file_uploader(
    "Upload your CSV file", type=["csv"], key="ai_assistant_uploader_final"
)

# --- Xử lý Data Source và tải dữ liệu ---
df_to_analyze = None
analysis_target_name = None
if uploaded_file:
    try:
        current_df = pd.read_csv(uploaded_file)
        st.session_state["current_df_display"] = current_df
        st.session_state["analysis_target_name"] = uploaded_file.name
        st.session_state["chat_history"] = []
        st.success(
            f"File '{uploaded_file.name}' uploaded successfully. Ready for analysis."
        )
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
        st.session_state["current_df_display"] = None
        st.session_state["analysis_target_name"] = None

if st.session_state.get("current_df_display") is not None:
    df_to_analyze = st.session_state["current_df_display"]
    analysis_target_name = st.session_state["analysis_target_name"]

if df_to_analyze is not None and client and analysis_target_name:
    st.success(
        f"Ready to analyze: **{analysis_target_name}** ({df_to_analyze.shape[0]} rows, {df_to_analyze.shape[1]} cols)"
    )

    # --- Get Column Information for Context ---
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
        # Create a more structured column info string for the prompt
        column_info_prompt = f"""
Available columns in the dataset '{analysis_target_name}':
- Numeric Columns: {numeric_columns if numeric_columns else 'None'}
- Categorical Columns: {categorical_columns if categorical_columns else 'None'}
- DateTime Columns: {datetime_columns if datetime_columns else 'None'}

Use the provided tools to generate visualizations based on these columns when requested.
Ask for clarification if the request is ambiguous about column names or types.
Provide text answers for general questions about the data.
"""
        # Keep the simpler string for display if needed elsewhere
        column_info_display = f"Numeric columns: {numeric_columns}\nCategorical columns: {categorical_columns}\nDateTime columns: {datetime_columns}"

    except Exception as e:
        st.warning(f"Could not automatically determine all column types: {e}")
        column_info_prompt = f"Column type detection failed. Available columns in '{analysis_target_name}': {df_to_analyze.columns.tolist()}\nUse tools based on user request and column names."
        column_info_display = "Column type detection failed."

    # --- Simplified Dashboard Tab ---
    st.write("---")
    with st.expander("📊 Quick Data Overview", expanded=False):
        st.markdown("#### Basic Info & Sample Data")
        col_info, col_sample = st.columns([1, 2])
        with col_info:
            st.metric("Total Rows", df_to_analyze.shape[0])
            st.metric("Total Columns", df_to_analyze.shape[1])
            st.text("Column Types:")
            st.json(
                df_to_analyze.dtypes.apply(lambda x: str(x)).to_dict(), expanded=False
            )

        with col_sample:
            st.text("Data Sample (First 5 rows):")
            st.dataframe(df_to_analyze.head())

        st.markdown("#### Numeric Summary")
        if numeric_columns:
            st.dataframe(df_to_analyze[numeric_columns].describe())
        else:
            st.caption("No numeric columns found for summary statistics.")

    # --- PHẦN HỎI ĐÁP VỚI AI (Updated Logic) ---
    st.write("---")
    st.subheader("💬 Ask the AI about this data")
    st.caption(
        "Example: 'Show the distribution of Age', 'Compare Sales and Profit', 'What are the most common product categories?'"
    )

    # --- Define System Prompt ---
    SYSTEM_PROMPT = f"""You are an AI assistant specialized in analyzing the provided CSV data ({analysis_target_name}).
Your goal is to help the user understand their data by answering questions and generating relevant visualizations using the available tools.

Data Context:
{column_info_prompt}
First 5 rows of the data:
{df_to_analyze.head().to_string()}

Instructions:
- Analyze the user's request.
- If the request asks for a visualization that matches one of your tools (histogram, bar chart, pie chart, line chart, scatter plot), use the appropriate tool function call with the correct column names based on the Data Context.
- Ensure you use column names exactly as listed in the Data Context.
- If the request is ambiguous or requires a column that doesn't exist or is of the wrong type for the chart, ask the user for clarification.
- For general questions about the data (e.g., 'What is the average age?', 'How many rows are there?'), provide a direct text answer based on the data context if possible, or explain if the information isn't readily available.
- Keep your text responses concise and focused on the user's query.
- If user ask to draw a random chart, just pick one that you think is most suitable for the data and call that function, dont ask any further questions or wait for any confirmation.
"""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history (no changes needed here)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if (
                isinstance(message["parts"], dict)
                and "function_call" in message["parts"]
            ):
                st.markdown("_AI requested a chart..._")
            elif (
                isinstance(message["parts"], dict)
                and "function_response" in message["parts"]
            ):
                st.markdown(f"📊 Chart generated based on AI request.")
            elif isinstance(message["parts"], list):
                st.markdown(message["parts"][0])
            else:
                st.markdown(message["parts"])

    user_query = st.chat_input(
        "Enter your question here...", key="ai_query_input_final"
    )

    if user_query:
        # Append user message immediately for display
        # st.session_state.chat_history.append({"role": "user", "parts": [user_query]})
        with st.chat_message("user"):
            st.markdown(user_query)

        # --- Prepare content for API call ---
        # Combine system prompt, history, and new query
        # api_contents = [
        #     types.Content(parts=[types.Part(text=SYSTEM_PROMPT)], role="system")
        # ]  # Start with system prompt as 'user' for context
        # api_contents = []
        # api_contents.append(
        #     types.Content(
        #         parts=[
        #             types.Part(
        #                 text="Okay, I understand the context and my role. How can I help?"
        #             )
        #         ],
        #         role="model",
        #     )
        # )  # Add an implicit model confirmation

        api_contents = []
        # Add actual chat history, ensuring correct format
        for msg in st.session_state.chat_history:
            # Skip potential function call/response dicts if they cause issues, or format them if API supports
            # if isinstance(msg["parts"], list):  # Only include text parts for now
            #     api_contents.append(
            #         types.Content(
            #             parts=[types.Part(text=msg["parts"][0])], role=msg["role"]
            #         )
            #     )
            print(msg)
            api_contents.append(msg)

        try:
            with st.spinner("🤖 AI is thinking..."):
                # --- Call Gemini API ---
                # print("API contents:", api_contents)  # Debugging line

                # config.system_instruction = SYSTEM_PROMPT  # type: ignore # Set system instruction
                response = client.models.generate_content(
                    model="gemini-2.0-flash",  # Use the correct model string
                    contents=user_query,  # Send the constructed history + system prompt
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,  # type: ignore
                        tools=[tools],  # Pass the tools
                    ),  # Pass the config with tools
                )

                # --- Process Response ---
                response_part = response.candidates[0].content.parts[0]  # type: ignore
                print("Response part:", response_part)  # Debugging line

                if not st.session_state.chat_history:
                    st.session_state.chat_history = []

                st.session_state.chat_history.append(
                    response.candidates[0].content  # type: ignore
                )

                # Check for function call (logic remains similar)
                if (
                    hasattr(response_part, "function_call")
                    and response_part.function_call
                ):
                    function_call = response_part.function_call
                    function_name = function_call.name
                    function_args = {
                        key: value for key, value in function_call.args.items()
                    }

                    if function_name in AVAILABLE_FUNCTIONS:
                        chart_function = AVAILABLE_FUNCTIONS[function_name]
                        st.info(
                            f"🤖 AI requested to run: `{function_name}` with arguments: `{function_args}`"
                        )

                        fig = chart_function(df=df_to_analyze, **function_args)

                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            # Create a simple text response confirming the action
                            final_response_text = f"OK. Here is the {function_name.replace('_', ' ')} you requested."
                            # Append the confirmation text to history for display
                            st.session_state.chat_history.append(
                                {"role": "model", "parts": [final_response_text]}
                            )
                            # Display the confirmation text
                            with st.chat_message("assistant"):
                                st.markdown(final_response_text)
                        else:
                            # Error handled within chart function, add generic error to chat
                            error_message = f"Failed to generate the requested chart ({function_name}). Please check the column names and types or try a different request."
                            st.error(error_message)
                            st.session_state.chat_history.append(
                                {"role": "model", "parts": [error_message]}
                            )
                    else:
                        # Handle unknown function call
                        error_message = f"Error: AI requested an unknown function '{function_name}'."
                        st.error(error_message)
                        st.session_state.chat_history.append(
                            {"role": "model", "parts": [error_message]}
                        )
                else:
                    # Handle text response
                    response_text = response_part.text
                    st.session_state.chat_history.append(
                        {"role": "model", "parts": [response_text]}
                    )
                    with st.chat_message("assistant"):
                        st.markdown(response_text)

        except:
            st.error(
                "An error occurred while processing your request. Please try again.",
                icon="⚠️",
            )
            st.error(f"An error occurred during AI interaction:", icon="🔥")
            # Append error to chat history for visibility
            # st.session_state.chat_history.append(
            #     {"role": "model", "parts": [f"Error during processing:"]}
            # )
            # Rerun might be needed here to show the error message added to history
            # st.rerun()

    # --- Clear History Button ---
    st.write("---")
    if st.session_state.get("chat_history"):
        if st.button("Clear Chat History", key="ai_clear_history_final"):
            st.session_state["chat_history"] = []
            st.rerun()

elif not client:
    st.warning("AI Assistant requires API configuration and a valid API key.")
elif df_to_analyze is None:
    st.info("☝️ Upload a CSV file to get started.")
