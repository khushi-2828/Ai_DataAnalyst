# ============================================================
# AI DATA ANALYST
# Step 16.11.7
# AI Chart Recommendations + Business Insights
# ============================================================

import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from dotenv import load_dotenv

load_dotenv()

from utils.nl_to_sql import generate_sql

try:
    from utils.dataset_summary import generate_dataset_summary
except ImportError:
    generate_dataset_summary = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        color: #666;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .dashboard-title {
        font-size: 28px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "df": None,
    "filtered_df": None,
    "file_name": None,

    "connection": None,
    "filtered_connection": None,

    "last_question": "",
    "sql_query": "",
    "query_result": None,

    "dataset_summary": None,
    "summary_generated_for": None,

    "dashboard_questions": [""],
    "dashboard_components": [],

    "filters_applied": False,

    "generated_report": None,

    "chart_recommendations": [],
    "recommended_charts": [],

    "business_insights": []
}


for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<p class="main-title">📊 AI Data Analyst</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">'
    'AI-powered data analysis, natural language SQL, '
    'interactive visualization and smart dashboards.'
    '</p>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📂 Dataset")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"]
    )

    st.divider()

    st.markdown("### 🚀 Features")

    st.markdown(
        """
        ✅ AI Dataset Summary

        ✅ Natural Language → SQL

        ✅ Automatic EDA

        ✅ Custom Visualization

        ✅ Multi-question Dashboard

        ✅ Smart Filters

        ✅ AI Chart Recommendations

        ✅ Business Insights

        ✅ KPI Cards

        ✅ Anomaly Detection

        ✅ Analyst Report
        """
    )


# ============================================================
# FILE CHECK
# ============================================================

if uploaded_file is None:

    st.info("👆 Upload a CSV file from the sidebar to begin.")

    st.stop()


# ============================================================
# READ CSV
# ============================================================

try:

    uploaded_df = pd.read_csv(uploaded_file)

except Exception as e:

    st.error(f"❌ Could not read CSV file: {e}")

    st.stop()


file_name = uploaded_file.name


# ============================================================
# DATASET CHANGE
# ============================================================

if st.session_state.file_name != file_name:

    st.session_state.file_name = file_name

    st.session_state.df = uploaded_df.copy()

    st.session_state.filtered_df = uploaded_df.copy()

    st.session_state.connection = None

    st.session_state.filtered_connection = None

    st.session_state.dataset_summary = None

    st.session_state.summary_generated_for = None

    st.session_state.query_result = None

    st.session_state.sql_query = ""

    st.session_state.dashboard_questions = [""]

    st.session_state.dashboard_components = []

    st.session_state.filters_applied = False

    st.session_state.chart_recommendations = []

    st.session_state.recommended_charts = []

    st.session_state.business_insights = []


df = st.session_state.df.copy()


# ============================================================
# SQLITE DATABASE
# ============================================================

if st.session_state.connection is None:

    connection = sqlite3.connect(
        ":memory:",
        check_same_thread=False
    )

    df.to_sql(
        "sales",
        connection,
        index=False,
        if_exists="replace"
    )

    st.session_state.connection = connection


connection = st.session_state.connection


# ============================================================
# DATE COLUMN DETECTION
# ============================================================

def detect_date_columns(dataframe):

    dates = []

    for column in dataframe.columns:

        if pd.api.types.is_datetime64_any_dtype(
            dataframe[column]
        ):
            dates.append(column)

        elif dataframe[column].dtype == "object":

            sample = dataframe[column].dropna().head(100)

            if len(sample) > 0:

                converted = pd.to_datetime(
                    sample,
                    errors="coerce"
                )

                if converted.notna().mean() >= 0.80:
                    dates.append(column)

    return dates


date_columns = detect_date_columns(df)


# ============================================================
# COLUMN TYPES
# ============================================================

numeric_columns = (
    df.select_dtypes(include=np.number)
    .columns
    .tolist()
)

categorical_columns = (
    df.select_dtypes(
        include=["object", "category", "bool"]
    )
    .columns
    .tolist()
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:

    st.divider()

    st.header("🔎 Dashboard Filters")

    selected_date_column = "None"
    start_date = None
    end_date = None


    # DATE FILTER

    if date_columns:

        selected_date_column = st.selectbox(
            "📅 Date Column",
            ["None"] + date_columns
        )

        if selected_date_column != "None":

            converted_dates = pd.to_datetime(
                df[selected_date_column],
                errors="coerce"
            )

            valid_dates = converted_dates.dropna()

            if not valid_dates.empty:

                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()

                date_range = st.date_input(
                    "Select Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )

                if (
                    isinstance(date_range, tuple)
                    and len(date_range) == 2
                ):
                    start_date, end_date = date_range


    # CATEGORICAL FILTERS

    selected_filters = {}

    for column in categorical_columns:

        unique_count = df[column].nunique(dropna=True)

        if 1 < unique_count <= 100:

            options = (
                df[column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            options.sort()

            selected_values = st.multiselect(
                f"🏷️ {column}",
                options
            )

            if selected_values:
                selected_filters[column] = selected_values


    st.divider()

    apply_filters = st.button(
        "🔄 Apply Filters",
        type="primary",
        width="stretch"
    )

    clear_filters = st.button(
        "❌ Clear Filters",
        width="stretch"
    )


# ============================================================
# CLEAR FILTERS
# ============================================================

if clear_filters:

    st.session_state.filtered_df = df.copy()

    st.session_state.filters_applied = False

    st.session_state.chart_recommendations = []

    st.session_state.recommended_charts = []

    st.session_state.business_insights = []

    st.session_state.dashboard_components = []

    st.rerun()


# ============================================================
# APPLY FILTERS
# ============================================================

if apply_filters:

    working_df = df.copy()


    # DATE FILTER

    if (
        selected_date_column != "None"
        and start_date is not None
        and end_date is not None
    ):

        converted_dates = pd.to_datetime(
            working_df[selected_date_column],
            errors="coerce"
        )

        working_df = working_df[
            (converted_dates.dt.date >= start_date)
            &
            (converted_dates.dt.date <= end_date)
        ]


    # CATEGORY FILTERS

    for column, values in selected_filters.items():

        working_df = working_df[
            working_df[column]
            .astype(str)
            .isin(values)
        ]


    st.session_state.filtered_df = working_df

    st.session_state.filters_applied = True

    st.session_state.chart_recommendations = []

    st.session_state.recommended_charts = []

    st.session_state.business_insights = []

    st.session_state.dashboard_components = []

    st.rerun()


# ============================================================
# FILTERED DATA
# ============================================================

filtered_df = st.session_state.filtered_df.copy()


if filtered_df.empty:

    st.warning(
        "⚠️ No data matches the selected filters."
    )


# ============================================================
# FILTER STATUS
# ============================================================

if st.session_state.filters_applied:

    st.info(
        f"🔎 Filters active: {len(filtered_df):,} of "
        f"{len(df):,} rows selected."
    )


# ============================================================
# FILTERED SQLITE DATABASE
# ============================================================

if st.session_state.filtered_connection is None:

    filtered_connection = sqlite3.connect(
        ":memory:",
        check_same_thread=False
    )

    st.session_state.filtered_connection = filtered_connection

else:

    filtered_connection = (
        st.session_state.filtered_connection
    )


filtered_df.to_sql(
    "sales",
    filtered_connection,
    index=False,
    if_exists="replace"
)


# ============================================================
# FILTERED COLUMN TYPES
# ============================================================

filtered_numeric_columns = (
    filtered_df.select_dtypes(include=np.number)
    .columns
    .tolist()
)

filtered_categorical_columns = (
    filtered_df.select_dtypes(
        include=["object", "category", "bool"]
    )
    .columns
    .tolist()
)

filtered_date_columns = detect_date_columns(
    filtered_df
)


# ============================================================
# DATA QUALITY
# ============================================================

missing_values = int(
    filtered_df.isna().sum().sum()
)

duplicate_rows = int(
    filtered_df.duplicated().sum()
)


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.subheader("📋 Dataset Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Rows", f"{len(filtered_df):,}")

c2.metric(
    "Columns",
    f"{len(filtered_df.columns):,}"
)

c3.metric(
    "Numerical Columns",
    f"{len(filtered_numeric_columns):,}"
)

c4.metric(
    "Missing Values",
    f"{missing_values:,}"
)


# ============================================================
# DATA QUALITY
# ============================================================

with st.expander("🔍 Data Quality Check"):

    q1, q2, q3 = st.columns(3)

    q1.metric(
        "Missing Values",
        missing_values
    )

    q2.metric(
        "Duplicate Rows",
        duplicate_rows
    )

    q3.metric(
        "Unique Rows",
        len(filtered_df.drop_duplicates())
    )


# ============================================================
# AI DATASET SUMMARY
# ============================================================

if generate_dataset_summary is not None:

    if (
        st.session_state.summary_generated_for
        != file_name
    ):

        try:

            with st.spinner(
                "🤖 Generating AI dataset summary..."
            ):

                summary = generate_dataset_summary(df)

                st.session_state.dataset_summary = summary

                st.session_state.summary_generated_for = file_name

        except Exception:

            st.session_state.dataset_summary = (
                "AI summary is temporarily unavailable."
            )

            st.session_state.summary_generated_for = file_name


    if st.session_state.dataset_summary:

        with st.expander(
            "🤖 AI Dataset Summary",
            expanded=True
        ):

            st.markdown(
                st.session_state.dataset_summary
            )


# ============================================================
# TABS
# ============================================================

(
    tab_ask,
    tab_dataset,
    tab_eda,
    tab_visualization,
    tab_recommendations,
    tab_insights,
    tab_dashboard,
    tab_anomaly,
    tab_report
) = st.tabs(
    [
        "💬 Ask Data",
        "📊 Dataset",
        "📈 EDA",
        "🎨 Visualization",
        "🤖 AI Recommendations",
        "🧠 Business Insights",
        "📊 Dashboard Builder",
        "🚨 Anomalies",
        "📄 Report"
    ]
)


# ============================================================
# ASK DATA
# ============================================================

with tab_ask:

    st.header("💬 Ask Your Data")

    question = st.text_input(
        "What do you want to know?",
        placeholder="Example: What are the total sales?"
    )


    if st.button(
        "🔍 Analyze",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            try:

                with st.spinner(
                    "🤖 Generating SQL..."
                ):

                    sql = generate_sql(
                        question,
                        filtered_df
                    )


                st.session_state.last_question = question

                st.session_state.sql_query = sql


                result = pd.read_sql_query(
                    sql,
                    filtered_connection
                )


                st.session_state.query_result = result


            except Exception as e:

                st.error(
                    f"Analysis failed: {e}"
                )


    if st.session_state.sql_query:

        st.subheader("🧠 Generated SQL")

        st.code(
            st.session_state.sql_query,
            language="sql"
        )


    if st.session_state.query_result is not None:

        st.subheader("📊 Result")

        st.dataframe(
            st.session_state.query_result,
            width="stretch"
        )

        csv_data = (
            st.session_state.query_result
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            "⬇️ Download Result",
            csv_data,
            "query_result.csv",
            "text/csv"
        )


# ============================================================
# DATASET TAB
# ============================================================

with tab_dataset:

    st.header("📊 Dataset Explorer")

    preview_tab, info_tab, summary_tab = st.tabs(
        [
            "Preview",
            "Column Information",
            "Numerical Summary"
        ]
    )


    with preview_tab:

        st.dataframe(
            filtered_df,
            width="stretch",
            height=500
        )


    with info_tab:

        info_df = pd.DataFrame({

            "Column": filtered_df.columns,

            "Data Type": [
                str(dtype)
                for dtype in filtered_df.dtypes
            ],

            "Non-Null Values": [
                filtered_df[column].notna().sum()
                for column in filtered_df.columns
            ],

            "Missing Values": [
                filtered_df[column].isna().sum()
                for column in filtered_df.columns
            ],

            "Unique Values": [
                filtered_df[column].nunique()
                for column in filtered_df.columns
            ]

        })

        st.dataframe(
            info_df,
            width="stretch",
            hide_index=True
        )


    with summary_tab:

        if filtered_numeric_columns:

            st.dataframe(
                filtered_df[
                    filtered_numeric_columns
                ]
                .describe()
                .T,
                width="stretch"
            )

        else:

            st.info(
                "No numerical columns available."
            )


# ============================================================
# EDA TAB
# ============================================================

with tab_eda:

    st.header(
        "📈 Exploratory Data Analysis"
    )


    if filtered_numeric_columns:

        selected_numeric = st.selectbox(
            "Select numerical column",
            filtered_numeric_columns,
            key="eda_numeric"
        )

        fig = px.histogram(
            filtered_df,
            x=selected_numeric,
            title=f"Distribution of {selected_numeric}"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


        if len(filtered_numeric_columns) >= 2:

            correlation = (
                filtered_df[
                    filtered_numeric_columns
                ]
                .corr()
            )

            corr_fig = px.imshow(
                correlation,
                text_auto=True,
                title="Correlation Matrix"
            )

            st.plotly_chart(
                corr_fig,
                width="stretch"
            )

    else:

        st.info(
            "No numerical columns available."
        )


# ============================================================
# VISUALIZATION TAB
# ============================================================

with tab_visualization:

    st.header(
        "🎨 Custom Visualization"
    )

    chart_type = st.selectbox(
        "Choose visualization",
        [
            "Bar Chart",
            "Line Chart",
            "Pie Chart",
            "Scatter Plot",
            "Histogram",
            "Box Plot",
            "Area Chart"
        ]
    )


    if chart_type == "Bar Chart":

        if (
            filtered_categorical_columns
            and filtered_numeric_columns
        ):

            x = st.selectbox(
                "Category",
                filtered_categorical_columns,
                key="bar_x"
            )

            y = st.selectbox(
                "Value",
                filtered_numeric_columns,
                key="bar_y"
            )

            grouped_df = (
                filtered_df
                .groupby(x, as_index=False)[y]
                .sum()
            )

            fig = px.bar(
                grouped_df,
                x=x,
                y=y,
                title=f"{y} by {x}"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    elif chart_type == "Line Chart":

        if filtered_numeric_columns:

            x_options = (
                filtered_date_columns
                + filtered_categorical_columns
                + filtered_numeric_columns
            )

            x = st.selectbox(
                "X-axis",
                x_options,
                key="line_x"
            )

            y = st.selectbox(
                "Y-axis",
                filtered_numeric_columns,
                key="line_y"
            )

            fig = px.line(
                filtered_df,
                x=x,
                y=y,
                markers=True
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    elif chart_type == "Pie Chart":

        if (
            filtered_categorical_columns
            and filtered_numeric_columns
        ):

            names = st.selectbox(
                "Category",
                filtered_categorical_columns,
                key="pie_names"
            )

            values = st.selectbox(
                "Values",
                filtered_numeric_columns,
                key="pie_values"
            )

            grouped_df = (
                filtered_df
                .groupby(names, as_index=False)[values]
                .sum()
            )

            fig = px.pie(
                grouped_df,
                names=names,
                values=values
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    elif chart_type == "Scatter Plot":

        if len(filtered_numeric_columns) >= 2:

            x = st.selectbox(
                "X-axis",
                filtered_numeric_columns,
                key="scatter_x"
            )

            y = st.selectbox(
                "Y-axis",
                filtered_numeric_columns,
                key="scatter_y"
            )

            fig = px.scatter(
                filtered_df,
                x=x,
                y=y
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    elif chart_type == "Histogram":

        if filtered_numeric_columns:

            column = st.selectbox(
                "Column",
                filtered_numeric_columns,
                key="hist_column"
            )

            fig = px.histogram(
                filtered_df,
                x=column
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    elif chart_type == "Box Plot":

        if filtered_numeric_columns:

            column = st.selectbox(
                "Column",
                filtered_numeric_columns,
                key="box_column"
            )

            fig = px.box(
                filtered_df,
                y=column
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    elif chart_type == "Area Chart":

        if filtered_numeric_columns:

            x_options = (
                filtered_date_columns
                + filtered_categorical_columns
                + filtered_numeric_columns
            )

            x = st.selectbox(
                "X-axis",
                x_options,
                key="area_x"
            )

            y = st.selectbox(
                "Y-axis",
                filtered_numeric_columns,
                key="area_y"
            )

            fig = px.area(
                filtered_df,
                x=x,
                y=y
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


# ============================================================
# AI CHART RECOMMENDATION ENGINE
# ============================================================

def generate_chart_recommendations(dataframe):

    recommendations = []

    numeric_cols = (
        dataframe.select_dtypes(include=np.number)
        .columns
        .tolist()
    )

    categorical_cols = (
        dataframe.select_dtypes(
            include=["object", "category", "bool"]
        )
        .columns
        .tolist()
    )

    detected_dates = detect_date_columns(dataframe)


    if detected_dates and numeric_cols:

        recommendations.append({

            "title": "📈 Trend Analysis",

            "chart": "Line Chart",

            "x": detected_dates[0],

            "y": numeric_cols[0],

            "reason": (
                "A date column and numerical column were "
                "detected, so a line chart can reveal "
                "changes over time."
            ),

            "priority": 1
        })


    if categorical_cols and numeric_cols:

        category_col = categorical_cols[0]

        value_col = numeric_cols[0]

        unique_count = (
            dataframe[category_col].nunique()
        )

        if unique_count <= 30:

            recommendations.append({

                "title": "📊 Category Comparison",

                "chart": "Bar Chart",

                "x": category_col,

                "y": value_col,

                "reason": (
                    f"Compare {value_col} across "
                    f"{category_col} categories."
                ),

                "priority": 2
            })


        if 2 <= unique_count <= 8:

            recommendations.append({

                "title": "🥧 Category Contribution",

                "chart": "Pie Chart",

                "x": category_col,

                "y": value_col,

                "reason": (
                    "A small number of categories makes "
                    "a pie chart suitable for contribution "
                    "analysis."
                ),

                "priority": 3
            })


    if len(numeric_cols) >= 2:

        recommendations.append({

            "title": "🔵 Variable Relationship",

            "chart": "Scatter Plot",

            "x": numeric_cols[0],

            "y": numeric_cols[1],

            "reason": (
                "Two numerical columns can be compared "
                "to identify relationships or patterns."
            ),

            "priority": 4
        })


    if numeric_cols:

        recommendations.append({

            "title": "📊 Distribution Analysis",

            "chart": "Histogram",

            "x": numeric_cols[0],

            "y": None,

            "reason": (
                "A histogram helps understand distribution "
                "and spread."
            ),

            "priority": 5
        })


        recommendations.append({

            "title": "📦 Outlier Analysis",

            "chart": "Box Plot",

            "x": None,

            "y": numeric_cols[0],

            "reason": (
                "A box plot helps identify unusual values "
                "and potential outliers."
            ),

            "priority": 6
        })


    return sorted(
        recommendations,
        key=lambda item: item["priority"]
    )


# ============================================================
# AI RECOMMENDATIONS TAB
# ============================================================

with tab_recommendations:

    st.header(
        "🤖 AI Chart Recommendations"
    )

    st.write(
        "Automatically recommends visualizations "
        "based on your dataset structure."
    )


    if st.button(
        "✨ Generate Recommendations",
        type="primary"
    ):

        st.session_state.chart_recommendations = (
            generate_chart_recommendations(
                filtered_df
            )
        )


    recommendations = (
        st.session_state.chart_recommendations
    )


    if not recommendations:

        st.info(
            "Click Generate Recommendations to begin."
        )

    else:

        for index, recommendation in enumerate(
            recommendations
        ):

            with st.container(border=True):

                st.subheader(
                    recommendation["title"]
                )

                st.write(
                    f"**Recommended Chart:** "
                    f"{recommendation['chart']}"
                )

                st.write(
                    recommendation["reason"]
                )

                if st.button(
                    "📊 Create This Chart",
                    key=f"recommend_chart_{index}"
                ):

                    st.session_state.recommended_charts = [
                        recommendation
                    ]

                    st.rerun()


        if st.session_state.recommended_charts:

            st.divider()

            st.subheader(
                "📊 Recommended Visualization"
            )

            recommendation = (
                st.session_state.recommended_charts[0]
            )

            chart = recommendation["chart"]

            x_col = recommendation["x"]

            y_col = recommendation["y"]


            if chart == "Line Chart":

                plot_df = filtered_df.copy()

                plot_df[x_col] = pd.to_datetime(
                    plot_df[x_col],
                    errors="coerce"
                )

                plot_df = (
                    plot_df
                    .dropna(subset=[x_col, y_col])
                    .sort_values(x_col)
                )

                fig = px.line(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    markers=True
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )


            elif chart == "Bar Chart":

                grouped_df = (
                    filtered_df
                    .groupby(x_col, as_index=False)[y_col]
                    .sum()
                    .sort_values(y_col, ascending=False)
                )

                fig = px.bar(
                    grouped_df,
                    x=x_col,
                    y=y_col
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )


            elif chart == "Pie Chart":

                grouped_df = (
                    filtered_df
                    .groupby(x_col, as_index=False)[y_col]
                    .sum()
                )

                fig = px.pie(
                    grouped_df,
                    names=x_col,
                    values=y_col
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )


            elif chart == "Scatter Plot":

                fig = px.scatter(
                    filtered_df,
                    x=x_col,
                    y=y_col
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )


            elif chart == "Histogram":

                fig = px.histogram(
                    filtered_df,
                    x=x_col
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )


            elif chart == "Box Plot":

                fig = px.box(
                    filtered_df,
                    y=y_col
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )


# ============================================================
# BUSINESS INSIGHTS ENGINE
# ============================================================

def generate_business_insights(dataframe):

    insights = []

    numeric_cols = (
        dataframe.select_dtypes(include=np.number)
        .columns
        .tolist()
    )

    categorical_cols = (
        dataframe.select_dtypes(
            include=["object", "category", "bool"]
        )
        .columns
        .tolist()
    )

    date_cols = detect_date_columns(dataframe)


    # --------------------------------------------------------
    # NUMERICAL INSIGHTS
    # --------------------------------------------------------

    for column in numeric_cols[:3]:

        series = (
            pd.to_numeric(
                dataframe[column],
                errors="coerce"
            )
            .dropna()
        )

        if series.empty:
            continue


        insights.append({
            "type": "metric",
            "title": f"💰 Total {column}",
            "value": series.sum(),
            "description": (
                f"The total value of {column} is "
                f"{series.sum():,.2f}."
            )
        })


        insights.append({
            "type": "metric",
            "title": f"📊 Average {column}",
            "value": series.mean(),
            "description": (
                f"The average value of {column} is "
                f"{series.mean():,.2f}."
            )
        })


        insights.append({
            "type": "text",
            "title": f"📈 Range of {column}",
            "description": (
                f"{column} ranges from "
                f"{series.min():,.2f} to "
                f"{series.max():,.2f}."
            )
        })


    # --------------------------------------------------------
    # BEST / LOWEST CATEGORY
    # --------------------------------------------------------

    if categorical_cols and numeric_cols:

        category_col = categorical_cols[0]
        value_col = numeric_cols[0]

        unique_count = (
            dataframe[category_col]
            .nunique()
        )


        if 2 <= unique_count <= 50:

            grouped = (
                dataframe
                .groupby(category_col)[value_col]
                .sum()
                .sort_values(
                    ascending=False
                )
            )


            if not grouped.empty:

                best_category = grouped.index[0]

                best_value = grouped.iloc[0]

                lowest_category = grouped.index[-1]

                lowest_value = grouped.iloc[-1]


                insights.append({
                    "type": "text",
                    "title": "🏆 Best Performing Category",
                    "description": (
                        f"**{best_category}** has the highest "
                        f"total {value_col} at "
                        f"**{best_value:,.2f}**."
                    )
                })


                insights.append({
                    "type": "text",
                    "title": "📉 Lowest Performing Category",
                    "description": (
                        f"**{lowest_category}** has the lowest "
                        f"total {value_col} at "
                        f"**{lowest_value:,.2f}**."
                    )
                })


    # --------------------------------------------------------
    # TREND ANALYSIS
    # --------------------------------------------------------

    if date_cols and numeric_cols:

        date_col = date_cols[0]
        value_col = numeric_cols[0]

        trend_df = dataframe[
            [date_col, value_col]
        ].copy()


        trend_df[date_col] = pd.to_datetime(
            trend_df[date_col],
            errors="coerce"
        )


        trend_df[value_col] = pd.to_numeric(
            trend_df[value_col],
            errors="coerce"
        )


        trend_df = trend_df.dropna()


        if len(trend_df) >= 2:

            trend_df = trend_df.sort_values(
                date_col
            )


            first_value = (
                trend_df[value_col].iloc[0]
            )

            last_value = (
                trend_df[value_col].iloc[-1]
            )


            if first_value != 0:

                percentage_change = (
                    (
                        last_value - first_value
                    )
                    / abs(first_value)
                    * 100
                )


                if percentage_change > 5:

                    trend_text = (
                        f"{value_col} increased by "
                        f"approximately "
                        f"{percentage_change:.1f}% "
                        f"between the first and last "
                        f"recorded values."
                    )

                elif percentage_change < -5:

                    trend_text = (
                        f"{value_col} decreased by "
                        f"approximately "
                        f"{abs(percentage_change):.1f}% "
                        f"between the first and last "
                        f"recorded values."
                    )

                else:

                    trend_text = (
                        f"{value_col} remained relatively "
                        f"stable over the available period."
                    )


                insights.append({
                    "type": "text",
                    "title": "📈 Trend Insight",
                    "description": trend_text
                })


    # --------------------------------------------------------
    # OUTLIER INSIGHT
    # --------------------------------------------------------

    if numeric_cols:

        value_col = numeric_cols[0]

        series = (
            pd.to_numeric(
                dataframe[value_col],
                errors="coerce"
            )
            .dropna()
        )


        if len(series) > 3:

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outlier_count = (
                (
                    (series < lower_bound)
                    |
                    (series > upper_bound)
                )
                .sum()
            )


            if outlier_count > 0:

                insights.append({
                    "type": "text",
                    "title": "⚠️ Unusual Values Detected",
                    "description": (
                        f"{outlier_count:,} records contain "
                        f"unusual {value_col} values based "
                        f"on the IQR method. Review these "
                        f"records for high-value transactions, "
                        f"data entry errors or exceptional "
                        f"events."
                    )
                })


    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    if categorical_cols and numeric_cols:

        insights.append({
            "type": "recommendation",
            "title": "💡 Recommended Action",
            "description": (
                "Compare high-performing and low-performing "
                "categories to identify factors contributing "
                "to the performance gap. Investigate unusual "
                "values before making major business decisions."
            )
        })


    return insights


# ============================================================
# BUSINESS INSIGHTS TAB
# ============================================================

with tab_insights:

    st.header(
        "🧠 Automated Business Insights"
    )

    st.write(
        "The system automatically analyzes your filtered "
        "data and highlights important findings."
    )


    if filtered_df.empty:

        st.warning(
            "No data is available for generating insights."
        )

    else:

        if st.button(
            "🧠 Generate Business Insights",
            type="primary"
        ):

            st.session_state.business_insights = (
                generate_business_insights(
                    filtered_df
                )
            )


        insights = (
            st.session_state.business_insights
        )


        if not insights:

            st.info(
                "Click **Generate Business Insights** "
                "to analyze the dataset."
            )

        else:

            st.success(
                f"Generated {len(insights)} "
                "business insights."
            )


            # KPI METRICS

            metric_insights = [
                insight
                for insight in insights
                if insight["type"] == "metric"
            ]


            if metric_insights:

                st.subheader(
                    "📊 Key Metrics"
                )


                metric_columns = st.columns(
                    min(3, len(metric_insights))
                )


                for index, insight in enumerate(
                    metric_insights[:3]
                ):

                    metric_columns[
                        index % len(metric_columns)
                    ].metric(
                        insight["title"],
                        f"{insight['value']:,.2f}"
                    )


            # TEXT INSIGHTS

            text_insights = [
                insight
                for insight in insights
                if insight["type"] == "text"
            ]


            if text_insights:

                st.subheader(
                    "🔎 Key Findings"
                )


                for insight in text_insights:

                    with st.container(border=True):

                        st.markdown(
                            f"### {insight['title']}"
                        )

                        st.markdown(
                            insight["description"]
                        )


            # RECOMMENDATIONS

            recommendations = [
                insight
                for insight in insights
                if insight["type"] == "recommendation"
            ]


            if recommendations:

                st.subheader(
                    "💡 Recommendations"
                )


                for insight in recommendations:

                    st.success(
                        f"{insight['title']}\n\n"
                        f"{insight['description']}"
                    )


# ============================================================
# DASHBOARD BUILDER
# ============================================================

with tab_dashboard:

    st.header(
        "📊 AI Dashboard Builder"
    )

    st.write(
        "Ask multiple questions and create a dashboard."
    )


    for index in range(
        len(st.session_state.dashboard_questions)
    ):

        question_value = st.text_input(
            f"Question {index + 1}",
            value=st.session_state.dashboard_questions[index],
            key=f"dashboard_question_{index}"
        )

        st.session_state.dashboard_questions[
            index
        ] = question_value


    if st.button("➕ Add Question"):

        st.session_state.dashboard_questions.append("")

        st.rerun()


    if st.button(
        "🚀 Build Dashboard",
        type="primary"
    ):

        valid_questions = [
            question.strip()
            for question in (
                st.session_state.dashboard_questions
            )
            if question.strip()
        ]


        if not valid_questions:

            st.warning(
                "Enter at least one question."
            )

        else:

            components = []


            for dashboard_question in valid_questions:

                try:

                    sql = generate_sql(
                        dashboard_question,
                        filtered_df
                    )

                    result = pd.read_sql_query(
                        sql,
                        filtered_connection
                    )

                    components.append({
                        "question": dashboard_question,
                        "sql": sql,
                        "data": result
                    })

                except Exception as e:

                    st.error(
                        f"Could not process "
                        f"'{dashboard_question}': {e}"
                    )


            st.session_state.dashboard_components = components


    if st.session_state.dashboard_components:

        st.divider()

        st.markdown(
            '<div class="dashboard-title">'
            '📊 Generated Dashboard'
            '</div>',
            unsafe_allow_html=True
        )


        for component in (
            st.session_state.dashboard_components
        ):

            st.subheader(
                component["question"]
            )

            st.dataframe(
                component["data"],
                width="stretch"
            )


# ============================================================
# ANOMALY DETECTION
# ============================================================

with tab_anomaly:

    st.header(
        "🚨 Anomaly Detection"
    )


    if not filtered_numeric_columns:

        st.info(
            "No numerical columns available."
        )

    else:

        anomaly_column = st.selectbox(
            "Select numerical column",
            filtered_numeric_columns,
            key="anomaly_column"
        )

        method = st.selectbox(
            "Detection Method",
            ["IQR", "Z-Score"],
            key="anomaly_method"
        )


        if method == "IQR":

            q1 = filtered_df[
                anomaly_column
            ].quantile(0.25)

            q3 = filtered_df[
                anomaly_column
            ].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            anomalies = filtered_df[
                (
                    filtered_df[anomaly_column] < lower
                )
                |
                (
                    filtered_df[anomaly_column] > upper
                )
            ]

        else:

            mean = filtered_df[
                anomaly_column
            ].mean()

            std = filtered_df[
                anomaly_column
            ].std()


            if std == 0 or pd.isna(std):

                anomalies = pd.DataFrame()

            else:

                z_scores = (
                    (
                        filtered_df[anomaly_column]
                        - mean
                    )
                    / std
                )

                anomalies = filtered_df[
                    z_scores.abs() > 3
                ]


        st.metric(
            "Detected Anomalies",
            len(anomalies)
        )


        if not anomalies.empty:

            st.warning(
                f"⚠️ {len(anomalies):,} unusual records "
                "were detected."
            )

            st.info(
                f"These records are unusual because their "
                f"**{anomaly_column}** values fall outside "
                f"the expected range using the **{method}** "
                "method. They may represent exceptional "
                "transactions, genuine outliers or data "
                "quality issues."
            )

            st.dataframe(
                anomalies,
                width="stretch"
            )

        else:

            st.success(
                "No significant anomalies detected."
            )


# ============================================================
# REPORT
# ============================================================

with tab_report:

    st.header(
        "📄 Analyst Report"
    )


    if st.button(
        "📝 Generate Report",
        type="primary"
    ):

        report = f"""# AI Data Analyst Report

## Dataset Overview

- Dataset: {file_name}
- Original Rows: {len(df):,}
- Filtered Rows: {len(filtered_df):,}
- Columns: {len(filtered_df.columns):,}
- Numerical Columns: {len(filtered_numeric_columns):,}
- Categorical Columns: {len(filtered_categorical_columns):,}
- Missing Values: {missing_values:,}
- Duplicate Rows: {duplicate_rows:,}

## Filters

Filters Applied: {"Yes" if st.session_state.filters_applied else "No"}

## Business Insights

"""


        if st.session_state.business_insights:

            for insight in (
                st.session_state.business_insights
            ):

                report += (
                    f"### {insight['title']}\n"
                    f"{insight['description']}\n\n"
                )

        else:

            report += (
                "Business insights have not been generated yet.\n\n"
            )


        report += "## AI Chart Recommendations\n\n"


        if st.session_state.chart_recommendations:

            for recommendation in (
                st.session_state.chart_recommendations
            ):

                report += (
                    f"- **{recommendation['title']}**\n"
                    f"  - Chart: "
                    f"{recommendation['chart']}\n"
                    f"  - Reason: "
                    f"{recommendation['reason']}\n\n"
                )

        else:

            report += (
                "Chart recommendations have not been generated yet.\n\n"
            )


        report += "## Numerical Summary\n\n"


        if filtered_numeric_columns:

            report += (
                filtered_df[
                    filtered_numeric_columns
                ]
                .describe()
                .round(2)
                .to_markdown()
            )

        else:

            report += (
                "No numerical columns available."
            )


        st.session_state.generated_report = report


    if st.session_state.generated_report:

        st.markdown(
            st.session_state.generated_report
        )

        st.download_button(
            "⬇️ Download Report",
            data=st.session_state.generated_report,
            file_name="ai_data_analyst_report.md",
            mime="text/markdown"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "📊 AI Data Analyst | "
    "AI Summary • NL → SQL • EDA • Visualization • "
    "Smart Filters • AI Recommendations • Business Insights • "
    "Dashboard • Anomalies • Reports"
)