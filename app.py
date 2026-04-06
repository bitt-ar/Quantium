"""
Quantium Retail Analytics Dashboard
====================================
Task 1: Customer Analytics  |  Task 2: Uplift Testing
"""

import re
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG & GLOBAL THEME
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Quantium · Retail Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

BG         = "#1a1d23"
SURFACE    = "#22262f"
BORDER     = "#2e3341"
ACCENT     = "#4f8ef7"
ACCENT2    = "#7c5cbf"
ACCENT3    = "#2ec4b6"
WARN       = "#f59e0b"
SUCCESS    = "#22c55e"
DANGER     = "#ef4444"
TEXT_MUTED = "#8b92a5"
TEXT_MAIN  = "#e2e6ef"
COLOR_SEQ  = [ACCENT, ACCENT3, WARN, SUCCESS, ACCENT2, DANGER,
              "#f97316", "#ec4899", "#84cc16", "#06b6d4"]

st.markdown(f"""
<style>
  html, body, [data-testid="stAppViewContainer"] {{
    background-color: {BG};
    color: {TEXT_MAIN};
    font-family: 'DM Sans', 'Segoe UI', sans-serif;
  }}
  [data-testid="stSidebar"] {{
    background-color: {SURFACE};
    border-right: 1px solid {BORDER};
  }}
  .stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background: {SURFACE};
    border-radius: 12px;
    padding: 4px;
    border: 1px solid {BORDER};
  }}
  .stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {TEXT_MUTED};
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: .03em;
    border: none !important;
  }}
  .stTabs [aria-selected="true"] {{
    background: {ACCENT} !important;
    color: #fff !important;
  }}
  .stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.5rem; }}
  .kpi-grid {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .kpi-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 18px 22px;
    flex: 1 1 160px;
    min-width: 160px;
    position: relative;
    overflow: hidden;
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--c, {ACCENT});
    border-radius: 14px 14px 0 0;
  }}
  .kpi-label {{ font-size: .75rem; color: {TEXT_MUTED}; letter-spacing:.06em; text-transform:uppercase; margin-bottom:6px; }}
  .kpi-value {{ font-size: 1.6rem; font-weight: 700; color: {TEXT_MAIN}; line-height:1; }}
  .kpi-sub   {{ font-size: .75rem; color: {TEXT_MUTED}; margin-top:4px; }}
  .sec-header {{ display: flex; align-items: center; gap: 10px; margin: 0 0 1rem 0; }}
  .sec-header .dot {{
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--c, {ACCENT}); flex-shrink: 0;
  }}
  .sec-header h3 {{ margin:0; font-size:1rem; font-weight:700; color:{TEXT_MAIN}; letter-spacing:.03em; }}
  hr {{ border-color: {BORDER}; }}
  .stSelectbox label, .stMultiSelect label {{ color: {TEXT_MUTED} !important; font-size:.8rem !important; }}
  .logo-row {{
    display: flex; align-items: center; gap: 14px;
    padding: 0 0 24px 0; margin-bottom: 8px;
    border-bottom: 1px solid {BORDER};
  }}
  .logo-icon {{
    width: 44px; height: 44px; border-radius: 12px;
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2});
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 900; color: white;
  }}
  .logo-title {{ font-size: 1.25rem; font-weight: 800; color: {TEXT_MAIN}; }}
  .logo-sub   {{ font-size: .75rem; color: {TEXT_MUTED}; margin-top: 2px; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def plotly_layout(title="", height=360):
    return dict(
        title=dict(text=title, font=dict(size=13, color=TEXT_MAIN)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, Segoe UI, sans-serif", color=TEXT_MUTED, size=11),
        height=height,
        margin=dict(l=10, r=10, t=36, b=10),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickcolor=BORDER),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, tickcolor=BORDER),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10, color=TEXT_MUTED)),
        colorway=COLOR_SEQ,
    )

def kpi(label, value, sub="", color=None):
    c = color or ACCENT
    return f"""<div class="kpi-card" style="--c:{c}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>"""

def sec(title, color=None):
    c = color or ACCENT
    st.markdown(f"""<div class="sec-header" style="--c:{c}">
        <div class="dot"></div><h3>{title}</h3></div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/cleaned_data.csv", parse_dates=["DATE"])
    df = df.dropna(subset=["DATE"])
    df["month_dt"] = df["DATE"].dt.to_period("M").dt.to_timestamp()
    return df

@st.cache_data
def compute_rfm(df_raw):
    reference_date = df_raw["DATE"].max()
    rfm = (df_raw.groupby("LYLTY_CARD_NBR")
           .agg(Recency=("DATE", lambda x: (reference_date - x.max()).days),
                Frequency=("TXN_ID", "count"),
                Monetary=("TOT_SALES", "sum"))
           .reset_index())
    rfm = rfm[rfm["Monetary"] > 0]
    rfm["R"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["M"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])
    rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)

    def segment_customer(score):
        if re.match(r"5[4-5][4-5]", score):    return "Champions"
        if re.match(r"[3-4][4-5][4-5]", score): return "Loyal Customers"
        if re.match(r"[4-5][2-3][2-3]", score): return "Potential Loyalists"
        if re.match(r"5[1-2][1-2]", score):     return "New Customers"
        if re.match(r"[3-4][1-2][1-2]", score): return "Promising"
        if re.match(r"[2-3][3-4][3-4]", score): return "Need Attention"
        if re.match(r"[2-3][1-2][1-2]", score): return "About to Sleep"
        if re.match(r"[1-2][4-5][4-5]", score): return "At Risk"
        if re.match(r"[1-2][2-3][2-3]", score): return "Hibernating"
        return "Lost"

    rfm["Segment"] = rfm["RFM_Score"].apply(segment_customer)
    return rfm

@st.cache_data
def compute_brand_affinity(df_raw):
    segment1 = df_raw[
        (df_raw["family_stage"] == "Standard") &
        (df_raw["PREMIUM_CUSTOMER"] == "Mainstream")
    ]
    other = df_raw[
        ~((df_raw["family_stage"] == "Standard") &
          (df_raw["PREMIUM_CUSTOMER"] == "Mainstream"))
    ]
    qty1   = segment1["PROD_QTY"].sum()
    qty_ot = other["PROD_QTY"].sum()

    s1_brand = segment1.groupby("company")["PROD_QTY"].sum().reset_index()
    s1_brand["targetSegment"] = s1_brand["PROD_QTY"] / qty1
    ot_brand = other.groupby("company")["PROD_QTY"].sum().reset_index()
    ot_brand["other"] = ot_brand["PROD_QTY"] / qty_ot

    brand_aff = pd.merge(s1_brand[["company","targetSegment"]],
                         ot_brand[["company","other"]], on="company")
    brand_aff["affinityToBrand"] = brand_aff["targetSegment"] / brand_aff["other"]
    brand_aff = brand_aff.sort_values("affinityToBrand", ascending=False).reset_index(drop=True)

    s1_size = segment1.groupby("size")["PROD_QTY"].sum().reset_index()
    s1_size["targetSegment"] = s1_size["PROD_QTY"] / qty1
    ot_size = other.groupby("size")["PROD_QTY"].sum().reset_index()
    ot_size["other"] = ot_size["PROD_QTY"] / qty_ot

    size_aff = pd.merge(s1_size[["size","targetSegment"]],
                        ot_size[["size","other"]], on="size")
    size_aff["affinityToSize"] = size_aff["targetSegment"] / size_aff["other"]
    size_aff = size_aff.sort_values("affinityToSize", ascending=False).reset_index(drop=True)
    return brand_aff, size_aff

@st.cache_data
def build_store_monthly(df_raw):
    stores = (df_raw.groupby([pd.Grouper(key="DATE", freq="ME"), "STORE_NBR"])
              .agg(total_sales=("TOT_SALES","sum"),
                   n_customers=("LYLTY_CARD_NBR","nunique"),
                   n_transactions=("TXN_ID","count"))
              .reset_index())
    stores["avg_transaction"] = stores["total_sales"] / stores["n_transactions"]
    counts = stores["STORE_NBR"].value_counts()
    full   = counts[counts == 12].index
    return stores[stores["STORE_NBR"].isin(full)]

df             = load_data()
rfm            = compute_rfm(df)
brand_aff, size_aff = compute_brand_affinity(df)
stores_monthly = build_store_monthly(df)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""<div style="padding-bottom:20px;border-bottom:1px solid {BORDER};margin-bottom:16px">
        <div style="font-size:1.1rem;font-weight:800;color:{TEXT_MAIN}">Quantium</div>
        <div style="font-size:.75rem;color:{TEXT_MUTED}">Retail Chip Analytics · FY 2018-19</div>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.75rem;color:{TEXT_MUTED};letter-spacing:.06em;text-transform:uppercase;margin-bottom:8px'>Filters</div>", unsafe_allow_html=True)

    sel_premium = st.multiselect("Customer Tier",
        sorted(df["PREMIUM_CUSTOMER"].dropna().unique()),
        default=sorted(df["PREMIUM_CUSTOMER"].dropna().unique()))
    sel_age = st.multiselect("Age Group",
        sorted(df["age_group"].dropna().unique()),
        default=sorted(df["age_group"].dropna().unique()))
    sel_stage = st.multiselect("Family Stage",
        sorted(df["family_stage"].dropna().unique()),
        default=sorted(df["family_stage"].dropna().unique()))
    sel_company = st.multiselect("Brand",
        sorted(df["company"].dropna().unique()),
        default=sorted(df["company"].dropna().unique()))

    st.markdown("---")
    st.markdown(f"<div style='font-size:.72rem;color:{TEXT_MUTED}'>{len(df):,} transactions · {df['STORE_NBR'].nunique()} stores</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILTERS
# ─────────────────────────────────────────────
mask = (
    df["PREMIUM_CUSTOMER"].isin(sel_premium) &
    df["age_group"].isin(sel_age) &
    df["family_stage"].isin(sel_stage) &
    df["company"].isin(sel_company)
)
dff = df[mask]

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown(f"""<div class="logo-row">
    <div class="logo-icon">Q</div>
    <div>
        <div class="logo-title">Quantium Retail Analytics</div>
        <div class="logo-sub">Chip Category · FY 2018-19 · {len(dff):,} transactions after filters</div>
    </div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Customer Segments",
    "Brands & Products",
    "RFM Analysis",
    "Trial vs Control",
])

# ══════════════════════════════════════════════
#  TAB 1  —  OVERVIEW
# ══════════════════════════════════════════════
with tab1:
    total_sales  = dff["TOT_SALES"].sum()
    total_txn    = len(dff)
    unique_cust  = dff["LYLTY_CARD_NBR"].nunique()
    avg_basket   = dff["TOT_SALES"].mean()
    total_units  = dff["PROD_QTY"].sum()
    total_stores = dff["STORE_NBR"].nunique()

    st.markdown(f"""<div class="kpi-grid">
        {kpi("Total Revenue",    f"${total_sales/1e6:.2f}M", "FY 2018-19",          ACCENT)}
        {kpi("Transactions",     f"{total_txn:,}",           "All stores",           ACCENT3)}
        {kpi("Unique Customers", f"{unique_cust:,}",          "Loyalty card holders", WARN)}
        {kpi("Avg Basket Size",  f"${avg_basket:.2f}",        "Per transaction",      SUCCESS)}
        {kpi("Units Sold",       f"{total_units:,}",          "Chip packets",         ACCENT2)}
        {kpi("Stores",           f"{total_stores}",           "Retail locations",     DANGER)}
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])

    with col1:
        sec("Monthly Revenue Trend", ACCENT)
        monthly = dff.groupby("month_dt")["TOT_SALES"].sum().reset_index()
        monthly.columns = ["Month","Revenue"]
        monthly["MA3"] = monthly["Revenue"].rolling(3, center=True).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Revenue"],
            mode="lines+markers", name="Monthly Revenue",
            line=dict(color=ACCENT, width=2.5), marker=dict(size=6),
            fill="tozeroy", fillcolor="rgba(79,142,247,.08)"))
        fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["MA3"],
            mode="lines", name="3-Month MA",
            line=dict(color=ACCENT2, width=2, dash="dash")))
        fig.update_layout(**plotly_layout("", 320))
        fig.update_yaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        sec("Revenue by Customer Tier", ACCENT2)
        tier = dff.groupby("PREMIUM_CUSTOMER")["TOT_SALES"].sum().reset_index()
        tier.columns = ["Tier","Revenue"]
        fig2 = go.Figure(go.Pie(
            labels=tier["Tier"], values=tier["Revenue"], hole=0.55,
            marker=dict(colors=[ACCENT, ACCENT2, ACCENT3]),
            textinfo="percent+label", textfont=dict(size=11, color="#fff")))
        fig2.update_layout(**plotly_layout("", 320))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    col3, col4 = st.columns(2)
    with col3:
        sec("Monthly Revenue Bar", ACCENT3)
        monthly2 = dff.groupby("month_dt")["TOT_SALES"].sum().reset_index()
        monthly2.columns = ["Month","Revenue"]
        monthly2["Label"] = monthly2["Month"].dt.strftime("%b '%y")
        fig3 = go.Figure(go.Bar(
            x=monthly2["Label"], y=monthly2["Revenue"],
            marker=dict(color=monthly2["Revenue"],
                        colorscale=[[0,SURFACE],[0.3,ACCENT2],[1,ACCENT]],
                        line=dict(width=0)),
            text=[f"${v/1000:.1f}K" for v in monthly2["Revenue"]],
            textposition="outside", textfont=dict(size=9, color=TEXT_MUTED)))
        fig3.update_layout(**plotly_layout("", 300))
        fig3.update_yaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col4:
        sec("Transactions by Day of Week", WARN)
        dff2 = dff.copy()
        dff2["DOW"] = dff2["DATE"].dt.day_name()
        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = dff2.groupby("DOW").agg(txn=("TXN_ID","count")).reindex(dow_order).reset_index()
        fig4 = go.Figure(go.Bar(
            x=dow["DOW"], y=dow["txn"],
            marker=dict(color=WARN, opacity=0.85, line=dict(width=0)),
            text=dow["txn"].apply(lambda x: f"{x:,}"),
            textposition="outside", textfont=dict(size=9, color=TEXT_MUTED)))
        fig4.update_layout(**plotly_layout("", 300))
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
#  TAB 2  —  CUSTOMER SEGMENTS
# ══════════════════════════════════════════════
with tab2:
    seg_summary = (dff.groupby("PREMIUM_CUSTOMER")
                   .agg(Revenue=("TOT_SALES","sum"),
                        Transactions=("TXN_ID","count"),
                        Customers=("LYLTY_CARD_NBR","nunique"),
                        Avg_Basket=("TOT_SALES","mean"))
                   .reset_index())
    cols = st.columns(3)
    colors_tier = [ACCENT, WARN, ACCENT2]
    for i, (_, row) in enumerate(seg_summary.iterrows()):
        with cols[i]:
            st.markdown(f"""<div class="kpi-card" style="--c:{colors_tier[i]}">
                <div class="kpi-label">{row['PREMIUM_CUSTOMER']}</div>
                <div class="kpi-value">${row['Revenue']/1000:.0f}K</div>
                <div class="kpi-sub">{row['Transactions']:,} txns · ${row['Avg_Basket']:.2f} avg basket</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        sec("Revenue by Age Group x Tier", ACCENT)
        age_tier = dff.groupby(["age_group","PREMIUM_CUSTOMER"])["TOT_SALES"].sum().reset_index()
        age_tier.columns = ["Age Group","Tier","Revenue"]
        fig5 = px.bar(age_tier, x="Age Group", y="Revenue", color="Tier",
                      barmode="group",
                      color_discrete_sequence=[ACCENT, ACCENT2, ACCENT3])
        fig5.update_layout(**plotly_layout("", 340))
        fig5.update_yaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

    with col2:
        sec("Revenue by Family Stage", ACCENT2)
        stage = (dff.groupby("family_stage")["TOT_SALES"].sum()
                 .sort_values(ascending=True).reset_index())
        stage.columns = ["Stage","Revenue"]
        fig6 = go.Figure(go.Bar(
            y=stage["Stage"], x=stage["Revenue"], orientation="h",
            marker=dict(color=stage["Revenue"],
                        colorscale=[[0,SURFACE],[0.4,ACCENT2],[1,ACCENT]],
                        line=dict(width=0)),
            text=[f"${v/1000:.1f}K" for v in stage["Revenue"]],
            textposition="outside", textfont=dict(size=10)))
        fig6.update_layout(**plotly_layout("", 340))
        fig6.update_xaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})

    col3, col4 = st.columns(2)
    with col3:
        sec("Avg Basket Size — Tier x Age Group (Heatmap)", ACCENT3)
        hm_data = (dff.groupby(["PREMIUM_CUSTOMER","age_group"])["TOT_SALES"]
                   .mean().reset_index())
        hm_pivot = hm_data.pivot(index="PREMIUM_CUSTOMER", columns="age_group", values="TOT_SALES")
        fig7 = go.Figure(go.Heatmap(
            z=hm_pivot.values,
            x=hm_pivot.columns.tolist(),
            y=hm_pivot.index.tolist(),
            colorscale=[[0,SURFACE],[0.5,ACCENT2],[1,ACCENT]],
            text=[[f"${v:.2f}" for v in row] for row in hm_pivot.values],
            texttemplate="%{text}", textfont=dict(size=11),
            showscale=True,
            colorbar=dict(tickfont=dict(color=TEXT_MUTED), bgcolor="rgba(0,0,0,0)")))
        fig7.update_layout(**plotly_layout("", 280))
        st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

    with col4:
        sec("Segment Revenue over Time", WARN)
        seg_time = dff.groupby(["month_dt","PREMIUM_CUSTOMER"])["TOT_SALES"].sum().reset_index()
        fig8 = px.line(seg_time, x="month_dt", y="TOT_SALES", color="PREMIUM_CUSTOMER",
                       color_discrete_sequence=[ACCENT, ACCENT2, WARN], markers=True)
        fig8.update_layout(**plotly_layout("", 280))
        fig8.update_yaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
#  TAB 3  —  BRANDS & PRODUCTS
# ══════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns([3, 2])
    with col1:
        sec("Top 10 Brands by Revenue", ACCENT)
        brand = (dff.groupby("company")["TOT_SALES"].sum()
                 .sort_values(ascending=False).head(10).reset_index())
        brand.columns = ["Brand","Revenue"]
        brand["pct"] = brand["Revenue"] / brand["Revenue"].sum() * 100
        colors_bar = [ACCENT if i == 0 else ACCENT2 if i < 3 else ACCENT3
                      for i in range(len(brand))]
        fig9 = go.Figure(go.Bar(
            y=brand["Brand"][::-1], x=brand["Revenue"][::-1], orientation="h",
            marker=dict(color=colors_bar[::-1], line=dict(width=0)),
            text=[f"${v/1000:.0f}K ({p:.1f}%)"
                  for v, p in zip(brand["Revenue"][::-1], brand["pct"][::-1])],
            textposition="outside", textfont=dict(size=10)))
        fig9.update_layout(**plotly_layout("", 380))
        fig9.update_xaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})

    with col2:
        sec("Brand Market Share (Top 10)", ACCENT2)
        fig10 = go.Figure(go.Pie(
            labels=brand["Brand"], values=brand["Revenue"], hole=0.5,
            marker=dict(colors=COLOR_SEQ[:len(brand)]),
            textinfo="percent", textfont=dict(size=10)))
        fig10.update_layout(**plotly_layout("", 380))
        st.plotly_chart(fig10, use_container_width=True, config={"displayModeBar": False})

    sec("Top 5 Brand Revenue Trend", ACCENT3)
    top5_brands = (dff.groupby("company")["TOT_SALES"].sum()
                   .sort_values(ascending=False).head(5).index.tolist())
    brand_trend = (dff[dff["company"].isin(top5_brands)]
                   .groupby(["month_dt","company"])["TOT_SALES"].sum().reset_index())
    fig11 = px.line(brand_trend, x="month_dt", y="TOT_SALES", color="company",
                    color_discrete_sequence=COLOR_SEQ[:5], markers=True)
    fig11.update_layout(**plotly_layout("", 320))
    fig11.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig11, use_container_width=True, config={"displayModeBar": False})

    col3, col4 = st.columns(2)
    with col3:
        # Categorical pack size — each size is its own category bar, evenly spaced
        sec("Pack Size Distribution (Categorical)", WARN)
        size_data = (dff.groupby("size")["TOT_SALES"].sum()
                     .reset_index().sort_values("size"))
        size_data.columns = ["Size","Revenue"]
        size_data["Size_cat"] = size_data["Size"].astype(str) + "g"
        fig12 = go.Figure(go.Bar(
            x=size_data["Size_cat"],
            y=size_data["Revenue"],
            marker=dict(color=WARN, opacity=0.85, line=dict(width=0)),
            text=[f"${v/1000:.1f}K" for v in size_data["Revenue"]],
            textposition="outside", textfont=dict(size=9, color=TEXT_MUTED)))
        fig12.update_layout(**plotly_layout("", 340))
        # Force categorical axis — uniform spacing regardless of numeric gaps
        fig12.update_xaxes(type="category", tickangle=-45, categoryorder="array",
                           categoryarray=size_data["Size_cat"].tolist())
        fig12.update_yaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig12, use_container_width=True, config={"displayModeBar": False})

    with col4:
        sec("Units Sold by Brand (Top 10)", SUCCESS)
        brand_units = (dff.groupby("company")["PROD_QTY"].sum()
                       .sort_values(ascending=False).head(10).reset_index())
        brand_units.columns = ["Brand","Units"]
        fig13 = go.Figure(go.Bar(
            x=brand_units["Brand"], y=brand_units["Units"],
            marker=dict(color=brand_units["Units"],
                        colorscale=[[0,SURFACE],[0.5,SUCCESS],[1,ACCENT3]],
                        line=dict(width=0)),
            text=brand_units["Units"].apply(lambda x: f"{x:,}"),
            textposition="outside", textfont=dict(size=9)))
        fig13.update_layout(**plotly_layout("", 340))
        st.plotly_chart(fig13, use_container_width=True, config={"displayModeBar": False})

    # ── Brand Affinity Analysis ───────────────
    st.markdown("<br>", unsafe_allow_html=True)
    sec("Brand Affinity Analysis — Mainstream Standard vs All Other Segments", ACCENT2)
    st.markdown(f"""<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:12px;
        padding:14px 18px;margin-bottom:16px;font-size:.82rem;color:{TEXT_MUTED};line-height:1.6">
        Affinity score = proportion of purchases by
        <b style="color:{TEXT_MAIN}">Mainstream Standard (Singles/Couples)</b>
        divided by proportion for all other segments.
        A score &gt; 1.0 means the target segment over-indexes on that brand or pack size.
    </div>""", unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        sec("Brand Affinity Score", ACCENT2)
        ba = brand_aff.copy()
        ba["color"] = ba["affinityToBrand"].apply(
            lambda v: SUCCESS if v >= 1.1 else (WARN if v >= 1.0 else DANGER))
        fig_aff = go.Figure(go.Bar(
            y=ba["company"][::-1],
            x=ba["affinityToBrand"][::-1],
            orientation="h",
            marker=dict(color=ba["color"][::-1].tolist(), line=dict(width=0)),
            text=[f"{v:.3f}" for v in ba["affinityToBrand"][::-1]],
            textposition="outside", textfont=dict(size=10)))
        fig_aff.add_vline(x=1.0, line_color=TEXT_MUTED, line_dash="dash",
                          annotation_text="Baseline = 1.0",
                          annotation_font_color=TEXT_MUTED, annotation_font_size=10)
        fig_aff.update_layout(**plotly_layout("", 440))
        st.plotly_chart(fig_aff, use_container_width=True, config={"displayModeBar": False})

    with col6:
        sec("Pack Size Affinity Score", ACCENT3)
        sa = size_aff.copy()
        sa["Size_cat"] = sa["size"].astype(str) + "g"
        sa["color"]    = sa["affinityToSize"].apply(
            lambda v: SUCCESS if v >= 1.1 else (WARN if v >= 1.0 else DANGER))
        fig_saff = go.Figure(go.Bar(
            y=sa["Size_cat"][::-1],
            x=sa["affinityToSize"][::-1],
            orientation="h",
            marker=dict(color=sa["color"][::-1].tolist(), line=dict(width=0)),
            text=[f"{v:.3f}" for v in sa["affinityToSize"][::-1]],
            textposition="outside", textfont=dict(size=10)))
        fig_saff.add_vline(x=1.0, line_color=TEXT_MUTED, line_dash="dash",
                           annotation_text="Baseline = 1.0",
                           annotation_font_color=TEXT_MUTED, annotation_font_size=10)
        fig_saff.update_layout(**plotly_layout("", 440))
        st.plotly_chart(fig_saff, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════
#  TAB 4  —  RFM ANALYSIS
# ══════════════════════════════════════════════
with tab4:
    seg_colors = {
        "Champions":           ACCENT,
        "Loyal Customers":     ACCENT3,
        "Potential Loyalists": SUCCESS,
        "New Customers":       WARN,
        "Promising":           "#84cc16",
        "Need Attention":      "#f97316",
        "About to Sleep":      ACCENT2,
        "At Risk":             DANGER,
        "Hibernating":         "#ec4899",
        "Lost":                "#6b7280",
    }

    st.markdown(f"""<div class="kpi-grid">
        {kpi("Total Customers",   f"{len(rfm):,}",                  "RFM eligible",        ACCENT)}
        {kpi("Avg Recency",       f"{rfm['Recency'].mean():.0f}d",   "Days since last buy",  ACCENT3)}
        {kpi("Avg Frequency",     f"{rfm['Frequency'].mean():.1f}",  "Transactions / yr",    WARN)}
        {kpi("Avg Monetary",      f"${rfm['Monetary'].mean():.2f}",  "Total spend",          SUCCESS)}
        {kpi("Champions",         f"{(rfm['Segment']=='Champions').sum():,}", "Best customers", ACCENT2)}
        {kpi("At Risk + Lost",    f"{rfm['Segment'].isin(['At Risk','Lost']).sum():,}", "Need recovery", DANGER)}
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 3])

    with col1:
        sec("Customers by RFM Segment", ACCENT)
        seg_counts = rfm["Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment","Count"]
        seg_counts["color"] = seg_counts["Segment"].map(seg_colors)
        fig_r1 = go.Figure(go.Bar(
            y=seg_counts["Segment"][::-1],
            x=seg_counts["Count"][::-1],
            orientation="h",
            marker=dict(color=seg_counts["color"][::-1].tolist(), line=dict(width=0)),
            text=seg_counts["Count"][::-1].apply(lambda x: f"{x:,}"),
            textposition="outside", textfont=dict(size=10)))
        fig_r1.update_layout(**plotly_layout("", 420))
        st.plotly_chart(fig_r1, use_container_width=True, config={"displayModeBar": False})

    with col2:
        sec("Segment Revenue Contribution", ACCENT2)
        rfm_merge = rfm[["LYLTY_CARD_NBR","Segment"]].copy()
        df_seg = dff.merge(rfm_merge, on="LYLTY_CARD_NBR", how="left")
        seg_rev = (df_seg.groupby("Segment")["TOT_SALES"].sum()
                   .sort_values(ascending=False).reset_index())
        seg_rev.columns = ["Segment","Revenue"]
        seg_rev["color"] = seg_rev["Segment"].map(seg_colors)
        fig_r2 = go.Figure(go.Bar(
            x=seg_rev["Segment"], y=seg_rev["Revenue"],
            marker=dict(color=seg_rev["color"].tolist(), line=dict(width=0)),
            text=[f"${v/1000:.0f}K" for v in seg_rev["Revenue"]],
            textposition="outside", textfont=dict(size=9)))
        fig_r2.update_layout(**plotly_layout("", 420))
        fig_r2.update_xaxes(tickangle=-30)
        fig_r2.update_yaxes(tickprefix="$", tickformat=",")
        st.plotly_chart(fig_r2, use_container_width=True, config={"displayModeBar": False})

    col3, col4 = st.columns(2)
    with col3:
        sec("Avg Recency by Segment (lower = more recent)", ACCENT3)
        seg_rfm_avg = rfm.groupby("Segment")[["Recency","Frequency","Monetary"]].mean().reset_index()
        seg_rfm_avg["color"] = seg_rfm_avg["Segment"].map(seg_colors)
        seg_rfm_avg = seg_rfm_avg.sort_values("Recency")
        fig_r3 = go.Figure(go.Bar(
            y=seg_rfm_avg["Segment"], x=seg_rfm_avg["Recency"],
            orientation="h",
            marker=dict(color=seg_rfm_avg["color"].tolist(), line=dict(width=0)),
            text=[f"{v:.0f}d" for v in seg_rfm_avg["Recency"]],
            textposition="outside", textfont=dict(size=9)))
        fig_r3.update_layout(**plotly_layout("", 340))
        fig_r3.update_xaxes(title_text="Days")
        st.plotly_chart(fig_r3, use_container_width=True, config={"displayModeBar": False})

    with col4:
        sec("Avg Monetary by Segment", WARN)
        seg_mon = rfm.groupby("Segment")["Monetary"].mean().sort_values(ascending=False).reset_index()
        seg_mon["color"] = seg_mon["Segment"].map(seg_colors)
        fig_r4 = go.Figure(go.Bar(
            x=seg_mon["Segment"], y=seg_mon["Monetary"],
            marker=dict(color=seg_mon["color"].tolist(), line=dict(width=0)),
            text=[f"${v:.1f}" for v in seg_mon["Monetary"]],
            textposition="outside", textfont=dict(size=9)))
        fig_r4.update_layout(**plotly_layout("", 340))
        fig_r4.update_xaxes(tickangle=-30)
        fig_r4.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_r4, use_container_width=True, config={"displayModeBar": False})

    sec("RFM Scatter — Frequency vs Monetary, colored by Segment", ACCENT)
    rfm_sample = rfm.sample(min(5000, len(rfm)), random_state=42)
    fig_r5 = px.scatter(rfm_sample, x="Frequency", y="Monetary",
                        color="Segment", color_discrete_map=seg_colors,
                        opacity=0.55, hover_data=["Recency","RFM_Score"])
    fig_r5.update_layout(**plotly_layout("", 420))
    fig_r5.update_yaxes(tickprefix="$")
    st.plotly_chart(fig_r5, use_container_width=True, config={"displayModeBar": False})

    sec("RFM Segment Summary Table", ACCENT2)
    seg_tbl = rfm.groupby("Segment").agg(
        Customers=("LYLTY_CARD_NBR","count"),
        Avg_Recency=("Recency","mean"),
        Avg_Frequency=("Frequency","mean"),
        Avg_Monetary=("Monetary","mean"),
    ).reset_index().sort_values("Customers", ascending=False)
    seg_tbl["Avg_Recency"]   = seg_tbl["Avg_Recency"].map("{:.1f} d".format)
    seg_tbl["Avg_Frequency"] = seg_tbl["Avg_Frequency"].map("{:.1f}".format)
    seg_tbl["Avg_Monetary"]  = seg_tbl["Avg_Monetary"].map("${:.2f}".format)
    st.dataframe(seg_tbl, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
#  TAB 5  —  TRIAL vs CONTROL
# ══════════════════════════════════════════════
with tab5:
    PAIRS       = {77: 233, 86: 231, 88: 237}
    TRIAL_START = pd.Timestamp("2019-02-01")
    TRIAL_END   = pd.Timestamp("2019-04-30")

    st.markdown(f"""<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:14px;
        padding:18px;margin-bottom:20px">
        <div style="font-size:.75rem;color:{TEXT_MUTED};letter-spacing:.06em;text-transform:uppercase;margin-bottom:10px">Trial Store Pairs</div>
        <div style="display:flex;gap:20px;flex-wrap:wrap">
        {"".join([f'<div style="background:{BG};border:1px solid {BORDER};border-radius:10px;padding:12px 20px"><div style="font-size:.7rem;color:{TEXT_MUTED}">Trial / Control</div><div style="font-size:1.1rem;font-weight:700;color:{TEXT_MAIN}">Store {t} / {c}</div></div>' for t, c in PAIRS.items()])}
        </div>
    </div>""", unsafe_allow_html=True)

    sel_trial = st.selectbox("Select Trial Store",
                             list(PAIRS.keys()),
                             format_func=lambda x: f"Trial Store {x}  (Control: {PAIRS[x]})")
    ctrl = PAIRS[sel_trial]

    pair = stores_monthly[stores_monthly["STORE_NBR"].isin([sel_trial, ctrl])].copy()
    pair["Store"] = pair["STORE_NBR"].map(
        {sel_trial: f"Trial ({sel_trial})", ctrl: f"Control ({ctrl})"})

    # Scaling factor (pre-trial)
    pre_trial = pair[pair["DATE"] < TRIAL_START]
    ts_pre = pre_trial[pre_trial["STORE_NBR"] == sel_trial]["total_sales"].sum()
    cs_pre = pre_trial[pre_trial["STORE_NBR"] == ctrl]["total_sales"].sum()
    sf = ts_pre / cs_pre if cs_pre else 1.0

    # Comparison df
    ctrl_df  = stores_monthly[stores_monthly["STORE_NBR"] == ctrl][["DATE","total_sales"]].copy()
    trial_df = stores_monthly[stores_monthly["STORE_NBR"] == sel_trial][["DATE","total_sales"]].copy()
    ctrl_df["ctrl_scaled"] = ctrl_df["total_sales"] * sf
    cmp = pd.merge(trial_df.rename(columns={"total_sales":"trial_sales"}),
                   ctrl_df[["DATE","ctrl_scaled"]], on="DATE")
    cmp["pct_diff"] = (cmp["trial_sales"] - cmp["ctrl_scaled"]) / cmp["ctrl_scaled"] * 100

    pre_std = cmp[cmp["DATE"] < TRIAL_START]["pct_diff"].std()
    trial_cmp = cmp[(cmp["DATE"] >= TRIAL_START) & (cmp["DATE"] <= TRIAL_END)].copy()
    trial_cmp["t_value"] = (trial_cmp["pct_diff"] / pre_std) if pre_std else np.nan

    # KPIs
    for lbl, pmask in [
        ("Pre-Trial Baseline",      pair["DATE"] < TRIAL_START),
        ("Trial Period  Feb - Apr 2019", pair["DATE"] >= TRIAL_START),
    ]:
        sub  = pair[pmask]
        ts   = sub[sub["STORE_NBR"] == sel_trial]["total_sales"].sum()
        cs   = sub[sub["STORE_NBR"] == ctrl]["total_sales"].sum() * sf
        up   = ((ts - cs) / cs * 100) if cs else 0
        col_kpi = SUCCESS if up > 0 else DANGER
        sec(lbl, ACCENT if "Baseline" in lbl else SUCCESS)
        st.markdown(f"""<div class="kpi-grid">
            {kpi(f"Trial Store {sel_trial}", f"${ts:,.0f}",  "Total sales",         ACCENT)}
            {kpi(f"Scaled Control {ctrl}",  f"${cs:,.0f}",   "Scaled sales",        ACCENT2)}
            {kpi("Sales Uplift",            f"{up:+.1f}%",   "Trial vs Scaled Ctrl", col_kpi)}
            {kpi("Scaling Factor",          f"{sf:.4f}",     "Pre-trial ratio",      ACCENT3)}
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Time-series
    sec(f"Monthly Total Sales — Trial {sel_trial} vs Control {ctrl}", ACCENT)
    fig14 = go.Figure()
    for slbl, clr in [(f"Trial ({sel_trial})", ACCENT), (f"Control ({ctrl})", ACCENT2)]:
        s = pair[pair["Store"] == slbl].sort_values("DATE")
        fig14.add_trace(go.Scatter(x=s["DATE"], y=s["total_sales"],
            mode="lines+markers", name=slbl,
            line=dict(color=clr, width=2.5), marker=dict(size=7)))
    ctrl_sc_line = stores_monthly[stores_monthly["STORE_NBR"] == ctrl].sort_values("DATE")
    fig14.add_trace(go.Scatter(x=ctrl_sc_line["DATE"],
        y=ctrl_sc_line["total_sales"] * sf,
        mode="lines", name=f"Control Scaled (x{sf:.3f})",
        line=dict(color=ACCENT3, width=1.5, dash="dot")))
    fig14.add_vrect(x0=TRIAL_START, x1=TRIAL_END,
                   fillcolor=SUCCESS, opacity=0.07, line_width=0,
                   annotation_text="Trial Window",
                   annotation_font_color=SUCCESS, annotation_font_size=11)
    fig14.update_layout(**plotly_layout("", 360))
    fig14.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig14, use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns(2)
    with col1:
        sec(f"Unique Customers — {sel_trial} vs {ctrl}", ACCENT3)
        fig15 = go.Figure()
        for slbl, clr in [(f"Trial ({sel_trial})", ACCENT), (f"Control ({ctrl})", ACCENT2)]:
            s = pair[pair["Store"] == slbl].sort_values("DATE")
            fig15.add_trace(go.Scatter(x=s["DATE"], y=s["n_customers"],
                mode="lines+markers", name=slbl,
                line=dict(color=clr, width=2), marker=dict(size=6)))
        fig15.add_vrect(x0=TRIAL_START, x1=TRIAL_END,
                       fillcolor=SUCCESS, opacity=0.07, line_width=0)
        fig15.update_layout(**plotly_layout("", 300))
        st.plotly_chart(fig15, use_container_width=True, config={"displayModeBar": False})

    with col2:
        sec(f"Avg Transaction Value — {sel_trial} vs {ctrl}", WARN)
        fig16 = go.Figure()
        for slbl, clr in [(f"Trial ({sel_trial})", ACCENT), (f"Control ({ctrl})", WARN)]:
            s = pair[pair["Store"] == slbl].sort_values("DATE")
            fig16.add_trace(go.Scatter(x=s["DATE"], y=s["avg_transaction"],
                mode="lines+markers", name=slbl,
                line=dict(color=clr, width=2), marker=dict(size=6)))
        fig16.add_vrect(x0=TRIAL_START, x1=TRIAL_END,
                       fillcolor=SUCCESS, opacity=0.07, line_width=0)
        fig16.update_layout(**plotly_layout("", 300))
        fig16.update_yaxes(tickprefix="$")
        st.plotly_chart(fig16, use_container_width=True, config={"displayModeBar": False})

    # Percentage Difference
    st.markdown("<br>", unsafe_allow_html=True)
    sec("Percentage Difference vs Scaled Control — Monthly", ACCENT2)
    fig17 = go.Figure(go.Bar(
        x=cmp["DATE"].dt.strftime("%b %Y"),
        y=cmp["pct_diff"],
        marker=dict(color=[SUCCESS if v > 0 else DANGER for v in cmp["pct_diff"]],
                    line=dict(width=0)),
        text=[f"{v:+.1f}%" for v in cmp["pct_diff"]],
        textposition="outside", textfont=dict(size=10)))
    fig17.add_hline(y=0, line_color=TEXT_MUTED, line_dash="dash")
    fig17.update_layout(**plotly_layout("", 300))
    fig17.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig17, use_container_width=True, config={"displayModeBar": False})

    # T-value table — notebook methodology
    sec(f"Statistical Significance — t-value Method  |  threshold |t| > 2.0", DANGER)
    st.markdown(f"""<div style="background:{SURFACE};border:1px solid {BORDER};border-radius:10px;
        padding:12px 18px;margin-bottom:14px;font-size:.82rem;color:{TEXT_MUTED};line-height:1.6">
        t-value = Percentage Difference / Pre-trial standard deviation of % difference<br>
        |t| &gt; 2.0 indicates significance at ~95% confidence.
        Pre-trial std for Store {sel_trial}: <b style="color:{TEXT_MAIN}">{pre_std:.4f}%</b>
    </div>""", unsafe_allow_html=True)

    if len(trial_cmp) > 0:
        rows = []
        for _, row in trial_cmp.iterrows():
            rows.append({
                "Month":           row["DATE"].strftime("%B %Y"),
                "Trial Sales":     f"${row['trial_sales']:,.0f}",
                "Scaled Control":  f"${row['ctrl_scaled']:,.0f}",
                "% Difference":    f"{row['pct_diff']:+.2f}%",
                "t-value":         f"{row['t_value']:.3f}",
                "Significant?":    "Yes  (|t| > 2)" if abs(row["t_value"]) > 2 else "No",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # All-stores summary
    st.markdown("<br>", unsafe_allow_html=True)
    sec("All Trial Stores Summary", ACCENT3)
    summary_rows = []
    for t, c in PAIRS.items():
        p    = stores_monthly[stores_monthly["STORE_NBR"].isin([t, c])]
        pre  = p[p["DATE"] < TRIAL_START]
        tsp  = pre[pre["STORE_NBR"] == t]["total_sales"].sum()
        csp  = pre[pre["STORE_NBR"] == c]["total_sales"].sum()
        sff  = tsp / csp if csp else 1.0
        trl  = p[(p["STORE_NBR"] == t) & (p["DATE"] >= TRIAL_START)]
        ctl  = p[(p["STORE_NBR"] == c) & (p["DATE"] >= TRIAL_START)]
        ts   = trl["total_sales"].sum()
        cs   = ctl["total_sales"].sum() * sff
        up   = ((ts - cs) / cs * 100) if cs else 0

        cd = stores_monthly[stores_monthly["STORE_NBR"] == c][["DATE","total_sales"]].copy()
        td = stores_monthly[stores_monthly["STORE_NBR"] == t][["DATE","total_sales"]].copy()
        cd["cs"] = cd["total_sales"] * sff
        cm2 = pd.merge(td.rename(columns={"total_sales":"ts"}), cd[["DATE","cs"]], on="DATE")
        cm2["pd2"] = (cm2["ts"] - cm2["cs"]) / cm2["cs"] * 100
        pstd2 = cm2[cm2["DATE"] < TRIAL_START]["pd2"].std()
        tc2   = cm2[(cm2["DATE"] >= TRIAL_START) & (cm2["DATE"] <= TRIAL_END)]
        if pstd2 and len(tc2):
            max_t = (tc2["pd2"] / pstd2).abs().max()
            sig   = "Yes" if max_t > 2 else "No"
        else:
            max_t, sig = np.nan, "N/A"

        summary_rows.append({
            "Trial":         t,
            "Control":       c,
            "Scale Factor":  f"{sff:.4f}",
            "Trial Sales":   f"${ts:,.0f}",
            "Scaled Ctrl":   f"${cs:,.0f}",
            "Uplift %":      f"{up:+.1f}%",
            "Max |t-value|": f"{max_t:.3f}" if not np.isnan(max_t) else "-",
            "Significant?":  sig,
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

# Footer
st.markdown(f"""
<div style="margin-top:40px;padding-top:20px;border-top:1px solid {BORDER};
     text-align:center;color:{TEXT_MUTED};font-size:.72rem;letter-spacing:.04em">
  Quantium Retail Analytics Dashboard · FY 2018-19 · Streamlit + Plotly
</div>""", unsafe_allow_html=True)