"""
MEDICAL INSURANCE PAYOUT ANALYSIS
Interactive Streamlit Dashboard

Command to run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Medical Insurance Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    h1 {
        color: #1f77b4;
    }
    h2 {
        color: #2ca02c;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD AND CACHE DATA
# ============================================================================

@st.cache_data
def load_data():
    df = pd.read_csv('expenses.csv')
    
    # Create derived columns
    df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 45, 55, 65], 
                             labels=['18-25', '26-35', '36-45', '46-55', '56-65'])
    df['bmi_category'] = pd.cut(df['bmi'], bins=[0, 18.5, 25, 30, 100],
                                labels=['Underweight', 'Normal', 'Overweight', 'Obese'])
    
    # Encoded version for correlation
    df_encoded = df.copy()
    df_encoded['sex'] = (df_encoded['sex'] == 'male').astype(int)
    df_encoded['smoker'] = (df_encoded['smoker'] == 'yes').astype(int)
    df_encoded['region'] = pd.factorize(df_encoded['region'])[0]
    
    return df, df_encoded

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

st.sidebar.title("🎛️ Filters")

df, df_encoded = load_data()

# Age filter
age_range = st.sidebar.slider(
    "Age Range",
    min_value=int(df['age'].min()),
    max_value=int(df['age'].max()),
    value=(int(df['age'].min()), int(df['age'].max()))
)

# Gender filter
gender_filter = st.sidebar.multiselect(
    "Gender",
    options=df['sex'].unique(),
    default=df['sex'].unique()
)

# Smoking filter
smoking_filter = st.sidebar.multiselect(
    "Smoking Status",
    options=['yes', 'no'],
    default=['yes', 'no']
)

# Region filter
region_filter = st.sidebar.multiselect(
    "Region",
    options=df['region'].unique(),
    default=df['region'].unique()
)

# BMI Category filter
bmi_filter = st.sidebar.multiselect(
    "BMI Category",
    options=df['bmi_category'].unique(),
    default=df['bmi_category'].unique()
)

# Apply filters
df_filtered = df[
    (df['age'] >= age_range[0]) & (df['age'] <= age_range[1]) &
    (df['sex'].isin(gender_filter)) &
    (df['smoker'].isin(smoking_filter)) &
    (df['region'].isin(region_filter)) &
    (df['bmi_category'].isin(bmi_filter))
].copy()

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

# Header
st.title("🏥 Medical Insurance Payout Analysis")
st.markdown("**Interactive Dashboard for Insurance Cost Analytics & Insights**")

# Summary stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Customers", len(df_filtered), 
              delta=f"{len(df_filtered)} of {len(df)}")

with col2:
    avg_charge = df_filtered['charges'].mean()
    st.metric("Avg Charge", f"${avg_charge:,.0f}", 
              delta=f"${avg_charge - df['charges'].mean():,.0f}")

with col3:
    total_charges = df_filtered['charges'].sum()
    st.metric("Total Payout", f"${total_charges/1e6:.2f}M", 
              delta=f"${(total_charges - df['charges'].sum())/1e6:.2f}M")

with col4:
    smoker_pct = (df_filtered['smoker'] == 'yes').sum() / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
    st.metric("Smokers %", f"{smoker_pct:.1f}%", 
              delta=f"{smoker_pct - ((df['smoker'] == 'yes').sum() / len(df) * 100):.1f}%")

st.divider()

# ============================================================================
# TAB LAYOUT
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🔍 Detailed Analysis", 
    "📈 Visualizations",
    "⚠️ Risk Analysis",
    "💡 Insights"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    st.subheader("Dataset Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Key Statistics**")
        stats_data = {
            'Metric': ['Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max'],
            'Age': [
                len(df_filtered),
                f"{df_filtered['age'].mean():.1f}" if len(df_filtered) > 0 else "0",
                f"{df_filtered['age'].median():.1f}" if len(df_filtered) > 0 else "0",
                f"{df_filtered['age'].std():.1f}" if len(df_filtered) > 1 else "0",
                f"{df_filtered['age'].min():.1f}" if len(df_filtered) > 0 else "0",
                f"{df_filtered['age'].max():.1f}" if len(df_filtered) > 0 else "0"
            ],
            'BMI': [
                len(df_filtered),
                f"{df_filtered['bmi'].mean():.2f}" if len(df_filtered) > 0 else "0",
                f"{df_filtered['bmi'].median():.2f}" if len(df_filtered) > 0 else "0",
                f"{df_filtered['bmi'].std():.2f}" if len(df_filtered) > 1 else "0",
                f"{df_filtered['bmi'].min():.2f}" if len(df_filtered) > 0 else "0",
                f"{df_filtered['bmi'].max():.2f}" if len(df_filtered) > 0 else "0"
            ],
            'Charges': [
                len(df_filtered),
                f"${df_filtered['charges'].mean():,.0f}" if len(df_filtered) > 0 else "$0",
                f"${df_filtered['charges'].median():,.0f}" if len(df_filtered) > 0 else "$0",
                f"${df_filtered['charges'].std():,.0f}" if len(df_filtered) > 1 else "$0",
                f"${df_filtered['charges'].min():,.0f}" if len(df_filtered) > 0 else "$0",
                f"${df_filtered['charges'].max():,.0f}" if len(df_filtered) > 0 else "$0"
            ]
        }
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
    
    with col2:
        st.write("**Categorical Distribution**")
        cat_col1, cat_col2 = st.columns(2)
        
        with cat_col1:
            st.write("**Gender**")
            gender_counts = df_filtered['sex'].value_counts()
            st.bar_chart(gender_counts)
            
            st.write("**Smoking Status**")
            smoke_counts = df_filtered['smoker'].value_counts()
            st.bar_chart(smoke_counts)
        
        with cat_col2:
            st.write("**Region**")
            region_counts = df_filtered['region'].value_counts()
            st.bar_chart(region_counts)
            
            st.write("**BMI Category**")
            bmi_counts = df_filtered['bmi_category'].value_counts()
            st.bar_chart(bmi_counts)

# ============================================================================
# TAB 2: DETAILED ANALYSIS
# ============================================================================

with tab2:
    st.subheader("Segmentation Analysis")
    
    seg_col1, seg_col2 = st.columns(2)
    
    with seg_col1:
        st.write("**Charges by Smoking Status**")
        smoke_data = df_filtered.groupby('smoker')['charges'].agg(['count', 'mean', 'median', 'min', 'max'])
        smoke_data.columns = ['Count', 'Avg', 'Median', 'Min', 'Max']
        st.dataframe(smoke_data.style.format("${:,.0f}"), use_container_width=True)
    
    with seg_col2:
        st.write("**Charges by Age Group**")
        age_data = df_filtered.groupby('age_group', observed=False)['charges'].agg(['count', 'mean', 'median', 'std'])
        age_data.columns = ['Count', 'Avg', 'Median', 'Std Dev']
        st.dataframe(age_data.style.format("${:,.0f}"), use_container_width=True)
    
    seg_col3, seg_col4 = st.columns(2)
    
    with seg_col3:
        st.write("**Charges by BMI Category**")
        bmi_data = df_filtered.groupby('bmi_category', observed=False)['charges'].agg(['count', 'mean', 'median', 'std'])
        bmi_data.columns = ['Count', 'Avg', 'Median', 'Std Dev']
        st.dataframe(bmi_data.style.format("${:,.0f}"), use_container_width=True)
    
    with seg_col4:
        st.write("**Charges by Region**")
        region_data = df_filtered.groupby('region')['charges'].agg(['count', 'mean', 'median', 'std'])
        region_data.columns = ['Count', 'Avg', 'Median', 'Std Dev']
        st.dataframe(region_data.style.format("${:,.0f}"), use_container_width=True)

# ============================================================================
# TAB 3: VISUALIZATIONS
# ============================================================================

with tab3:
    st.subheader("Interactive Visualizations")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        st.write("**Charges Distribution**")
        fig, ax = plt.subplots(figsize=(8, 5))
        if len(df_filtered) > 0:
            ax.hist(df_filtered['charges'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
            ax.axvline(df_filtered['charges'].mean(), color='red', linestyle='--', label='Mean')
        ax.set_xlabel('Charges ($)')
        ax.set_ylabel('Frequency')
        ax.legend()
        st.pyplot(fig)
    
    with viz_col2:
        st.write("**Age vs Charges**")
        fig, ax = plt.subplots(figsize=(8, 5))
        if len(df_filtered) > 0:
            colors = ['red' if x == 'yes' else 'blue' for x in df_filtered['smoker']]
            ax.scatter(df_filtered['age'], df_filtered['charges'], c=colors, alpha=0.5, s=30)
        ax.set_xlabel('Age (years)')
        ax.set_ylabel('Charges ($)')
        st.pyplot(fig)
    
    viz_col3, viz_col4 = st.columns(2)
    
    with viz_col3:
        st.write("**BMI vs Charges**")
        fig, ax = plt.subplots(figsize=(8, 5))
        if len(df_filtered) > 0:
            colors = ['red' if x == 'yes' else 'blue' for x in df_filtered['smoker']]
            ax.scatter(df_filtered['bmi'], df_filtered['charges'], c=colors, alpha=0.5, s=30)
        ax.set_xlabel('BMI')
        ax.set_ylabel('Charges ($)')
        st.pyplot(fig)
    
    with viz_col4:
        st.write("**Charges by Smoking Status**")
        fig, ax = plt.subplots(figsize=(8, 5))
        if len(df_filtered) > 0:
            smoke_avg = df_filtered.groupby('smoker')['charges'].mean()
            colors = ['#2ecc71', '#e74c3c']
            bars = ax.bar(smoke_avg.index, smoke_avg.values, color=colors, edgecolor='black')
            ax.set_ylabel('Average Charges ($)')
            ax.set_title('Smoking Impact on Charges')
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')
        st.pyplot(fig)
    
    st.divider()
    
    # Correlation heatmap - only numeric columns
    st.write("**Correlation Matrix**")
    corr_fig, corr_ax = plt.subplots(figsize=(10, 8))
    numeric_cols = df_encoded.select_dtypes(include=[np.number]).columns
    correlation = df_encoded[numeric_cols].corr()
    sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, ax=corr_ax)
    st.pyplot(corr_fig)

# ============================================================================
# TAB 4: RISK ANALYSIS
# ============================================================================

with tab4:
    st.subheader("Risk Assessment")
    st.write("**Risk Segmentation Model**")
    
    risk_df = df_filtered.copy()
    if len(risk_df) > 0:
        risk_df['risk_tier'] = 'Tier 2: Moderate'
        
        # Tier 1: Low Risk
        tier1 = (risk_df['smoker'] == 'no') & (risk_df['bmi'] < 25) & (risk_df['age'] < 35)
        risk_df.loc[tier1, 'risk_tier'] = 'Tier 1: Low'
        
        # Tier 3: High Risk
        tier3 = ((risk_df['smoker'] == 'yes') | (risk_df['bmi'] > 30)) & (risk_df['age'] >= 45)
        risk_df.loc[tier3, 'risk_tier'] = 'Tier 3: High'
        
        # Tier 4: Critical Risk
        tier4 = (risk_df['smoker'] == 'yes') & (risk_df['bmi'] > 30) & (risk_df['age'] >= 45)
        risk_df.loc[tier4, 'risk_tier'] = 'Tier 4: Critical'
        
        risk_summary = risk_df.groupby('risk_tier').agg({
            'charges': ['count', 'mean', 'min', 'max'],
            'age': 'mean',
            'bmi': 'mean'
        }).round(0)
        st.dataframe(risk_summary, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Risk Distribution**")
            risk_counts = risk_df['risk_tier'].value_counts()
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c']
            ax.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%',
                   colors=colors, startangle=90)
            st.pyplot(fig)
        
        with col2:
            st.write("**Average Charge by Risk Tier**")
            tier_charges = risk_df.groupby('risk_tier')['charges'].mean().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.barh(tier_charges.index, tier_charges.values, 
                           color=['#e74c3c', '#e67e22', '#f39c12', '#2ecc71'])
            ax.set_xlabel('Average Charges ($)')
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'${width:,.0f}', ha='left', va='center', fontweight='bold')
            st.pyplot(fig)
    else:
        st.write("No data available for current filter selection.")

# ============================================================================
# TAB 5: INSIGHTS & RECOMMENDATIONS
# ============================================================================

with tab5:
    st.subheader("📌 Key Insights & Recommendations")
    
    if len(df_filtered) > 0 and 'yes' in df_filtered['smoker'].values and 'no' in df_filtered['smoker'].values:
        smoker_avg = df_filtered[df_filtered['smoker'] == 'yes']['charges'].mean()
        non_smoker_avg = df_filtered[df_filtered['smoker'] == 'no']['charges'].mean()
        smoking_premium = ((smoker_avg / non_smoker_avg) - 1) * 100
        
        young_avg = df_filtered[df_filtered['age']
