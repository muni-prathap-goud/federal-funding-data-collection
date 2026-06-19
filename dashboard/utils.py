from pathlib import Path
import pandas as pd
import streamlit as st

FORECAST_DIR = Path(__file__).parent.parent / "pipeline-a-hierarchical" / "data" / "forecasts"

MODEL_COLORS = {
    "Prophet": "#F4A228",
    "SARIMA":  "#27AE60",
    "XGBoost": "#8E44AD",
}

MODEL_DASH = {
    "Prophet": "solid",
    "SARIMA":  "dash",
    "XGBoost": "dot",
}


def fmt_dollars(v, decimals=2):
    if abs(v) >= 1e12:
        return f"${v/1e12:.{decimals}f}T"
    if abs(v) >= 1e9:
        return f"${v/1e9:.{decimals}f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:.{decimals}f}M"
    return f"${v:,.0f}"


@st.cache_data
def load_all_metrics():
    rows = []
    configs = [
        ("Budget Functions", "budget_functions_model_metrics.csv", "Cumulative YTD", "FY2023–2024"),
        ("Agency",           "agency_model_metrics.csv",           "Cumulative YTD", "FY2023–2024"),
        ("Federal Accounts", "federal_accounts_model_metrics.csv", "Cumulative YTD", "FY2023–2024"),
        ("Geography",        "geography_model_metrics.csv",        "Quarterly",       "FY2021–2024"),
    ]
    for layer, fname, dtype, test_period in configs:
        df = pd.read_csv(FORECAST_DIR / fname)
        df["Layer"]       = layer
        df["Data Type"]   = dtype
        df["Test Period"] = test_period
        rows.append(df)
    return pd.concat(rows, ignore_index=True)


@st.cache_data
def load_total_predictions():
    return {
        "Budget Functions": pd.read_csv(FORECAST_DIR / "budget_functions_total_predictions.csv",  parse_dates=["ds"]),
        "Agency":           pd.read_csv(FORECAST_DIR / "agency_total_predictions.csv",             parse_dates=["ds"]),
        "Federal Accounts": pd.read_csv(FORECAST_DIR / "federal_accounts_total_predictions.csv",  parse_dates=["ds"]),
        "Geography":        pd.read_csv(FORECAST_DIR / "geography_total_predictions.csv",          parse_dates=["ds"]),
    }


@st.cache_data
def load_budget_function_series():
    return pd.read_csv(FORECAST_DIR / "budget_functions_per_function_predictions.csv", parse_dates=["ds"])


@st.cache_data
def load_agency_series():
    return pd.read_csv(FORECAST_DIR / "agency_per_agency_predictions.csv", parse_dates=["ds"])


@st.cache_data
def load_federal_account_series():
    return pd.read_csv(FORECAST_DIR / "federal_accounts_per_account_predictions.csv", parse_dates=["ds"])


@st.cache_data
def load_geography_series():
    return pd.read_csv(FORECAST_DIR / "geography_per_state_predictions.csv", parse_dates=["ds"])


@st.cache_data
def load_per_capita():
    return pd.read_csv(FORECAST_DIR / "geography_per_capita_annual.csv")
