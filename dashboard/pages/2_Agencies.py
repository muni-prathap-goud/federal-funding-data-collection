import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    load_total_predictions, load_agency_series,
    load_all_metrics, MODEL_COLORS, fmt_dollars,
)

st.set_page_config(page_title="Agencies", page_icon="🏢", layout="wide")
st.title("🏢 Agency-Level Forecast")
st.caption("116 federal agencies · FY2017–2024 · Cumulative YTD per quarter")

preds   = load_total_predictions()
series  = load_agency_series()
metrics = load_all_metrics()
ag_met  = metrics[metrics["Layer"] == "Agency"]
total   = preds["Agency"]

tab1, tab2, tab3 = st.tabs(["Total Forecast", "Per Agency", "Model Metrics"])

# ── Tab 1: Total ──────────────────────────────────────────────────────────────
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("SARIMA MAPE (winner)", "3.8%")
    col2.metric("XGBoost MAPE",          "5.4%")
    col3.metric("Prophet MAPE",          "30.6%")

    model_sel = st.multiselect(
        "Models to display",
        ["Prophet", "SARIMA", "XGBoost"],
        default=["SARIMA", "XGBoost"],
        key="ag_model_sel",
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
        "**XGBoost improves to 5.4% vs 8.3% on budget functions** because 116 agency-level "
        "predictions sum to the total, providing more error cancellation than 20 function-level predictions. "
        "Feature importance: lag_4=41.3%, lag_8=35.4% (77% combined). Agency encoding contributes only 0.6% — "
        "temporal patterns dominate over agency identity."
    )

# ── Tab 2: Per Agency ────────────────────────────────────────────────────────
with tab2:
    # Top agencies by total spending
    agency_totals = (
        series.groupby(["agency_id", "agency_name"])["actual"]
        .sum().reset_index()
        .sort_values("actual", ascending=False)
    )
    agency_totals["label"] = agency_totals.apply(
        lambda r: f"{r['agency_name'][:45]}  ({fmt_dollars(r['actual'])})", axis=1
    )

    col_left, col_right = st.columns([2, 1])
    with col_left:
        selected_agency = st.selectbox("Select Agency", agency_totals["label"].tolist())
    with col_right:
        top_n = st.slider("Top N agencies chart", 5, 20, 10, key="ag_topn")

    sel_name = agency_totals.loc[
        agency_totals["label"] == selected_agency, "agency_name"
    ].iloc[0]
    sub = series[series["agency_name"] == sel_name].copy()

    fig2 = go.Figure()
    actual_row = sub[sub["model"] == "Prophet"]
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
        label = f"{m}  (MAPE: {mape:.1f}%)" if mape and mape < 1e5 else f"{m}  (diverged)"
        fig2.add_trace(go.Scatter(
            x=sub_m["ds"], y=sub_m["predicted"] / 1e9,
            mode="lines", name=label,
            line=dict(color=MODEL_COLORS[m], width=2),
        ))

    fig2.update_layout(
        height=380, yaxis_title="Obligated Amount ($B)", xaxis_title="",
        title=sel_name,
        legend=dict(orientation="h", y=-0.15),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#333"), xaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Top N bar chart
    top_agencies = agency_totals.head(top_n)
    fig3 = go.Figure(go.Bar(
        y=top_agencies["agency_name"].str[:35],
        x=top_agencies["actual"] / 1e12,
        orientation="h",
        marker_color="#4A9EDE",
        text=[fmt_dollars(v) for v in top_agencies["actual"]],
        textposition="outside",
    ))
    fig3.update_layout(
        height=max(300, top_n * 30),
        xaxis_title="Total Obligated ($T, test period)",
        yaxis=dict(autorange="reversed"),
        title=f"Top {top_n} Agencies by Test-Period Spending",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#333"),
        margin=dict(l=0, r=120, t=40, b=0),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Tab 3: Metrics ────────────────────────────────────────────────────────────
with tab3:
    st.dataframe(
        ag_met[["Model", "MAE ($B)", "RMSE ($B)", "MAPE (%)"]].set_index("Model"),
        use_container_width=True,
    )
    st.markdown("""
    **Notable per-agency results (Prophet MAPE):**
    | Agency | Prophet MAPE | SARIMA |
    |---|---|---|
    | Social Security Admin. | 3.3% | diverged (345M%) |
    | HHS | 5.4% | — |
    | Veterans Affairs | 5.6% | — |
    | Department of Defense | 6.4% | — |
    | OPM | 9.2% | — |
    | Treasury | 21.5% | — |
    | Dept. of Labor | — | diverged (1,846%) |
    | Transportation | — | diverged (537%) |

    Prophet won all 10 of the top-10 agency per-series comparisons. SARIMA diverged on 4/10.
    """)
