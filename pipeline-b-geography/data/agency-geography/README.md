# Agency-Geography Data

## 🏛️ Overview
This folder contains **agency-filtered geographic spending data** showing federal spending by location broken down by specific agencies. Each dataset provides both funding and awarding agency perspectives.

## 📊 Datasets

### Dual Agency Perspectives
Each geographic layer includes both funding and awarding agency views:

#### Country Level
- **`geo_country_funding_ALL_FY.csv`**: Country spending by funding agencies
- **`geo_country_awarding_ALL_FY.csv`**: Country spending by awarding agencies

#### State Level  
- **`geo_state_funding_ALL_FY.csv`**: State spending by funding agencies
- **`geo_state_awarding_ALL_FY.csv`**: State spending by awarding agencies

#### County Level
- **`geo_county_funding_ALL_FY.csv`**: County spending by funding agencies
- **`geo_county_awarding_ALL_FY.csv`**: County spending by awarding agencies

#### Congressional District Level
- **`geo_district_funding_ALL_FY.csv`**: District spending by funding agencies
- **`geo_district_awarding_ALL_FY.csv`**: District spending by awarding agencies

## 🔍 Enhanced Data Schema
Each dataset contains all basic geography columns plus agency attribution:

### Geographic & Financial Data
- **`code`**: Geographic identifier (country/state/county/district code)
- **`name`**: Geographic display name
- **`amount`**: Federal obligations/spending amount
- **`population`**: Population data when available

### Temporal Dimensions
- **`fy`**: Fiscal year (2008-2024)
- **`quarter`**: Quarter (1-4)

### Agency Attribution
- **`agency_type`**: "funding" or "awarding" - agency role perspective
- **`agency_code`**: 3-digit top-tier federal agency code
- **`agency_name`**: Official federal agency name
- **`geo_layer`**: Geographic granularity level

### County-Specific Enhancements
For county datasets only:
- **`state_code`**: State FIPS code (first 2 digits of county code)
- **`state_name`**: State name derived from FIPS mapping

## 📈 Analysis Applications

### Agency Geographic Footprint
- **Which agencies spend where**: Agency-specific geographic distribution
- **Funding vs awarding patterns**: Compare agencies that provide funds vs execute spending
- **Agency specialization**: Geographic concentration by mission area

### Cross-Dimensional Analysis
- **Agency × Geography × Time**: Multi-dimensional spending analysis
- **Regional agency presence**: Which agencies are active in specific regions
- **Mission geography**: How different federal missions distribute geographically

### Comparative Studies
- **Agency efficiency by location**: Compare similar agencies across regions
- **Geographic equity by agency**: Fair distribution analysis per agency
- **Funding flow analysis**: Track money from funding to awarding agencies by location

## 🗃️ Supporting Files
- **`toptier_roster_cache.csv`**: Cached federal agency directory used for processing

## 🔗 Related Data
For total geographic spending without agency breakdown, see [`basic-geography/`](../basic-geography/) folder.

---
**Data Source**: USASpending.gov Agency-Geography API  
**Collection Method**: [`agency_geography.ipynb`](../../agency_geography.ipynb)
