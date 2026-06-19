import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils import load_all_metrics, load_total_predictions, MODEL_COLORS, fmt_dollars

st.set_page_config(
    page_title="Federal Funding Forecasts",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏛️ Federal Funding Forecasts")
st.caption("USASpending.gov · FY2008–2024 · Three forecasting models across four data layers")

st.markdown("""
This dashboard presents forecasting results for U.S. federal spending across four hierarchical
data layers. Three models were evaluated — **Prophet**, **SARIMA**, and **XGBoost** — on each layer.
The key finding is that **data structure determines which model wins**, not model complexity.
""")

# ── Key metrics row ──────────────────────────────────────────────────────────
metrics = load_all_metrics()

best_model = {
    "Budget Functions": ("SARIMA",  "3.8%",  "Cumulative YTD", "FY2023–2024"),
    "Agency":           ("SARIMA",  "3.8%",  "Cumulative YTD", "FY2023–2024"),
    "Federal Accounts": ("SARIMA",  "3.8%",  "Cumulative YTD", "FY2023–2024"),
    "Geography":        ("Prophet", "13.7%", "Quarterly",       "FY2021–2024"),
}

cols = st.columns(4)
for col, (layer, (model, mape, dtype, period)) in zip(cols, best_model.items()):
    color = MODEL_COLORS[model]
    col.markdown(
        f"""
        <div style='background:#1e1e2e;border-left:4px solid {color};padding:12px 16px;border-radius:6px'>
            <div style='font-size:12px;color:#aaa'>{layer}</div>
            <div style='font-size:24px;font-weight:700;color:{color}'>{mape}</div>
            <div style='font-size:12px;color:#ccc'>{model} · {dtype}</div>
            <div style='font-size:11px;color:#888'>Test: {period}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── MAPE heatmap ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Model Performance Heatmap")
    pivot = metrics.pivot_table(index="Model", columns="Layer", values="MAPE (%)").round(1)
    layer_order = ["Budget Functions", "Agency", "Federal Accounts", "Geography"]
    model_order = ["SARIMA", "Prophet", "XGBoost"]
    pivot = pivot.reindex(index=model_order, columns=layer_order)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=["Budget\nFunctions", "Agency", "Federal\nAccounts", "Geography"],
        y=model_order,
        colorscale="RdYlGn_r",
        zmin=0, zmax=60,
        text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont={"size": 15, "color": "white"},
        showscale=True,
        colorbar=dict(title=dict(text="MAPE (%)", font=dict(size=11))),
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(side="top", tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=12)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("The Central Finding")
    st.markdown("""
    **Cumulative YTD data → SARIMA wins**

    Budget functions, agencies, and federal accounts all report
    *year-to-date* spending per quarter. Q4 is always ≥ Q3 ≥ Q2 ≥ Q1.
    SARIMA's seasonal differencing cleanly removes the accumulation
    pattern, leaving only year-over-year growth. Result: **3.8% MAPE** on all three layers.

    **Quarterly data → Prophet wins**

    Geography reports *actual spending per quarter* — Q1 ≈ Q4 in scale.
    SARIMA's differencing destroys the signal (58.3% MAPE). Prophet fits
    a trend + seasonality independently and handles the quarterly pattern
    well: **13.7% MAPE**.
    """)

st.divider()

# ── Total spending overview ───────────────────────────────────────────────────
st.subheader("Total Federal Spending — All Models")

preds = load_total_predictions()
layer_sel = st.selectbox("Data Layer", list(preds.keys()), index=0)
df = preds[layer_sel].copy()

best_col = "sarima" if layer_sel != "Geography" else "prophet"
best_label = "SARIMA" if layer_sel != "Geography" else "Prophet"

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=df["ds"], y=df["actual"] / 1e12,
    mode="lines+markers", name="Actual",
    line=dict(color="#FFFFFF", width=2),
    marker=dict(size=5),
))
for model, col in [("Prophet", "prophet"), ("SARIMA", "sarima"), ("XGBoost", "xgboost")]:
    fig2.add_trace(go.Scatter(
        x=df["ds"], y=df[col] / 1e12,
        mode="lines", name=model,
        line=dict(color=MODEL_COLORS[model], width=2,
                  dash="solid" if model == best_label else "dot"),
        opacity=1.0 if model == best_label else 0.6,
    ))

fig2.update_layout(
    height=380,
    margin=dict(l=0, r=0, t=10, b=0),
    yaxis_title="Obligated Amount ($T)",
    xaxis_title="",
    legend=dict(orientation="h", y=-0.15),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="#333"),
    xaxis=dict(gridcolor="#333"),
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Key insights ─────────────────────────────────────────────────────────────
st.subheader("Key Project Insights")

insights = [
    ("🏆", "SARIMA dominates YTD data",
     "3.8% MAPE on Budget Functions, Agency, and Federal Accounts. The seasonal differencing in SARIMA(1,1,1)(1,1,0,4) is perfectly suited to cumulative within-year patterns."),
    ("🏆", "Prophet dominates quarterly data",
     "13.7% MAPE on Geography. True quarterly spending has no accumulation for SARIMA to exploit — Prophet's additive trend + seasonality fits better."),
    ("🔄", "XGBoost is the universal fallback",
     "5–22% MAPE across all layers. Never the best, never catastrophically wrong. Key feature: lag_4 dominates on YTD data; roll4_mean takes over on quarterly/sparse data."),
    ("⚠️", "COVID-era programs are unforecastable",
     "SBA PPP loans, Unemployment Trust Fund, U.S. Coronavirus Payments, and Federal Direct Student Loans all have >100% MAPE on both models. These require policy-driven estimates."),
    ("✅", "Most predictable series",
     "SSA Old-Age Trust Fund: 2.8% Prophet MAPE. Demographic-driven, formula-bound, insulated from discretionary shocks."),
    ("❌", "Least predictable series",
     "Florida: 143.8% Prophet / 58.2% SARIMA MAPE. Hurricane disaster relief creates irregular spikes no historical model can anticipate."),
]

cols = st.columns(3)
for i, (icon, title, body) in enumerate(insights):
    cols[i % 3].markdown(
        f"""
        <div style='background:#1e1e2e;padding:14px;border-radius:8px;margin-bottom:12px;min-height:110px'>
            <div style='font-size:18px'>{icon} <strong>{title}</strong></div>
            <div style='font-size:13px;color:#bbb;margin-top:6px'>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("""
---
**Data source:** [USASpending.gov API v2](https://api.usaspending.gov) · FY2008–2024
**Navigate using the sidebar** to explore Budget Functions, Agencies, Federal Accounts, Geography, and Model Comparison.
""")
