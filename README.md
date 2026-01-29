# Federal Funding Data Collection Pipelines

A comprehensive data collection system for extracting federal spending data from USASpending.gov API, organized into **two specialized pipelines** for different analytical perspectives.

## Quick Start

Choose your analysis focus and navigate to the appropriate pipeline:

| Analysis Goal | Pipeline | Quick Link |
|---------------|----------|------------|
| **Budget & Agency Analysis** | Hierarchical Pipeline | [`pipeline-a-hierarchical/`](pipeline-a-hierarchical/) |
| **Geographic Analysis** | Geography Pipeline | [`pipeline-b-geography/`](pipeline-b-geography/) |

## Pipeline Overview

### Pipeline A: Hierarchical Data Collection
**What it does**: Collects federal spending data through organizational hierarchy (Budget Functions → Agencies → Recipients → Awards)

**Use for**: Budget analysis, agency performance, recipient research, award tracking

**[Full Documentation & Notebooks →](pipeline-a-hierarchical/)**

### Pipeline B: Geographic Data Collection  
**What it does**: Collects federal spending data by location (Country/State/County/District) with optional agency filtering

**Use for**: Geographic spending analysis, regional impact studies, congressional district research

**[Full Documentation & Notebooks →](pipeline-b-geography/)**

## Project Structure

```
federal-funding-data-collection/
├── pipeline-a-hierarchical/          # Hierarchical Pipeline + Data
├── pipeline-b-geography/             # Geography Pipeline + Data
├── README.md                         # This overview
└── requirements.txt                  # Python dependencies
```

Each pipeline folder contains:
- **Detailed README.md** with complete documentation
- **Jupyter notebooks** for data collection
- **Data folder** with relevant datasets

## Usage

### Prerequisites
```bash
pip install -r requirements.txt
```

### Getting Started

1. **Choose your pipeline** based on analysis needs (see Quick Start table above)
2. **Navigate to the pipeline folder** and read the detailed README
3. **Run the Jupyter notebooks** in the suggested order

### Running Pipelines

#### Pipeline A: Hierarchical Collection
Navigate to `pipeline-a-hierarchical/` and follow the detailed documentation for:
- Budget function and subfunction collection
- Agency and federal account data collection  
- Recipient and award data collection

#### Pipeline B: Geography Collection
Navigate to `pipeline-b-geography/` and follow the detailed documentation for:
- Basic geographic spending collection
- Agency-filtered geographic spending collection

## Key Features

- **Parallel Processing**: Efficient data collection with concurrent API calls
- **Intelligent Retry Logic**: Robust error handling and recovery
- **Multiple Data Perspectives**: Hierarchical and geographic views
- **Data Quality Assurance**: Built-in validation and quality checks
- **Comprehensive Documentation**: Detailed READMEs in each pipeline folder
- **Analysis-Ready Output**: Final datasets ready for research and analysis

## Data Coverage

- **Temporal**: Federal fiscal years 2008-2024 (quarterly granularity)
- **Organizational**: Budget functions, agencies, federal accounts, recipients, awards
- **Geographic**: Country, state, county, and congressional district levels
- **Scale**: Multi-GB datasets covering comprehensive federal spending

## Quick Navigation

### For Budget & Agency Analysis
**Start here**: [`pipeline-a-hierarchical/`](pipeline-a-hierarchical/)
- Understand federal spending by organizational structure
- Track funding flows from budget functions to individual awards
- Analyze agency performance and recipient patterns

### For Geographic Analysis  
**Start here**: [`pipeline-b-geography/`](pipeline-b-geography/)
- Analyze federal spending by location
- Compare regional distribution of federal funds
- Study congressional district funding patterns

---

**Data Source**: [USASpending.gov](https://www.usaspending.gov/) - Official source of federal spending data  
**API Documentation**: [USASpending.gov API](https://api.usaspending.gov/)

**Repository Organization**: Each pipeline is self-contained with dedicated documentation, notebooks, and data folders for optimal collaboration and understanding.
