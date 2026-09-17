import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import warnings

warnings.filterwarnings("ignore")

# 1. Page Configuration & Custom CSS
st.set_page_config(
    page_title="Medical Insurance Payout Dashboard",
    layout="wide",
    page_icon="📊",
)

st.markdown(
    """
    <style>
    .main { background-color: #f8f9fa; }
    .kpi-box {
        background-color: white; 
        padding: 20px; 
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        text-align: center; 
        border-top: 4px solid #3498db;
        margin-bottom: 10px;
    }
    .kpi-box h5 {
        margin: 0;
        font-size: 1rem;
        color: #666;
    }
    .kpi-box h3 {
        margin: 5px 0 0 0;
        font-size: 1.8rem;
        color: #111;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 2. Safe Data Loader & Preprocessing
@st.cache_data
def load_insurance_data():
    try:
        df_raw = pd.read_csv("expenses.csv")
    except FileNotFoundError:
        np.random.seed(42)
        n_samples = 1338
        df_raw = pd.DataFrame({
            "age": np.random.randint(18, 65, n_samples),
            "sex": np.random.choice(["male", "female"], n_samples),
            "bmi": np.random.normal(30, 6, n_samples),
            "children": np.random.randint(0, 6, n_samples),
            "smoker": np.random.choice(
                ["yes", "no"], n_samples, p=[0.2, 0.8]
            ),
            "region": np.random.choice(
                ["southwest", "southeast", "northwest", "northeast"], n_samples
            ),
            "charges": np.random.normal(13270, 12000, n_samples).clip(
                1000, 64000
            ),
        })

    # Clean column headers
    df_raw.columns = df_raw.columns.str.lower().str.strip()

    # Cast numeric columns cleanly (handles text $ or commas in CSVs)
    numeric_cols = ["charges", "bmi", "age", "children"]
    for col in numeric_cols:
        if col in df_raw.columns:
            if (
                df_raw[col].dtype == "object"
                or df_raw[col].dtype.name == "string"
            ):
                df_raw[col] = (
                    df_raw[col]
                    .astype(str)
                    .str.replace("$", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                )
            df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

    # Clean text columns
    text_cols = ["sex", "smoker", "region"]
    for col in text_cols:
        if col in df_raw.columns:
            df_raw[col] = df_raw[col].astype(str).str.lower().str.strip()

    return df_raw.dropna(subset=["charges"])


# Load dataset
df = load_insurance_data()

# 3. Defensive Schema Validation Engine
required_columns = [
    "age",
    "sex",
    "bmi",
    "children",
    "smoker",
    "region",
    "charges",
]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(
        f"❌ **Data Schema Error:** Missing required columns: `{missing_columns}`"
    )
    st.write(
        "🕵️‍♂️ **Available columns detected in dataset:**", df.columns.tolist()
    )
    st.info(
        "Please adjust your dataset column headers to match the expected schema."
    )
    st.stop()

# 4. Sidebar Controls (Real-Time Filters)
st.sidebar.title("📊 Filter Engine")

regions_avail = sorted(df["region"].unique().tolist())
smokers_avail = sorted(df["smoker"].unique().tolist())
genders_avail = sorted(df["sex"].unique().tolist())

selected_regions = st.sidebar.multiselect(
    "Region", options=regions_avail, default=regions_avail
)
selected_smokers = st.sidebar.multiselect(
    "Smoker Status", options=smokers_avail, default=smokers_avail
)
selected_genders = st.sidebar.multiselect(
    "Gender", options=genders_avail, default=genders_avail
)

# Dynamic Filtering
df_filtered = df[
    (df["region"].isin(selected_regions))
    & (df["smoker"].isin(selected_smokers))
    & (df["sex"].isin(selected_genders))
]

# 5. Main Application Header
st.title("Medical Insurance Payout Business Intelligence Dashboard")
st.markdown("Operational Risk Management and Actuarial Analysis Matrix.")
st.markdown("---")

# Empty Filter State Shield
if len(df_filtered) == 0:
    st.warning(
        "⚠️ No records match the active filter criteria. Please adjust your sidebar selections."
    )
    st.stop()

# 6. Core Operational KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_enrolled = len(df_filtered)
avg_payout = df_filtered["charges"].mean() if total_enrolled > 0 else 0.0
total_payout_m = (
    df_filtered["charges"].sum() / 1e6 if total_enrolled > 0 else 0.0
)
smk_ratio = (
    (df_filtered["smoker"] == "yes").sum() / total_enrolled * 100
    if total_enrolled > 0
    else 0.0
)

with kpi1:
    st.markdown(
        f'<div class="kpi-box"><h5>Total Enrolled</h5><h3>{total_enrolled:,}</h3></div>',
        unsafe_allow_html=True,
    )
with kpi2:
    st.markdown(
        f'<div class="kpi-box"'
        ' style="border-top-color:#e74c3c;"><h5>Avg Payout'
        f" Charge</h5><h3>${avg_payout:,.2f}</h3></div>",
        unsafe_allow_html=True,
    )
with kpi3:
    st.markdown(
        f'<div class="kpi-box"'
        ' style="border-top-color:#2ecc71;"><h5>Total Financial'
        f" Payout</h5><h3>${total_payout_m:.2f}M</h3></div>",
        unsafe_allow_html=True,
    )
with kpi4:
    st.markdown(
        f'<div class="kpi-box"'
        ' style="border-top-color:#f39c12;"><h5>Smoker'
        f" Ratio</h5><h3>{smk_ratio:.1f}%</h3></div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# 7. Tabular Sub-Layout System
tab_main, tab_charts, tab_ml = st.tabs(
    ["📋 Fleet Analysis", "📉 Interactive Plots", "🧬 Risk Drivers (ML)"]
)

with tab_main:
    st.subheader("Segmented Cohort Breakdown")
    seg_feature = st.selectbox(
        "Pivot Data Matrix By:", ["age", "smoker", "region", "sex"]
    )

    df_pivot_input = df_filtered.copy()

    if seg_feature == "age":
        df_pivot_input["age_bin"] = pd.cut(
            df_pivot_input["age"],
            bins=[0, 25, 35, 45, 55, 100],
            labels=["18-25", "26-35", "36-45", "46-55", "56+"],
        )
        pivot_target = "age_bin"
    else:
        pivot_target = seg_feature

    summary = (
        df_pivot_input.groupby(pivot_target, observed=False)["charges"]
        .agg(["count", "mean", "median", "sum"])
        .round(2)
    )
    summary.columns = [
        "Total Policies",
        "Mean Payout ($)",
        "Median Payout ($)",
        "Total Pool Capital ($)",
    ]
    st.dataframe(summary, use_container_width=True)

    st.subheader("Granular Audit Stream (Top 50 Records)")
    st.dataframe(df_filtered.head(50), use_container_width=True)

with tab_charts:
    st.subheader("Actuarial Scatter and Density Plots")
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        sns.scatterplot(
            data=df_filtered,
            x="age",
            y="charges",
            hue="smoker",
            palette={"yes": "#e74c3c", "no": "#2ecc71"},
            alpha=0.7,
            ax=ax,
        )
        ax.set_title("Age vs Premium Payouts")
        ax.set_ylabel("Payout ($)")
        st.pyplot(fig)
        plt.close(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        sns.boxplot(
            data=df_filtered,
            x="smoker",
            y="charges",
            palette={"yes": "#e74c3c", "no": "#2ecc71"},
            ax=ax,
        )
        ax.set_title("Distribution Spread: Smokers vs Non-Smokers")
        ax.set_ylabel("Payout ($)")
        st.pyplot(fig)
        plt.close(fig)

with tab_ml:
    st.subheader("Statistical Analysis & Strategic Risk Assessment")

    if len(df_filtered) >= 15:
        # Mini Predictive Engine
        df_encoded = df_filtered.copy()
        df_encoded["sex"] = (df_encoded["sex"] == "male").astype(int)
        df_encoded["smoker"] = (df_encoded["smoker"] == "yes").astype(int)
        df_encoded["region"] = pd.factorize(df_encoded["region"])[0]

        X = df_encoded[["age", "sex", "bmi", "children", "smoker", "region"]]
        y = df_encoded["charges"]

        lr = LinearRegression()
        lr.fit(X, y)

        st.info(f"🤖 **Actuarial Model Performance R²:** {lr.score(X, y):.4f}")

        coef_summary = pd.DataFrame({
            "Predictor Feature": X.columns,
            "Financial Impact Coefficient ($)": lr.coef_,
        })
        st.table(
            coef_summary.sort_values(
                by="Financial Impact Coefficient ($)", ascending=False
            )
        )
    else:
        st.warning(
            "⚠️ Minimum 15 records required to run linear regression analysis."
        )

    st.markdown("---")
    st.subheader("Executive Recommendations Matrix")

    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.markdown("#### 🚬 Smoking Financial Overhead")
        non_smoker_subset = df_filtered[df_filtered["smoker"] == "no"]
        smoker_subset = df_filtered[df_filtered["smoker"] == "yes"]

        non_smoke_mean = (
            non_smoker_subset["charges"].mean()
            if len(non_smoker_subset) > 0
            else 0.0
        )
        smoke_mean = (
            smoker_subset["charges"].mean() if len(smoker_subset) > 0 else 0.0
        )

        st.write(f"• **Non-Smoker Claims Baseline:** ${non_smoke_mean:,.2f}")
        st.write(f"• **Active Smoker Claims Baseline:** ${smoke_mean:,.2f}")
        if non_smoke_mean > 0 and smoke_mean > 0:
            st.error(
                "• **Risk Multiplier:**"
                f" +{((smoke_mean / non_smoke_mean) - 1) * 100:.1f}% escalation."
            )

    with col_inf2:
        st.markdown("#### 🧬 Age Group Risk Vector")
        young_subset = df_filtered[df_filtered["age"] < 35]
        old_subset = df_filtered[df_filtered["age"] >= 55]

        young_avg = (
            young_subset["charges"].mean() if len(young_subset) > 0 else 0.0
        )
        old_avg = old_subset["charges"].mean() if len(old_subset) > 0 else 0.0

        st.write(f"• **Youth Segment Payout (Under 35):** ${young_avg:,.2f}")
        st.write(f"• **Senior Segment Payout (Age 55+):** ${old_avg:,.2f}")
        if young_avg > 0 and old_avg > 0:
            st.warning(
                "• **Age Demographics Overhead:**"
                f" +{((old_avg / young_avg) - 1) * 100:.1f}% cost shift."
            )

st.markdown("---")
st.caption("Engineered by Ghulam Muneer Uddin | Actuarial Engine")
