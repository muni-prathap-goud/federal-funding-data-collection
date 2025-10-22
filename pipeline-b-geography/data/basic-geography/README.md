# Basic Geography Data

## Overview
This folder contains **basic geographic spending data** collected without agency filtering. These datasets show total federal spending by location across all agencies combined.

## Datasets

### Geographic Layers
Each dataset covers all fiscal years (FY2008-2024) with quarterly granularity:

#### `geography_country_all_FY2008_2024.csv`
- **Scope**: International and domestic spending totals
- **Geographic Coverage**: Countries worldwide where federal funds were spent
- **Use Cases**: International aid analysis, domestic vs international spending comparison

#### `geography_state_all_FY2008_2024.csv`  
- **Scope**: U.S. state and territory spending totals
- **Geographic Coverage**: All 50 states plus U.S. territories
- **Use Cases**: State-by-state federal investment analysis, regional equity studies

#### `geography_county_all_FY2008_2024.csv`
- **Scope**: County-level spending distribution
- **Geographic Coverage**: ~3,000 U.S. counties with FIPS codes
- **Use Cases**: Local economic impact analysis, rural vs urban spending patterns

#### `geography_district_all_FY2008_2024.csv`
- **Scope**: Congressional district spending totals
- **Geographic Coverage**: All U.S. congressional districts (accounting for redistricting)
- **Use Cases**: Political analysis, district-level federal investment tracking

## Data Schema
Each dataset contains standardized columns:
- **`code`**: Geographic identifier (country code, state FIPS, county FIPS, district ID)
- **`name`**: Geographic display name
- **`amount`**: Total federal obligations/spending (numeric)
- **`population`**: Population data when available
- **`fy`**: Fiscal year (2008-2024)
- **`quarter`**: Quarter (1-4)
- **`geo_layer`**: Geographic granularity level

## Analysis Applications
- **Total spending by location** without agency attribution
- **Geographic distribution patterns** across jurisdictions
- **Regional equity analysis** comparing per-capita spending
- **Economic impact studies** by location
- **Baseline geographic analysis** for comparison with agency-filtered data

## Related Data
For agency-specific geographic analysis, see the [`agency-geography/`](../agency-geography/) folder.

---
**Data Source**: USASpending.gov Basic Geography API  
**Collection Method**: [`Geography_basic.ipynb`](../../Geography_basic.ipynb)
