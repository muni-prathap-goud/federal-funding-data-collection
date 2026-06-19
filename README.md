# Federal Funding Forecasts & Data Collection Pipelines

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://federal-funding-data-collection-laxuv3nnnhlcvxcaa2umqy.streamlit.app/)

> End-to-end Python pipelines that pull 17 years of U.S. federal spending data from the USASpending.gov REST API, forecast it across four hierarchical layers using three models, and present the results in an interactive Streamlit dashboard.

---

## What This Is

I wanted to do more than collect federal spending data — I wanted to forecast where it's going next and find out which forecasting approach actually works on government accounting data. So I built:

1. **Two data pipelines** that pull 17 fiscal years (2008–2024) of federal spending at quarterly granularity from the USASpending.gov API
2. **A four-level forecasting suite** — Budget Functions, Agencies, Federal Accounts, and Geography
3. **A model comparison** across Prophet, SARIMA, and XGBoost on each layer
4. **An interactive Streamlit dashboard** that lets a visitor pick a layer, see historical spending, and view forecasts with confidence intervals

---

## Results at a Glance

| Data Layer | Winning Model | MAPE | Data Type |
|---|---|---|---|
| **Budget Functions** | SARIMA | **3.8%** | Cumulative YTD |
| **Agency** | SARIMA | **3.8%** | Cumulative YTD |
| **Federal Accounts** | SARIMA | **3.8%** | Cumulative YTD |
| **Geography** | Prophet | **13.7%** | Quarterly |

### The Central Finding

**Data structure determines which model wins, not model complexity.**

- **Cumulative YTD data → SARIMA wins.** Budget functions, agencies, and federal accounts all report year-to-date spending per quarter, so Q4 ≥ Q3 ≥ Q2 ≥ Q1 every fiscal year. SARIMA's seasonal differencing cleanly removes that accumulation pattern, leaving only year-over-year growth — and gets to **3.8% MAPE** on all three layers.
- **Quarterly data → Prophet wins.** Geography reports actual spending per quarter, so Q1 ≈ Q4 in scale. SARIMA's differencing destroys the signal (**58.3% MAPE**). Prophet fits a trend + seasonality independently and handles the quarterly pattern well — **13.7% MAPE**.
- **XGBoost** was competitive but didn't beat the time-series-native models on any layer.

This is the kind of finding you only get by actually running the comparison instead of defaulting to "use the most complex model."

---

## Live Dashboard

**Live URL:** https://federal-funding-data-collection-laxuv3nnnhlcvxcaa2umqy.streamlit.app/

The Streamlit app (`dashboard/`) presents the forecasts and model comparison across 6 pages:

1. **Overview** (`app.py`) — Model performance heatmap, central finding, total predictions
2. **Budget Functions** — Layer-1 forecasts and accuracy
3. **Agencies** — Agency-level forecasts
4. **Federal Accounts** — Account-level forecasts
5. **Geography** — State-level forecasts + per-capita choropleth map
6. **Model Comparison** — Side-by-side model performance, feature importance, recommendation matrix

To run locally:
```bash
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```

---

## Project Structure

```
federal-funding-data-collection/
├── pipeline-a-hierarchical/        # Pulls budget→agency→account→recipient→award data
├── pipeline-b-geography/           # Pulls geographic breakdown (country/state/county/district)
├── hierarchical-analysis/          # Forecasting notebooks
│   ├── 00_data_cleaning.ipynb
│   ├── 01_eda.ipynb
│   ├── 02_forecast_budget_functions.ipynb
│   ├── 03_forecast_agency.ipynb
│   ├── 04_forecast_federal_accounts.ipynb
│   ├── 05_forecast_geography.ipynb
│   └── 06_model_evaluation.ipynb
├── dashboard/                      # Streamlit app
│   ├── app.py
│   ├── utils.py
│   └── pages/
├── README.md
└── requirements.txt
```

---

## The Two Data Pipelines

### Pipeline A — Hierarchical (organizational structure)

Pulls federal spending data through the hierarchy: **Budget Functions → Agencies → Federal Accounts → Recipients → Awards.** Lets you trace spending from the highest mission area down to individual contracts.

See [`pipeline-a-hierarchical/`](pipeline-a-hierarchical/) for the notebooks.

### Pipeline B — Geography

Pulls federal spending broken down by **country, state, county, and congressional district**, with optional agency filters. Lets you ask things like "how much defense spending happened in Alabama in FY2023."

See [`pipeline-b-geography/`](pipeline-b-geography/) for the notebooks.

---

## Forecasting Approach

Each of the 4 data layers got the same treatment:

1. **Data cleaning** — handle missing quarters, normalize fiscal year boundaries, build a clean time-series per entity
2. **EDA** — examine seasonality, trend, growth rates, top entities by volume
3. **Three models trained** on each layer:
   - **Prophet** (Facebook's library) — handles seasonality automatically, robust defaults
   - **SARIMA** (Seasonal ARIMA via `statsmodels`) — strong on data with clear seasonal patterns
   - **XGBoost** — gradient-boosted trees treating the forecast as a tabular regression
4. **Model evaluation** on a held-out test period (FY2023–2024 for cumulative layers, FY2021–2024 for geography), measured on MAPE

---

## What Worked vs What Didn't

**Worked:**
- SARIMA on the three cumulative-YTD layers — converged cleanly, near-3% errors
- Prophet on geography quarterly data — handled the non-monotonic pattern well
- Building one consistent pipeline across all four layers so model comparison was apples-to-apples
- Multi-page Streamlit dashboard for live exploration

**Didn't work as expected:**
- SARIMA on geography fell apart (58% MAPE) because differencing destroys quarterly-not-cumulative data
- XGBoost never won — strong on raw tabular, but time-series-native models had the edge
- Prophet on cumulative YTD layers underperformed SARIMA because Prophet doesn't natively model "this period's value is bounded above the previous period's"

**Takeaway:** Before picking a forecasting model, understand whether your data is cumulative or per-period. That single check determines whether SARIMA or Prophet is the right starting point.

---

## Tech Stack

- **Python 3.11**
- **Data ingestion** — `requests`, `urllib3`, `concurrent.futures` for parallel API calls
- **Forecasting** — `prophet`, `statsmodels` (SARIMA), `xgboost`, `scikit-learn`
- **Data** — `pandas`, `numpy`
- **Dashboard** — `streamlit`, `plotly`
- **Data source** — [USASpending.gov API](https://api.usaspending.gov/)

---

## How to Reproduce

```bash
# Clone
git clone https://github.com/muni-prathap-goud/federal-funding-data-collection.git
cd federal-funding-data-collection

# Install dependencies
pip install -r requirements.txt

# Step 1 — Run the data collection pipelines (these pull from USASpending.gov)
jupyter notebook pipeline-a-hierarchical/
jupyter notebook pipeline-b-geography/

# Step 2 — Run the forecasting analysis
jupyter notebook hierarchical-analysis/

# Step 3 — Launch the dashboard
cd dashboard
streamlit run app.py
```

Open `http://localhost:8501` to view the dashboard.

---

## Data Coverage

- **Temporal**: 17 fiscal years (2008–2024) at quarterly granularity
- **Organizational**: Budget functions, agencies, federal accounts, recipients, awards
- **Geographic**: Country, state, county, and congressional district levels
- **Scale**: Multi-GB analysis-ready datasets

---

## Future Improvements

- Add confidence-interval visualization (Prophet provides them natively)
- Add cross-validation instead of a single holdout
- Try LightGBM and CatBoost as XGBoost alternatives
- Add anomaly detection on top of the forecasts to flag unusual spending patterns

---

*Author: Muniprathap Murari · [github.com/muni-prathap-goud](https://github.com/muni-prathap-goud)*
*Data Source: [USASpending.gov](https://www.usaspending.gov/)*
