import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import load_all_metrics, MODEL_COLORS, fmt_dollars

st.set_page_config(page_title="Model Comparison", page_icon="🔬", layout="wide")
st.title("🔬 Cross-Notebook Model Comparison")
st.caption("Consolidated evaluation across all four data layers and three forecasting models")

metrics = load_all_metrics()

# ── MAPE heatmap ─────────────────────────────────────────────────────────────
st.subheader("MAPE Heatmap — All Models × All Layers")

layer_order = ["Budget Functions", "Agency", "Federal Accounts", "Geography"]
model_order = ["SARIMA", "Prophet", "XGBoost"]
pivot = metrics.pivot_table(index="Model", columns="Layer", values="MAPE (%)").round(1)
pivot = pivot.reindex(index=model_order, columns=layer_order)

fig_heat = go.Figure(go.Heatmap(
    z=pivot.values,
    x=["Budget\nFunctions", "Agency", "Federal\nAccounts", "Geography"],
    y=model_order,
    colorscale="RdYlGn_r",
    zmin=0, zmax=60,
    text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
    texttemplate="%{text}",
    textfont={"size": 16, "color": "white"},
    showscale=True,
    colorbar=dict(title=dict(text="MAPE (%)", font=dict(size=12))),
))
fig_heat.update_layout(
    height=250,
    margin=dict(l=0, r=0, t=20, b=10),
    xaxis=dict(side="top", tickfont=dict(size=12)),
    yaxis=dict(tickfont=dict(size=13)),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig_heat, use_container_width=True)

st.caption(
    "Green = best MAPE. Red = worst. The reversal between SARIMA and Prophet across the "
    "YTD / quarterly boundary is the central finding of this project."
)

# ── Grouped bar ──────────────────────────────────────────────────────────────
st.subheader("MAPE by Model and Layer")

fig_bar = go.Figure()
for model in model_order:
    sub = metrics[metrics["Model"] == model]
    mapes = [sub[sub["Layer"] == l]["MAPE (%)"].values[0] for l in layer_order]
    fig_bar.add_trace(go.Bar(
        name=model,
        x=["Budget\nFunctions", "Agency", "Federal\nAccounts", "Geography"],
        y=mapes,
        marker_color=MODEL_COLORS[model],
        text=[f"{v:.1f}%" for v in mapes],
        textposition="outside",
    ))
fig_bar.update_layout(
    barmode="group",
    height=380,
    yaxis_title="MAPE (%) — lower is better",
    legend=dict(orientation="h", y=-0.15),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="#333", range=[0, 70]),
    xaxis=dict(gridcolor="#333"),
    margin=dict(l=0, r=0, t=20, b=0),
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Full metrics table ────────────────────────────────────────────────────────
st.subheader("Full Metrics Table")

display = metrics[["Layer", "Data Type", "Test Period", "Model", "MAE ($B)", "RMSE ($B)", "MAPE (%)"]].copy()
display = display.sort_values(["Layer", "MAPE (%)"])

def highlight_best(grp):
    colors = [""] * len(grp)
    idx = grp["MAPE (%)"].idxmin()
    pos = grp.index.get_loc(idx)
    colors[pos] = "background-color: rgba(39,174,96,0.25)"
    return pd.Series(colors, index=grp.index)

st.dataframe(
    display.set_index(["Layer", "Model"]),
    use_container_width=True,
)

st.divider()

# ── XGBoost feature importance ────────────────────────────────────────────────
st.subheader("XGBoost Feature Importance Across Notebooks")

feat_imp = pd.DataFrame([
    {"Notebook": "Budget Functions", "lag_4": 43.2, "lag_8": 27.3, "lag_1":  9.1, "roll4_mean":  7.4, "quarter": 6.1, "covid": 1.1, "entity_enc": 2.3, "fy": 3.5},
    {"Notebook": "Agency",           "lag_4": 41.3, "lag_8": 35.4, "lag_1":  7.1, "roll4_mean":  6.9, "quarter": 3.9, "covid": 0.6, "entity_enc": 0.6, "fy": 4.2},
    {"Notebook": "Federal Accounts", "lag_4":  4.1, "lag_8": 16.4, "lag_1": 12.2, "roll4_mean": 44.4, "quarter":10.1, "covid": 0.5, "entity_enc": 3.8, "fy": 8.5},
    {"Notebook": "Geography",        "lag_4": 16.4, "lag_8":  2.7, "lag_1": 16.3, "roll4_mean": 49.2, "quarter": 1.7, "covid": 2.6, "entity_enc": 4.0, "fy": 7.1},
])

features = ["roll4_mean", "lag_4", "lag_8", "lag_1", "fy", "quarter", "entity_enc", "covid"]
feat_colors = {
    "roll4_mean": "#E74C3C", "lag_4": "#3498DB", "lag_8": "#2ECC71",
    "lag_1": "#9B59B6", "fy": "#F39C12", "quarter": "#1ABC9C",
    "entity_enc": "#95A5A6", "covid": "#E67E22",
}

fig_feat = go.Figure()
for feat in features:
    fig_feat.add_trace(go.Bar(
        name=feat,
        x=feat_imp["Notebook"],
        y=feat_imp[feat],
        marker_color=feat_colors[feat],
    ))
fig_feat.update_layout(
    barmode="stack",
    height=350,
    yaxis_title="Feature Importance (%)",
    legend=dict(orientation="h", y=-0.2, font=dict(size=10)),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(gridcolor="#333", range=[0, 105]),
    xaxis=dict(gridcolor="#333"),
    margin=dict(l=0, r=0, t=10, b=0),
)
st.plotly_chart(fig_feat, use_container_width=True)

st.markdown("""
**Feature importance pattern:**
- **lag_4 dominates on YTD data** (41–43%): same quarter last year is the strongest predictor when data is regular and cumulative
- **roll4_mean dominates on heterogeneous/quarterly data** (44–49%): the smoothed recent average is more robust when individual lag values are noisy across diverse series
- **COVID flag is consistently low** (0.5–2.6%): XGBoost learns to handle the COVID spike through the lag features, not a separate flag
""")

st.divider()

# ── Recommendation matrix ─────────────────────────────────────────────────────
st.subheader("Dashboard Model Assignment — Recommendation Matrix")

rec_data = {
    "Data Layer":      ["Budget Functions", "Agency", "Federal Accounts", "Geography (States)"],
    "Total Series":    ["SARIMA (3.8%)", "SARIMA (3.8%)", "SARIMA (3.8%)", "Prophet (13.7%)"],
    "Per Series":      [
        "Prophet wins 7/10",
        "Prophet wins 10/10",
        "Prophet wins 14/17; SARIMA for Hosp. Ins., Mil. Retirement, Tax Refunds",
        "Prophet wins 8/10; SARIMA for TX, VA",
    ],
    "Fallback":        ["XGBoost (8.3%)", "XGBoost (5.4%)", "XGBoost (5.8%)", "XGBoost (21.5%)"],
    "High Uncertainty": [
        "Income Security, Commerce & Housing Credit",
        "Labor, Transportation, Education",
        "COVID Payments, PPP Loans, Student Loans, Unemployment",
        "Florida (both >50% MAPE)",
    ],
}

rec_df = pd.DataFrame(rec_data)
st.dataframe(rec_df.set_index("Data Layer"), use_container_width=True)

st.markdown("""
**Decision rules for deploying models in this dashboard:**

1. **SARIMA** for all total-series views on hierarchical (YTD) data — 3.8% MAPE consistently
2. **Prophet** as the default per-series model — wins the majority of individual comparisons across all layers
3. **Override to SARIMA** for the 3 specific federal accounts and 2 states where SARIMA was measured to beat Prophet
4. **XGBoost** for Geography total (second-best at 21.5%), and as general fallback
5. **Flag as high-uncertainty** any series with MAPE > 100% on both models — show actual data but suppress or warn on the forecast line
""")
