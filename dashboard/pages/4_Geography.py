import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import (
    load_total_predictions, load_geography_series,
    load_per_capita, load_all_metrics, MODEL_COLORS, fmt_dollars,
)

st.set_page_config(page_title="Geography", page_icon="🗺️", layout="wide")
st.title("🗺️ Geography Forecast")
st.caption("56 states & territories · FY2008–2024 · True quarterly spending")

preds    = load_total_predictions()
series   = load_geography_series()
pc       = load_per_capita()
metrics  = load_all_metrics()
geo_met  = metrics[metrics["Layer"] == "Geography"]
total    = preds["Geography"]

tab1, tab2, tab3, tab4 = st.tabs(["Total Forecast", "Per State", "Per-Capita", "Model Metrics"])

# ── Tab 1: Total ──────────────────────────────────────────────────────────────
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Prophet MAPE (winner)", "13.7%")
    col2.metric("XGBoost MAPE",           "21.5%")
    col3.metric("SARIMA MAPE",            "58.3%",  help="Fails on quarterly data — SARIMA's differencing destroys the signal")

    model_sel = st.multiselect(
        "Models to display",
        ["Prophet", "SARIMA", "XGBoost"],
        default=["Prophet", "XGBoost"],
        key="geo_model_sel",
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=total["ds"], y=total["actual"] / 1e12,
        mode="lines+markers", name="Actual",
        line=dict(color="#FFFFFF", width=2.5), marker=dict(size=5),
    ))
    col_map = {"Prophet": "prophet", "SARIMA": "sarima", "XGBoost": "xgboost"}
    for m in model_sel:
        fig.add_trace(go.Scatter(
            x=total["ds"], y=total[col_map[m]] / 1e12,
            mode="lines", name=m,
            line=dict(color=MODEL_COLORS[m], width=2),
        ))

    test_start = total[total["fy"] == 2021]["ds"].min()
    fig.add_vrect(x0=test_start, x1=total["ds"].max(),
                  fillcolor="rgba(255,255,255,0.04)", line_width=0,
                  annotation_text="Test period (FY2021–2024)", annotation_position="top left",
                  annotation_font_size=11, annotation_font_color="#aaa")
    fig.update_layout(
        height=400, yaxis_title="Obligated Amount ($T)", xaxis_title="",
        legend=dict(orientation="h", y=-0.15),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#333"), xaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.warning(
        "**Model ranking reversal:** This is the only data layer where Prophet beats SARIMA. "
        "Geography reports *true quarterly spending* — Q1 ≈ Q4 in scale with no accumulation. "
        "SARIMA's seasonal differencing destroys the level signal, causing over-projection by "
        "$1–1.4T/quarter by FY2024. Prophet's independent trend+seasonality handles quarterly "
        "data correctly."
    )

# ── Tab 2: Per State ─────────────────────────────────────────────────────────
with tab2:
    state_totals = (
        series.groupby(["geo_code", "state_name"])["actual"]
        .sum().reset_index()
        .sort_values("actual", ascending=False)
    )
    state_totals["label"] = state_totals.apply(
        lambda r: f"{r['state_name']} ({r['geo_code']})  —  {fmt_dollars(r['actual'])}", axis=1
    )

    col_left, col_right = st.columns([2, 1])
    with col_left:
        selected_state = st.selectbox("Select State / Territory", state_totals["label"].tolist())
    with col_right:
        top_n = st.slider("Top N states chart", 5, 20, 10, key="geo_topn")

    sel_code = state_totals.loc[
        state_totals["label"] == selected_state, "geo_code"
    ].iloc[0]

    sub = series[series["geo_code"] == sel_code].copy()

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
        label = f"{m}  (MAPE: {mape:.1f}%)" if mape and mape < 1000 else f"{m}  (poor: {mape:.0f}%)" if mape else m
        fig2.add_trace(go.Scatter(
            x=sub_m["ds"], y=sub_m["predicted"] / 1e9,
            mode="lines", name=label,
            line=dict(color=MODEL_COLORS[m], width=2),
        ))

    state_name = state_totals.loc[state_totals["geo_code"] == sel_code, "state_name"].iloc[0]
    fig2.update_layout(
        height=380, yaxis_title="Obligated Amount ($B)", xaxis_title="",
        title=state_name,
        legend=dict(orientation="h", y=-0.15),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#333"), xaxis=dict(gridcolor="#333"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    if sel_code == "FL":
        st.error(
            "⚠️ **Florida — both models fail (>50% MAPE).** "
            "Hurricane disaster relief creates irregular spending spikes that no historical model can anticipate."
        )

    # Top N bar
    top_states = state_totals.head(top_n)
    fig3 = go.Figure(go.Bar(
        y=top_states["state_name"],
        x=top_states["actual"] / 1e12,
        orientation="h",
        marker_color="#4A9EDE",
        text=[fmt_dollars(v) for v in top_states["actual"]],
        textposition="outside",
    ))
    fig3.update_layout(
        height=max(300, top_n * 32),
        xaxis_title="Total Obligated ($T, test period FY2021–2024)",
        yaxis=dict(autorange="reversed"),
        title=f"Top {top_n} States by Test-Period Spending",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#333"),
        margin=dict(l=0, r=120, t=40, b=0),
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── Tab 3: Per Capita ────────────────────────────────────────────────────────
with tab3:
    fy_options = sorted(pc["fy"].unique(), reverse=True)
    fy_sel = st.selectbox("Fiscal Year", fy_options, index=0, key="pc_fy")
    pc_fy  = pc[pc["fy"] == fy_sel].copy()

    # Choropleth — US states only (2-letter codes that are valid state abbreviations)
    us_states = pc_fy[pc_fy["geo_code"].str.len() == 2].copy()

    fig_map = px.choropleth(
        us_states,
        locations="geo_code",
        locationmode="USA-states",
        color="per_capita",
        color_continuous_scale="Blues",
        scope="usa",
        hover_name="geo_name",
        hover_data={"per_capita": ":,.0f", "obligated_amount": False, "geo_code": False},
        labels={"per_capita": "Per Capita ($)"},
        title=f"Federal Spending Per Capita — FY{fy_sel}",
    )
    fig_map.update_layout(
        height=420,
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title="$ per capita"),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Table
    pc_table = (
        pc_fy[["geo_name", "geo_code", "obligated_amount", "population", "per_capita"]]
        .sort_values("per_capita", ascending=False)
        .head(20)
        .copy()
    )
    pc_table["obligated_amount"] = pc_table["obligated_amount"].apply(lambda v: fmt_dollars(v))
    pc_table["per_capita"]       = pc_table["per_capita"].apply(lambda v: f"${v:,.0f}")
    pc_table["population"]       = pc_table["population"].apply(lambda v: f"{v:,.0f}" if pd.notna(v) else "N/A")
    pc_table.columns = ["Name", "Code", "Total Spending", "Population", "Per Capita"]
    st.dataframe(pc_table.set_index("Code"), use_container_width=True)

    st.caption(
        "DC, North Dakota, and territories (VI, Guam) consistently rank highest per capita — "
        "federal employment concentration and formula-driven entitlement programs are the primary drivers."
    )

# ── Tab 4: Metrics ────────────────────────────────────────────────────────────
with tab4:
    st.dataframe(
        geo_met[["Model", "MAE ($B)", "RMSE ($B)", "MAPE (%)"]].set_index("Model"),
        use_container_width=True,
    )
    st.markdown("""
    **Geography is structurally different from all other layers:**

    | Metric | Budget Functions / Agency / Accounts | Geography |
    |---|---|---|
    | Data type | Cumulative YTD | True quarterly |
    | Train window | FY2017–2022 (24Q) | FY2008–2020 (52Q) |
    | Test window | FY2023–2024 (8Q) | FY2021–2024 (16Q) |
    | Best model | SARIMA | Prophet |
    | SARIMA MAPE | 3.8% | 58.3% |
    | Prophet MAPE | 27–30% | 13.7% |

    **Per-state notable results:**
    | State | Prophet MAPE | SARIMA MAPE |
    |---|---|---|
    | Texas | 32.0% | **22.6%** (SARIMA wins) |
    | Virginia | 31.2% | **22.9%** (SARIMA wins) |
    | California | ~15% | >50% |
    | Florida | 143.8% | 58.2% (both fail) |
    """)
