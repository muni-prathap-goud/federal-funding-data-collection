import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    load_total_predictions, load_federal_account_series,
    load_all_metrics, MODEL_COLORS, fmt_dollars,
)

st.set_page_config(page_title="Federal Accounts", page_icon="📁", layout="wide")
st.title("📁 Federal Accounts Forecast")
st.caption("2,236 federal accounts · Top 20 modeled individually · FY2017–2024 · Cumulative YTD")

preds   = load_total_predictions()
series  = load_federal_account_series()
metrics = load_all_metrics()
fa_met  = metrics[metrics["Layer"] == "Federal Accounts"]
total   = preds["Federal Accounts"]

# COVID-impacted accounts (both models fail)
COVID_ACCOUNTS = {
    "U.S. Coronavirus Payments",
    "Business Loans Program Account (SBA PPP)",
    "Unemployment Trust Fund",
    "Federal Direct Student Loan Program Account",
}

tab1, tab2, tab3 = st.tabs(["Total Forecast", "Per Account", "Model Metrics"])

# ── Tab 1: Total ──────────────────────────────────────────────────────────────
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("SARIMA MAPE (winner)", "3.8%")
    col2.metric("XGBoost MAPE",          "5.8%")
    col3.metric("Prophet MAPE",          "30.5%")

    model_sel = st.multiselect(
        "Models to display",
        ["Prophet", "SARIMA", "XGBoost"],
        default=["SARIMA", "XGBoost"],
        key="fa_model_sel",
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
            line=dict(color=MODEL_COLORS[m], width=2),
        ))
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
        "**XGBoost feature importance shifts here**: roll4_mean dominates at 44.4% "
        "(vs lag_4 at 43% on budget functions). With 2,236 heterogeneous accounts, "
        "the smoothed recent average is more reliable than any single lagged quarter. "
        "lag_4 drops to just 4.1%."
    )

# ── Tab 2: Per Account ───────────────────────────────────────────────────────
with tab2:
    acct_totals = (
        series.groupby(["federal_account_id", "acct_name"])["actual"]
        .sum().reset_index()
        .sort_values("actual", ascending=False)
    )
    acct_totals["label"] = acct_totals.apply(
        lambda r: f"{r['acct_name'][:50]}  ({fmt_dollars(r['actual'])})", axis=1
    )

    selected_acct = st.selectbox("Select Federal Account", acct_totals["label"].tolist())
    sel_name = acct_totals.loc[
        acct_totals["label"] == selected_acct, "acct_name"
    ].iloc[0]

    if any(c in sel_name for c in COVID_ACCOUNTS):
        st.error(
            "⚠️ **High-uncertainty series.** This account was directly impacted by COVID-era "
            "emergency spending (stimulus payments, PPP loans, UI surge, or student loan reversals). "
            "Both Prophet and SARIMA have MAPE > 100%. The chart shows actual vs model output "
            "but neither should be used for operational forecasting."
        )

    sub = series[series["acct_name"] == sel_name].copy()
    fig2 = go.Figure()
    actual_row = sub[sub["model"] == "Prophet"]
    if not actual_row.empty:
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
            mape = float(abs((pred[nonzero] - actual[nonzero]) / actual[nonzero]).mean() * 100)
        else:
            mape = None
        if mape and mape > 1e6:
            label = f"{m}  (diverged)"
        elif mape:
            label = f"{m}  (MAPE: {mape:.1f}%)"
        else:
            label = m
        fig2.add_trace(go.Scatter(
            x=sub_m["ds"], y=sub_m["predicted"] / 1e9,
            mode="lines", name=label,
            line=dict(color=MODEL_COLORS[m], width=2),
        ))

    fig2.update_layout(
        height=400, yaxis_title="Obligated Amount ($B)", xaxis_title="",
        title=sel_name[:60],
        legend=dict(orientation="h", y=-0.15),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#333"), xaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Top 20 bar chart
    top20 = acct_totals.head(20)
    fig3 = go.Figure(go.Bar(
        y=top20["acct_name"].str[:40],
        x=top20["actual"] / 1e12,
        orientation="h",
        marker_color="#4A9EDE",
        text=[fmt_dollars(v) for v in top20["actual"]],
        textposition="outside",
    ))
    fig3.update_layout(
        height=580,
        xaxis_title="Total Obligated ($T, test period)",
        yaxis=dict(autorange="reversed"),
        title="Top 20 Federal Accounts by Test-Period Spending",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#333"),
        margin=dict(l=0, r=130, t=40, b=0),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Tab 3: Metrics ────────────────────────────────────────────────────────────
with tab3:
    st.dataframe(
        fa_met[["Model", "MAE ($B)", "RMSE ($B)", "MAPE (%)"]].set_index("Model"),
        use_container_width=True,
    )
    st.markdown("""
    **Notable per-account results:**
    | Account | Best Model | MAPE |
    |---|---|---|
    | SSA Old-Age & Survivors Trust Fund | Prophet | **2.8%** ← lowest in project |
    | Medicare Health Care Trust Funds | Prophet | 3.4% |
    | Disability Insurance Trust Fund | Prophet | 4.1% |
    | Civil Service Retirement | Prophet | 4.7% |
    | Medicare Part A Hospital Insurance | **SARIMA** | 9.1% (Prophet: 15.7%) |
    | Military Retirement | **SARIMA** | 7.1% (Prophet: 8.1%) |
    | Tax Refunds | **SARIMA** | 23.3% (Prophet: 36.2%) |
    | U.S. Coronavirus Payments | Both fail | >100% |
    | Business Loans / SBA PPP | Both fail | >100% |
    | Unemployment Trust Fund | Both fail | >100% |
    | Federal Direct Student Loan | Both fail | >100% |

    SARIMA catastrophic failures: SSA Old-Age (6.1 billion%), Medicare (2.9M%), Civil Service (36,365%).
    """)
