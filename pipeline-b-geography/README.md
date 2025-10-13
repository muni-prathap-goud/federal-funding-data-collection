# 🌍 Pipeline B: Geography-Based Federal Spending Data Collection

## Overview
A **geographic-dimensional pipeline** that collects federal spending data by location, providing insights into where federal funds are being spent across the United States and globally.

## Two Independent Branches

### 🗺️ Branch A: Geography (Basic)
**What it answers**: *"How much federal money was obligated where (country/state/county/district) in each fiscal year and quarter?"*

### 🏛️ Branch B: Geography-by-Agency  
**What it answers**: *"For each federal agency (funding or awarding), how much was obligated where in each fiscal year and quarter?"*

## 📋 Geographic Granularity Levels

Both branches collect data at four geographic levels:
- **Country**: International and domestic spending totals
- **State**: U.S. state-level spending distribution  
- **County**: County-level spending within states
- **District**: Congressional district-level spending

## 🗺️ Branch A: Geography (Basic) Details

### API Configuration
- **Endpoint**: `POST /api/v2/search/spending_by_geography/`
- **Filters**: 
  - `time_period`: FY/Quarter date ranges  
  - `date_type`: "action_date"
  - `scope`: "place_of_performance" (consistent)
  - `geo_layer`: {"country","state","county","district"}
  - **No agency filter applied** - captures total spending by location

### Notebooks
- **`Geography_basic.ipynb`**: Complete basic geography data collection

### Storage Structure
```
geography/basic/
├── country/  geo_country_FY{YYYY}.csv
├── state/    geo_state_FY{YYYY}.csv  
├── county/   geo_county_FY{YYYY}.csv
└── district/ geo_district_FY{YYYY}.csv
```

### Schema (Basic)
- `code`: Geographic identifier (ISO/FIPS/District code)
- `name`: Geographic display name
- `amount`: Obligation amount (numeric)
- `population`: When provided by API
- `fy`, `quarter`: Temporal dimensions
- `geo_layer`: Geographic granularity level
- `state_code`: For counties (derived from code[:2])
- **Dedupe Key**: `("fy","quarter","geo_layer","code")`

## 🏛️ Branch B: Geography-by-Agency Details

### API Configuration
- **Agency Roster**: `GET /api/v2/references/toptier_agencies/` (cached)
- **Data Endpoint**: `POST /api/v2/search/spending_by_geography/`
- **Additional Filters**:
  - `agencies`: `[{"type":"funding|awarding","tier":"toptier","name":"<Agency Name>"}]`
  - Same geographic and temporal filters as Basic branch

### Notebooks
- **`agency_geography.ipynb`**: Complete agency-geography data collection

### Dual Agency Perspectives
- **Funding Agencies**: Agencies that provide the funding for obligations
- **Awarding Agencies**: Agencies that make the actual awards/contracts

### Storage Structure
```
geography/geography_by_agency/
├── funding/
│   ├── country/  geo_country_funding_FY{YYYY}.csv
│   ├── state/    geo_state_funding_FY{YYYY}.csv
│   ├── county/   geo_county_funding_FY{YYYY}.csv  
│   └── district/ geo_district_funding_FY{YYYY}.csv
└── awarding/
    ├── country/  geo_country_awarding_FY{YYYY}.csv
    ├── state/    geo_state_awarding_FY{YYYY}.csv
    ├── county/   geo_county_awarding_FY{YYYY}.csv
    └── district/ geo_district_awarding_FY{YYYY}.csv
```

### Schema (Agency-Enhanced)
- **All Basic columns** plus:
- `agency_type`: "funding" or "awarding"
- `agency_code`: 3-digit toptier agency code
- `agency_name`: Official agency name
- **Dedupe Key**: `("fy","quarter","geo_layer","code","agency_type","agency_code")`

## 📅 Temporal Coverage

### FY/Quarter Date Mapping
- **Q1**: `(fy-1)-10-01` to `(fy-1)-12-31`
- **Q2**: `fy-01-01` to `fy-03-31`  
- **Q3**: `fy-04-01` to `fy-06-30`
- **Q4**: `fy-07-01` to `fy-09-30`

### Coverage Period
- **Fiscal Years**: 2008-2024 (17 years)
- **Quarters**: All quarters (Q1, Q2, Q3, Q4)
- **Total Periods**: 68 quarter combinations per geographic level

## 🔧 Technical Implementation

### Runtime Features
- **Thread Pools**: Configurable worker limits per geographic layer
- **Keep-Alive Sessions**: Pooled HTTP connections with reuse
- **Exponential Backoff**: Smart retry logic with jitter for network failures
- **Empty CSV Handling**: Creates valid CSV files even for zero-result queries
- **Failure Tracking**: Detailed logging and retry file generation

### Orchestration Patterns
- **Initial Run**: Complete data collection across all dimensions
- **Retry Run**: Processes only failed tasks from previous runs
- **Task Grid Processing**: Systematic coverage of all parameter combinations

## 🚀 Usage

### Geography (Basic) Execution
```python
# Initial complete run
run_geography_basic(
    mode="initial", 
    layers=["country","state","county","district"], 
    start_fy=2008, 
    end_fy=2024
)

# Retry failed tasks
run_geography_basic(
    mode="retry", 
    layers=["country","state","county","district"], 
    start_fy=2008, 
    end_fy=2024
)
```

### Geography-by-Agency Execution
```python
# Initial complete run
run_geography(
    mode="initial", 
    types=["funding","awarding"], 
    layers=["country","state","county","district"], 
    start_fy=2008, 
    end_fy=2024
)

# Retry failed tasks
run_geography(
    mode="retry", 
    types=["funding","awarding"], 
    layers=["country","state","county","district"], 
    start_fy=2008, 
    end_fy=2024
)
```

## 💡 What This Pipeline Answers

### Geographic Questions
| Branch | Focus | Key Question |
|--------|-------|-------------|
| Geography Basic | Location Totals | How much federal money was spent where? |
| Geography by Agency | Agency-Location Matrix | Which agencies spent how much in each location? |

### Analysis Capabilities
- **Geographic spending distribution** across U.S. and internationally
- **Regional economic impact analysis** of federal spending
- **Agency geographic footprint** comparison and analysis
- **Congressional district funding** patterns and equity analysis
- **State-by-state federal investment** tracking and trends
- **Cross-temporal geographic analysis** showing spending shifts over time

## 🎯 Key Insights Enabled

- **Regional Equity**: Are federal funds distributed fairly across regions?
- **Economic Impact**: Which areas benefit most from federal spending?
- **Agency Strategies**: Do agencies have consistent geographic priorities?
- **Political Analysis**: How does spending correlate with political representation?
- **Disaster Response**: How do emergency spending patterns vary geographically?
- **Infrastructure Investment**: Where are federal infrastructure dollars going?

---

**Next Step**: After collecting geographic data, run the [Data Consolidation Pipeline](../data-consolidation/) to create analysis-ready consolidated datasets.
