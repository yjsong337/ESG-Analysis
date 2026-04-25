import operator
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="ESG and Revenue Analysis",
    layout="wide"
)


@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Data file not found: {file_path}")
        st.info("Please make sure the CSV file is stored in the same folder as app.py.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

    df.columns = [str(col).strip() for col in df.columns]
    return df


def format_number(value):
    if pd.isna(value):
        return "N/A"

    value = float(value)

    if operator.ge(abs(value), 1000000000):
        return f"{value / 1000000000:.2f}B"
    if operator.ge(abs(value), 1000000):
        return f"{value / 1000000:.2f}M"
    if operator.ge(abs(value), 1000):
        return f"{value / 1000:.2f}K"

    return f"{value:.2f}"


def calculate_correlation(df, x_col, y_col):
    temp = df[[x_col, y_col]].dropna()

    if operator.lt(len(temp), 2):
        return None

    if operator.lt(temp[x_col].nunique(), 2):
        return None

    if operator.lt(temp[y_col].nunique(), 2):
        return None

    correlation = temp[x_col].corr(temp[y_col])

    if pd.isna(correlation):
        return None

    return correlation


def fit_linear_model(df, x_col, y_col):
    temp = df[[x_col, y_col]].dropna()

    if operator.lt(len(temp), 2):
        return None

    if operator.lt(temp[x_col].nunique(), 2):
        return None

    if operator.lt(temp[y_col].nunique(), 2):
        return None

    x = temp[x_col].astype(float).to_numpy()
    y = temp[y_col].astype(float).to_numpy()

    try:
        slope, intercept = np.polyfit(x, y, 1)
    except Exception:
        return None

    if pd.isna(slope) or pd.isna(intercept):
        return None

    return slope, intercept


def get_correlation_text(correlation_value):
    if correlation_value is None or pd.isna(correlation_value):
        return "not available"
    if operator.gt(correlation_value, 0.5):
        return "moderately to strongly positive"
    if operator.gt(correlation_value, 0.1):
        return "weakly positive"
    if operator.lt(correlation_value, -0.5):
        return "moderately to strongly negative"
    if operator.lt(correlation_value, -0.1):
        return "weakly negative"
    return "very weak or close to zero"


st.title("ESG and Revenue Analysis App")
st.write("This app explores how ESG indicators are associated with company revenue across regions and years.")
st.write("Target users: ESG focused investors, corporate strategy managers, and sustainability analysts.")
st.write("How to use: choose an ESG indicator, region, and year range in the sidebar, then explore the tabs for patterns, rankings, and simple prediction.")
st.write("Important note: this app shows association in the current sample and does not prove causation.")

df = load_data("ESG_sta1_selected_one_company_per_region.csv")

COMPANY_COL = "CompanyName"
REGION_COL = "Region"
YEAR_COL = "Year"
REVENUE_COL = "Revenue"
ESG_OVERALL_COL = "ESG_Overall"
ENV_COL = "ESG_Environmental"
SOC_COL = "ESG_Social"
GOV_COL = "ESG_Governance"

required_columns = [
    COMPANY_COL,
    REGION_COL,
    YEAR_COL,
    REVENUE_COL,
    ESG_OVERALL_COL,
    ENV_COL,
    SOC_COL,
    GOV_COL
]

missing_columns = [col for col in required_columns if col not in df.columns]

if len(missing_columns) != 0:
    st.error("Missing required columns: " + ", ".join(missing_columns))
    st.write("Detected columns in your file:")
    st.write(list(df.columns))
    st.stop()

df[YEAR_COL] = pd.to_numeric(df[YEAR_COL], errors="coerce")
df[REVENUE_COL] = pd.to_numeric(df[REVENUE_COL], errors="coerce")
df[ESG_OVERALL_COL] = pd.to_numeric(df[ESG_OVERALL_COL], errors="coerce")
df[ENV_COL] = pd.to_numeric(df[ENV_COL], errors="coerce")
df[SOC_COL] = pd.to_numeric(df[SOC_COL], errors="coerce")
df[GOV_COL] = pd.to_numeric(df[GOV_COL], errors="coerce")

esg_options = {
    "ESG Overall Score": ESG_OVERALL_COL,
    "Environmental Score": ENV_COL,
    "Social Score": SOC_COL,
    "Governance Score": GOV_COL
}

ranking_options = {
    "Revenue": REVENUE_COL,
    "ESG Overall Score": ESG_OVERALL_COL,
    "Environmental Score": ENV_COL,
    "Social Score": SOC_COL,
    "Governance Score": GOV_COL
}

st.sidebar.header("Filter Panel")

selected_esg_label = st.sidebar.selectbox(
    "Choose ESG indicator",
    list(esg_options.keys())
)
selected_esg_col = esg_options[selected_esg_label]

all_regions = sorted(df[REGION_COL].dropna().astype(str).unique().tolist())

selected_regions = st.sidebar.multiselect(
    "Choose region",
    all_regions,
    default=all_regions
)

year_series = df[YEAR_COL].dropna()

if len(year_series) == 0:
    st.error("No valid year values found.")
    st.stop()

min_year = int(year_series.min())
max_year = int(year_series.max())

selected_years = st.sidebar.slider(
    "Choose year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

filtered_df = df.copy()

if len(selected_regions) != 0:
    filtered_df = filtered_df[filtered_df[REGION_COL].astype(str).isin(selected_regions)]
else:
    filtered_df = filtered_df.iloc[0:0]

filtered_df = filtered_df[filtered_df[YEAR_COL].ge(selected_years  [0])]
filtered_df = filtered_df[filtered_df[YEAR_COL].le(selected_years  [1])]

if len(filtered_df) == 0:
    st.warning("No data available after filtering. Try selecting more regions or widening the year range.")
    st.stop()

average_revenue = filtered_df[REVENUE_COL].mean()
average_esg = filtered_df[selected_esg_col].mean()
average_esg_overall = filtered_df[ESG_OVERALL_COL].mean()

correlation_value = calculate_correlation(filtered_df, selected_esg_col, REVENUE_COL)
model_result = fit_linear_model(filtered_df, selected_esg_col, REVENUE_COL)

record_count = len(filtered_df)
region_count = filtered_df[REGION_COL].dropna().astype(str).nunique()
company_count = filtered_df[COMPANY_COL].dropna().astype(str).nunique()

st.subheader("Current Sample Overview")

s1, s2, s3 = st.columns(3)

with s1:
    st.metric("Records", record_count)

with s2:
    st.metric("Regions", region_count)

with s3:
    st.metric("Companies", company_count)

st.subheader("Summary Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Average Revenue", format_number(average_revenue))

with col2:
    if pd.isna(average_esg):
        st.metric(f"Average {selected_esg_label}", "N/A")
    else:
        st.metric(f"Average {selected_esg_label}", f"{average_esg:.2f}")

with col3:
    if pd.isna(average_esg_overall):
        st.metric("Average ESG Overall Score", "N/A")
    else:
        st.metric("Average ESG Overall Score", f"{average_esg_overall:.2f}")

with col4:
    if correlation_value is None or pd.isna(correlation_value):
        st.metric("Correlation", "N/A")
    else:
        st.metric("Correlation", f"{correlation_value:.2f}")

st.subheader("Benchmark Comparison")

high_esg_df = filtered_df[filtered_df[ESG_OVERALL_COL].ge(average_esg_overall)]
low_esg_df = filtered_df[filtered_df[ESG_OVERALL_COL].lt(average_esg_overall)]

b1, b2, b3 = st.columns(3)

with b1:
    if pd.isna(average_esg_overall):
        st.metric("Average ESG Overall Score", "N/A")
    else:
        st.metric("Average ESG Overall Score", f"{average_esg_overall:.2f}")

with b2:
    if len(high_esg_df) == 0:
        st.metric("High ESG Group Avg Revenue", "N/A")
    else:
        st.metric("High ESG Group Avg Revenue", format_number(high_esg_df[REVENUE_COL].mean()))

with b3:
    if len(low_esg_df) == 0:
        st.metric("Low ESG Group Avg Revenue", "N/A")
    else:
        st.metric("Low ESG Group Avg Revenue", format_number(low_esg_df[REVENUE_COL].mean()))

if len(high_esg_df) != 0 and len(low_esg_df) != 0:
    revenue_gap = high_esg_df[REVENUE_COL].mean() - low_esg_df[REVENUE_COL].mean()
    st.write(f"Revenue gap between high ESG and low ESG groups: {format_number(revenue_gap)}")

    if operator.gt(revenue_gap, 0):
        st.success("Companies above the average ESG overall score tend to have higher average revenue in the current sample.")
    elif operator.lt(revenue_gap, 0):
        st.warning("Companies above the average ESG overall score tend to have lower average revenue in the current sample.")
    else:
        st.info("The average revenue difference between the two groups is very small.")

st.subheader("Dynamic Summary")

selected_region_text = ", ".join(selected_regions) if len(selected_regions) != 0 else "No region selected"
correlation_text = get_correlation_text(correlation_value)

st.write(f"In the current view, the app analyzes {len(filtered_df)} records across {selected_region_text} from {selected_years  [0]} to {selected_years  [1]}.")
st.write(f"The average revenue is {format_number(average_revenue)}.")

if pd.isna(average_esg):
    st.write(f"The average {selected_esg_label} score is not available.")
else:
    st.write(f"The average {selected_esg_label} score is {average_esg:.2f}.")

st.write(f"The relationship between {selected_esg_label} and revenue is {correlation_text} in the current sample.")

region_summary_df = (
    filtered_df.groupby(REGION_COL)[[REVENUE_COL, selected_esg_col]]
    .mean()
    .reset_index()
)

if len(region_summary_df) != 0:
    top_revenue_region = region_summary_df.sort_values(REVENUE_COL, ascending=False).iloc  [0][REGION_COL]
    top_esg_region = region_summary_df.sort_values(selected_esg_col, ascending=False).iloc  [0][REGION_COL]

    st.write(f"The region with the highest average revenue is {top_revenue_region}.")
    st.write(f"The region with the highest average {selected_esg_label} score is {top_esg_region}.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Overview", "Trends", "Relationship", "ESG Components", "Prediction", "Rankings"]
)

with tab1:
    st.subheader("Overview")

    preview_cols = [
        COMPANY_COL,
        REGION_COL,
        YEAR_COL,
        REVENUE_COL,
        selected_esg_col
    ]

    st.dataframe(filtered_df[preview_cols].head(10), use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        revenue_data = filtered_df[REVENUE_COL].dropna()

        if len(revenue_data) != 0:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(revenue_data, bins=12, color="skyblue", edgecolor="black")
            ax.set_title("Revenue Distribution")
            ax.set_xlabel("Revenue")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No valid revenue data.")

    with c2:
        esg_data = filtered_df[selected_esg_col].dropna()

        if len(esg_data) != 0:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(esg_data, bins=12, color="lightgreen", edgecolor="black")
            ax.set_title(f"{selected_esg_label} Distribution")
            ax.set_xlabel(selected_esg_label)
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No valid ESG data.")

with tab2:
    st.subheader("Trends")

    trend_df = (
        filtered_df.groupby(YEAR_COL)[[REVENUE_COL, selected_esg_col]]
        .mean()
        .reset_index()
        .sort_values(YEAR_COL)
    )

    if operator.lt(len(trend_df), 2):
        st.info("Not enough data points to show time trends.")
    else:
        fig, ax1 = plt.subplots(figsize=(9, 5))

        ax1.plot(
            trend_df[YEAR_COL],
            trend_df[REVENUE_COL],
            marker="o",
            color="blue"
        )
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Average Revenue", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")

        ax2 = ax1.twinx()
        ax2.plot(
            trend_df[YEAR_COL],
            trend_df[selected_esg_col],
            marker="s",
            color="green"
        )
        ax2.set_ylabel(selected_esg_label, color="green")
        ax2.tick_params(axis="y", labelcolor="green")

        plt.title("Average Revenue and ESG Trend by Year")
        st.pyplot(fig)
        plt.close(fig)

        st.dataframe(trend_df, use_container_width=True)

with tab3:
    st.subheader("Relationship")

    relationship_df = filtered_df[[selected_esg_col, REVENUE_COL]].dropna()

    if operator.lt(len(relationship_df), 2):
        st.info("Not enough valid data to show the relationship plot.")
    else:
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(
            relationship_df[selected_esg_col],
            relationship_df[REVENUE_COL],
            alpha=0.7,
            color="purple"
        )

        if model_result is not None:
            slope, intercept = model_result
            x_line = np.linspace(
                relationship_df[selected_esg_col].min(),
                relationship_df[selected_esg_col].max(),
                100
            )
            y_line = slope * x_line + intercept
            ax.plot(x_line, y_line, color="red", linewidth=2)

        ax.set_xlabel(selected_esg_label)
        ax.set_ylabel("Revenue")
        ax.set_title(f"{selected_esg_label} and Revenue")
        st.pyplot(fig)
        plt.close(fig)

        if correlation_value is None or pd.isna(correlation_value):
            st.write("Correlation is not available.")
        else:
            st.write(f"Correlation between {selected_esg_label} and revenue: {correlation_value:.2f}")

            if operator.gt(correlation_value, 0.5):
                st.success("The relationship is moderately to strongly positive in the current sample.")
            elif operator.gt(correlation_value, 0.1):
                st.info("The relationship is weakly positive in the current sample.")
            elif operator.lt(correlation_value, -0.5):
                st.warning("The relationship is moderately to strongly negative in the current sample.")
            elif operator.lt(correlation_value, -0.1):
                st.warning("The relationship is weakly negative in the current sample.")
            else:
                st.info("The relationship is very weak or close to zero in the current sample.")

        st.write("Interpretation note: this plot shows association in the filtered sample and should not be interpreted as causal proof.")

with tab4:
    st.subheader("ESG Components")

    component_df = pd.DataFrame(
        {
            "Component": ["Environmental", "Social", "Governance"],
            "Average Score": [
                filtered_df[ENV_COL].mean(),
                filtered_df[SOC_COL].mean(),
                filtered_df[GOV_COL].mean()
            ]
        }
    )

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        component_df["Component"],
        component_df["Average Score"],
        color=["#66c2a5", "#fc8d62", "#8da0cb"]
    )
    ax.set_title("Average ESG Component Scores")
    ax.set_ylabel("Score")
    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(component_df, use_container_width=True)

    component_trend_df = (
        filtered_df.groupby(YEAR_COL)[[ENV_COL, SOC_COL, GOV_COL]]
        .mean()
        .reset_index()
        .sort_values(YEAR_COL)
    )

    if operator.ge(len(component_trend_df), 2):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(component_trend_df[YEAR_COL], component_trend_df[ENV_COL], marker="o", label="Environmental")
        ax.plot(component_trend_df[YEAR_COL], component_trend_df[SOC_COL], marker="o", label="Social")
        ax.plot(component_trend_df[YEAR_COL], component_trend_df[GOV_COL], marker="o", label="Governance")
        ax.set_title("ESG Component Trends by Year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Average Score")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Not enough data points to show ESG component trends.")

with tab5:
    st.subheader("Prediction")

    model_for_prediction = fit_linear_model(filtered_df, ESG_OVERALL_COL, REVENUE_COL)

    if model_for_prediction is not None:
        slope, intercept = model_for_prediction

        valid_esg_series = filtered_df[ESG_OVERALL_COL].dropna()
        valid_revenue_series = filtered_df[REVENUE_COL].dropna()

        if len(valid_esg_series) == 0 or len(valid_revenue_series) == 0:
            st.info("Not enough valid data to support prediction.")
        else:
            esg_min = float(valid_esg_series.min())
            esg_max = float(valid_esg_series.max())
            revenue_min = float(valid_revenue_series.min())
            revenue_max = float(valid_revenue_series.max())

            st.write(f"Observed ESG Overall Score range in current sample: {esg_min:.2f} to {esg_max:.2f}")
            st.write(f"Observed revenue range in current sample: {format_number(revenue_min)} to {format_number(revenue_max)}")

            default_esg = filtered_df[ESG_OVERALL_COL].mean()
            default_revenue = filtered_df[REVENUE_COL].mean()

            if pd.isna(default_esg):
                default_esg = esg_min
            if pd.isna(default_revenue):
                default_revenue = revenue_min

            if operator.lt(default_esg, esg_min):
                default_esg = esg_min
            if operator.gt(default_esg, esg_max):
                default_esg = esg_max

            slider_step = (esg_max - esg_min) / 100
            if operator.le(slider_step, 0):
                slider_step = 0.1

            esg_input = st.slider(
                "Choose ESG Overall Score value",
                min_value=float(esg_min),
                max_value=float(esg_max),
                value=float(default_esg),
                step=float(slider_step)
            )

            predicted_revenue = slope * esg_input + intercept
            st.write(f"Estimated revenue based on the fitted model: {format_number(predicted_revenue)}")

            revenue_input = st.number_input(
                "Input revenue value",
                value=float(default_revenue)
            )

            if operator.lt(revenue_input, revenue_min):
                st.warning("This revenue input is below the observed sample range, so the estimated ESG value may be less reliable.")
            elif operator.gt(revenue_input, revenue_max):
                st.warning("This revenue input is above the observed sample range, so the estimated ESG value may be less reliable.")

            estimated_esg = None

            if np.isclose(slope, 0.0):
                st.info("The fitted line is too flat to estimate ESG reliably from revenue.")
            else:
                estimated_esg = (revenue_input - intercept) / slope
                st.write(f"Estimated ESG Overall Score based on the fitted model: {estimated_esg:.2f}")

            st.subheader("Simple Decision Guidance")

            if estimated_esg is not None and not pd.isna(average_esg_overall):
                if operator.ge(estimated_esg, average_esg_overall):
                    st.success(
                        f"The estimated ESG Overall Score is above the sample average of {average_esg_overall:.2f}. This may indicate relatively stronger ESG positioning."
                    )
                    st.write("Possible implication: the company may be more attractive to ESG focused investors and stronger in sustainability communication.")
                else:
                    st.warning(
                        f"The estimated ESG Overall Score is below the sample average of {average_esg_overall:.2f}."
                    )
                    st.write("Possible implication: the company may need to improve ESG performance to strengthen stakeholder confidence.")

            if not pd.isna(average_esg_overall):
                if operator.ge(esg_input, average_esg_overall):
                    st.info("The selected ESG input is above the sample average. Under the fitted model, this corresponds to a relatively stronger expected revenue level.")
                else:
                    st.info("The selected ESG input is below the sample average. Under the fitted model, this corresponds to a relatively weaker expected revenue level.")

            st.write("This prediction is based on a simple linear relationship and should be interpreted as exploratory analysis rather than causal proof.")
            st.write("This output should not be used as investment advice.")

    else:
        st.info("Not enough valid data to fit a linear model for prediction.")

with tab6:
    st.subheader("Rankings")

    ranking_df = filtered_df[
        [COMPANY_COL, REGION_COL, YEAR_COL, REVENUE_COL, ESG_OVERALL_COL, ENV_COL, SOC_COL, GOV_COL]
    ].copy()

    available_top_n = [n for n in [3, 5, 10] if operator.le(n, len(ranking_df))]
    if len(available_top_n) == 0:
        available_top_n = [len(ranking_df)]

    selected_ranking_label = st.selectbox(
        "Choose ranking metric",
        list(ranking_options.keys())
    )
    selected_ranking_col = ranking_options[selected_ranking_label]

    selected_top_n = st.selectbox(
        "Choose number of rows to display",
        available_top_n,
        index=0
    )

    top_ranked_df = ranking_df.sort_values(selected_ranking_col, ascending=False).head(selected_top_n)
    top_revenue_df = ranking_df.sort_values(REVENUE_COL, ascending=False).head(selected_top_n)
    top_esg_df = ranking_df.sort_values(ESG_OVERALL_COL, ascending=False).head(selected_top_n)

    r1, r2 = st.columns(2)

    with r1:
        st.subheader(f"Top {selected_top_n} by {selected_ranking_label}")
        st.dataframe(top_ranked_df, use_container_width=True)

    with r2:
        st.subheader(f"Top {selected_top_n} by ESG Overall Score")
        st.dataframe(top_esg_df, use_container_width=True)

    ranking_df["Revenue Rank"] = ranking_df[REVENUE_COL].rank(ascending=False, method="dense")
    ranking_df["ESG Rank"] = ranking_df[ESG_OVERALL_COL].rank(ascending=False, method="dense")
    ranking_df["Rank Gap"] = (ranking_df["Revenue Rank"] - ranking_df["ESG Rank"]).abs()

    mismatch_df = ranking_df.sort_values("Rank Gap", ascending=False).head(selected_top_n)

    st.subheader("Largest Revenue and ESG Ranking Gaps")
    st.dataframe(mismatch_df, use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered data as CSV",
        data=csv_data,
        file_name="filtered_esg_revenue_data.csv",
        mime="text/csv"
    )

with st.expander("Show detected columns"):
    st.write(list(df.columns))