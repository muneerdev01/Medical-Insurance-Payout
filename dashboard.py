import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# 1. Page Configuration & Custom CSS
st.set_page_config(page_title="Medical Insurance Payout Dashboard", layout="wide", page_icon="📊")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .kpi-box {
        background-color: white; padding: 20px; border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #3498db;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Safe Data Loader
@st.cache_data
def load_insurance_data():
    try:
        return pd.read_csv('expenses.csv')
    except FileNotFoundError:
        np.random.seed(42)
        n_samples = 1338
        return pd.DataFrame({
            'age': np.random.randint(18, 65, n_samples),
            'sex': np.random.choice(['male', 'female'], n_samples),
            'bmi': np.random.normal(30, 6, n_samples),
            'children': np.random.randint(0, 6, n_samples),
            'smoker': np.random.choice(['yes', 'no'], n_samples, p=[0.2, 0.8]),
            'region': np.random.choice(['southwest', 'southeast', 'northwest', 'northeast'], n_samples),
            'charges': np.random.normal(13270, 12000, n_samples).clip(1000, 64000)
        })

# Load dataset
df = load_insurance_data()

# Clean column headers immediately to avoid key errors from trailing spaces or capitalization
df.columns = df.columns.str.lower().str.strip()

# 3. Defensive Validation Engine
required_columns = ['age', 'sex', 'bmi', 'children', 'smoker', 'region', 'charges']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"❌ **Data Schema Error:** Missing required columns: `{missing_columns}`")
    st.write("🕵️‍♂️ **Available columns detected in dataset:**", df.columns.tolist())
    st.info("Please adjust your `expenses.csv` column headers to match the expected schema.")
    st.stop()

# 4. Sidebar Controls (Real-Time Filters)
st.sidebar.title("📊 Filter Engine")
selected_regions = st.sidebar.multiselect("Region", options=df['region'].unique(), default=df['region'].unique())
selected_smokers = st.sidebar.multiselect("Smoker Status", options=df['smoker'].unique(), default=df['smoker'].unique())
selected_genders = st.sidebar.multiselect("Gender", options=df['sex'].unique(), default=df['sex'].unique())

# Dynamic Filtering
df_filtered = df[
    (df['region'].isin(selected_regions)) &
    (df['smoker'].isin(selected_smokers)) &
    (df['sex'].isin(selected_genders))
]

# 5. Main Application Header
st.title("Medical Insurance Payout Business Intelligence Dashboard")
st.markdown("Operational Risk Management and Actuarial Analysis Matrix.")
st.markdown("---")

# 6. Core Operational KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="kpi-box"><h5>Total Enrolled</h5><h3>{len(df_filtered):,}</h3></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="kpi-box" style="border-top-color:#e74c3c;"><h5>Avg Payout Charge</h5><h3>${df_filtered["charges"].mean():,.2f}</h3></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="kpi-box" style="border-top-color:#2ecc71;"><h5>Total Financial Payout</h5><h3>${df_filtered["charges"].sum()/1e6:.2f}M</h3></div>', unsafe_allow_html=True)
with kpi4:
    smk_ratio = (df_filtered['smoker'] == 'yes').sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
    st.markdown(f'<div class="kpi-box" style="border-top-color:#f39c12;"><h5>Smoker Ratio</h5><h3>{smk_ratio:.1f}%</h3></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 7. Tabular Sub-Layout System
tab_main, tab_charts, tab_ml = st.tabs(["📋 Fleet Analysis", "📉 Interactive Plots", "🧬 Risk Drivers (ML)"])

with tab_main:
    st.subheader("Segmented Cohort Breakdown")
    seg_feature = st.selectbox("Pivot Data Matrix By:", ["age", "smoker", "region", "sex"])
    
    if seg_feature == "age":
        df_filtered['age_bin'] = pd.cut(df_filtered['age'], bins=[0, 25, 35, 45, 55, 65], labels=['18-25', '26-35', '36-45', '46-55', '56-65'])
        pivot_target = 'age_bin'
    else:
        pivot_target = seg_feature

    summary = df_filtered.groupby(pivot_target)['charges'].agg(['count', 'mean', 'median', 'sum']).round(2)
    summary.columns = ['Total Policies', 'Mean Payout ($)', 'Median Payout ($)', 'Total Pool Capital ($)']
    st.dataframe(summary, use_container_width=True)
    
    st.subheader("Granular Audit Stream (Top 50 Records)")
    st.dataframe(df_filtered.head(50), use_container_width=True)

with tab_charts:
    st.subheader("Actuarial Scatter and Density Plots")
    c1, c2 = st.columns(2)
    
    with c1:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        sns.scatterplot(data=df_filtered, x='age', y='charges', hue='smoker', palette='Set1', alpha=0.7, ax=ax)
        ax.set_title("Age vs Premium Payouts")
        st.pyplot(fig)
        plt.close()

    with c2:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        sns.boxplot(data=df_filtered, x='smoker', y='charges', palette='muted', ax=ax)
        ax.set_title("Distribution Spread: Smokers vs Non-Smokers")
        st.pyplot(fig)
        plt.close()

with tab_ml:
    st.subheader("Statistical Analysis & Strategic Risk Assessment")
    
    if len(df_filtered) > 15:
        # Mini Predictive Engine
        df_encoded = df_filtered.copy()
        df_encoded['sex'] = (df_encoded['sex'] == 'male').astype(int)
        df_encoded['smoker'] = (df_encoded['smoker'] == 'yes').astype(int)
        df_encoded['region'] = pd.factorize(df_encoded['region'])[0]
        
        X = df_encoded[['age', 'sex', 'bmi', 'children', 'smoker', 'region']]
        y = df_encoded['charges']
        
        lr = LinearRegression()
        lr.fit(X, y)
        
        st.info(f"🤖 **Actuarial Model Performance R²:** {lr.score(X, y):.4f}")
        
        coef_summary = pd.DataFrame({'Predictor Feature': X.columns, 'Financial Impact Coefficient ($)': lr.coef_})
        st.table(coef_summary.sort_values(by='Financial Impact Coefficient ($)', ascending=False))
    
    st.markdown("---")
    st.subheader("Executive Recommendations Matrix")
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.markdown("#### 🚬 Smoking Financial Overhead")
        non_smoke_mean = df_filtered[df_filtered['smoker'] == 'no']['charges'].mean() if (df_filtered['smoker'] == 'no').sum() > 0 else 0
        smoke_mean = df_filtered[df_filtered['smoker'] == 'yes']['charges'].mean() if (df_filtered['smoker'] == 'yes').sum() > 0 else 0
        
        st.write(f"• **Non-Smoker Claims Baseline:** ${non_smoke_mean:,.2f}")
        st.write(f"• **Active Smoker Claims Baseline:** ${smoke_mean:,.2f}")
        if non_smoke_mean > 0:
            st.error(f"• **Risk Multiplier:** +{((smoke_mean / non_smoke_mean) - 1) * 100:.1f}% escalation.")

    with col_inf2:
        st.markdown("#### 🧬 Age Group Risk Vector")
        young_avg = df_filtered[df_filtered['age'] < 35]['charges'].mean() if (df_filtered['age'] < 35).sum() > 0 else 0
        old_avg = df_filtered[df_filtered['age'] >= 55]['charges'].mean() if (df_filtered['age'] >= 55).sum() > 0 else 0
        
        st.write(f"• **Youth Segment Payout (Under 35):** ${young_avg:,.2f}")
        st.write(f"• **Senior Segment Payout (Age 55+):** ${old_avg:,.2f}")
        if young_avg > 0:
            st.warning(f"• **Age Demographics Overhead:** +{((old_avg / young_avg) - 1) * 100:.1f}% cost shift.")

st.markdown("---")
st.caption("Engineered by Ghulam Muneer Uddin | Actuarial Engine")
