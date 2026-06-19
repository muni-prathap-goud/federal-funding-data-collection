import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    load_total_predictions, load_budget_function_series,
    load_all_metrics, MODEL_COLORS, fmt_dollars,
)

st.set_page_config(page_title="Budget Functions", page_icon="📊", layout="wide")
st.title("📊 Budget Functions Forecast")
st.caption("20 OMB budget functions · FY2017–2024 · Cumulative YTD per quarter")

preds   = load_total_predictions()
series  = load_budget_function_series()
metrics = load_all_metrics()
bf_met  = metrics[metrics["Layer"] == "Budget Functions"]
total   = preds["Budget Functions"]

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Total Forecast", "Per Function", "Model Metrics"])

# ── Tab 1: Total ──────────────────────────────────────────────────────────────
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("SARIMA MAPE (winner)", "3.8%",    delta=None)
    col2.metric("Prophet MAPE",          "27.6%",   delta=None)
    col3.metric("XGBoost MAPE",          "8.3%",    delta=None)

    model_sel = st.multiselect(
        "Models to display",
        ["Prophet", "SARIMA", "XGBoost"],
        default=["SARIMA", "XGBoost"],
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=total["ds"], y=total["actual"] / 1e12,
        mode="lines+markers", name="Actual",
        line=dict(color="#FFFFFF", width=2.5), marker=dict(size=6),
    ))
    col_map = {"Prophet": "prophet", "SARIMA": "sarima", "XGBoost": "xgboost"}
    for m in model_sel:
        fig.add_trace(go.Scatter(
            x=total["ds"], y=total[col_map[m]] / 1e12,
            mode="lines", name=m,
            line=dict(color=MODEL_COLORS[m], width=2, dash="dot" if m == "Prophet" else "solid"),
        ))

    # Shade test period
    test_start = total[total["fy"] == 2023]["ds"].min()
    fig.add_vrect(x0=test_start, x1=total["ds"].max(),
                  fillcolor="rgba(255,255,255,0.04)", line_width=0,
                  annotation_text="Test period", annotation_position="top left",
                  annotation_font_size=11, annotation_font_color="#aaa")

    fig.update_layout(
        height=400, yaxis_title="Obligated Amount ($T)", xaxis_title="",
        legend=dict(orientation="h", y=-0.15),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#333"), xaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "**Why SARIMA wins here:** Budget function spending is reported as cumulative YTD — "
        "Q4 always exceeds Q3 > Q2 > Q1 within each fiscal year. SARIMA's (1,1,1)(1,1,0,4) "
        "double differencing removes this accumulation pattern, leaving only year-over-year growth. "
        "Prophet systematically underestimates Q3/Q4 (worst: −$4,553B in Q4 FY2024)."
    )

# ── Tab 2: Per Function ───────────────────────────────────────────────────────
with tab2:
    functions = (
        series.groupby(["budget_function_id", "function_name"])["actual"]
        .sum().reset_index()
        .sort_values("actual", ascending=False)
    )
    func_options = functions.apply(lambda r: r["function_name"], axis=1).tolist()
    func_id_map  = dict(zip(functions["function_name"], functions["budget_function_id"]))

    selected_func = st.selectbox("Budget Function", func_options)
    sel_id        = func_id_map[selected_func]

    sub = series[series["budget_function_id"] == sel_id].copy()
    models_in = sub["model"].unique().tolist()

    prophet_mape = sarima_mape = None
    fig2 = go.Figure()
    actual_row = sub[sub["model"] == models_in[0]]
    fig2.add_trace(go.Scatter(
        x=actual_row["ds"], y=actual_row["actual"] / 1e9,
        mode="lines+markers", name="Actual",
        line=dict(color="#FFFFFF", width=2.5), marker=dict(size=6),
    ))

    for m in ["Prophet", "SARIMA"]:
        sub_m = sub[sub["model"] == m]
        if sub_m.empty:
            continue
        actual  = sub_m["actual"].values
        pred    = sub_m["predicted"].values
        nonzero = actual != 0
        if nonzero.sum() > 0:
            mape = float(pd.Series(abs((pred[nonzero] - actual[nonzero]) / actual[nonzero])).mean() * 100)
        else:
            mape = None
        if m == "Prophet":
            prophet_mape = mape
        else:
            sarima_mape  = mape
        label = f"{m}  (MAPE: {mape:.1f}%)" if mape and mape < 1e5 else f"{m}  (diverged)"
        fig2.add_trace(go.Scatter(
            x=sub_m["ds"], y=sub_m["predicted"] / 1e9,
            mode="lines", name=label,
            line=dict(color=MODEL_COLORS[m], width=2),
        ))

    test_start2 = sub[sub["model"] == models_in[0]].sort_values("ds")["ds"].iloc[len(sub[sub["model"] == models_in[0]])//2]
    fig2.add_vrect(x0=test_start2, x1=sub["ds"].max(),
                   fillcolor="rgba(255,255,255,0.04)", line_width=0,
                   annotation_text="Test", annotation_position="top left",
                   annotation_font_size=10, annotation_font_color="#aaa")
    fig2.update_layout(
        height=400, yaxis_title="Obligated Amount ($B)", xaxis_title="",
        title=f"{selected_func}",
        legend=dict(orientation="h", y=-0.15),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#333"), xaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Total spending badge
    total_spend = actual_row["actual"].sum()
    st.caption(f"Total test-period spending: **{fmt_dollars(total_spend)}**")

    if sarima_mape and sarima_mape > 1e4:
        st.warning(
            f"⚠️ SARIMA diverged on this function (MAPE > 10,000%). "
            "COVID-era stimulus created a large temporary spike that causes coefficient instability "
            "after seasonal differencing. Use Prophet for this series."
        )

# ── Tab 3: Metrics ────────────────────────────────────────────────────────────
with tab3:
    st.dataframe(
        bf_met[["Model", "MAE ($B)", "RMSE ($B)", "MAPE (%)"]].set_index("Model"),
        use_container_width=True,
    )

    fig3 = go.Figure()
    for _, row in bf_met.iterrows():
        fig3.add_trace(go.Bar(
            name=row["Model"],
            x=[row["Model"]],
            y=[row["MAPE (%)"]],
            marker_color=MODEL_COLORS[row["Model"]],
            text=[f"{row['MAPE (%)']:.1f}%"],
            textposition="outside",
        ))
    fig3.update_layout(
        height=300, yaxis_title="MAPE (%)", showlegend=False,
        title="Total-Series MAPE — Budget Functions",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    **Notable per-function results:**
    | Function | Best Model | MAPE |
    |---|---|---|
    | Social Security | Prophet | 3.0% |
    | Veterans Benefits | Prophet | 4.5% |
    | Medicare | Prophet | 6.5% |
    | National Defense | Prophet | 6.6% |
    | Health | Prophet | 8.0% |
    | Income Security | SARIMA diverged | 423M% |
    | Commerce & Housing Credit | SARIMA diverged | 1,124% |
    """)
