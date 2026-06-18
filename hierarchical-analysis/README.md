# Hierarchical Analysis: Pipeline A Deep Dive

## Purpose
Comprehensive analysis of Pipeline A hierarchical federal funding data to understand government spending priorities, agency performance, and budget allocation patterns.

## Analysis Structure

### **Phase 1: Foundation Analysis**
- **`00_data_profiling.ipynb`** - Comprehensive data quality and structure analysis
- **`01_budget_function_analysis.ipynb`** - Federal spending priorities and budget structure

### **Phase 2: Entity Analysis** (Planned)
- **`02_agency_performance.ipynb`** - Agency efficiency and spending patterns
- **`03_federal_account_analysis.ipynb`** - Treasury account spending flows
- **`04_recipient_network.ipynb`** - Funding recipient patterns and relationships

### **Phase 3: Integration & Insights** (Planned)
- **`05_hierarchical_integration.ipynb`** - Cross-dataset insights and patterns
- **`06_temporal_trends.ipynb`** - Time series analysis (2017-2024)
- **`07_policy_insights.ipynb`** - Policy implications and recommendations

## Getting Started

### Prerequisites
```bash
# Install required packages
pip install pandas numpy matplotlib seaborn jupyter
```

### Data Requirements
Ensure Pipeline A data collection is complete:
- `budget_functions.csv` - Budget categories
- `budget_subfunctions.csv` - Program details  
- `budget_function_subfunction_mapping.csv` - Hierarchical relationships
- `budget_functions_quarterly_all.csv` - **NEW:** Quarterly function spending data
- `budget_subfunctions_quarterly_all.csv` - **NEW:** Quarterly subfunction spending data
- `agency_ALL_FY.csv` - Multi-year agency data
- `federal_accounts_ALL_FY.csv` - Treasury account data
- `recipients_ALL_FY.csv` - Federal funding recipients
- `awards_ALL_FY.csv` - Individual awards/contracts

### Analysis Workflow
1. **Start with Data Profiling** - Run `00_data_profiling.ipynb`
2. **Understand Budget Structure** - Run `01_budget_function_analysis.ipynb`
3. **Continue with Entity Analysis** - Based on your research interests

## Key Research Questions

### **Budget Function Analysis**
- What are the federal government's top spending priorities? (NOW WITH ACTUAL $ AMOUNTS!)
- How have budget allocations changed over time? (QUARTERLY TRENDS!)
- Which functions show growth/decline patterns? (TIME SERIES ANALYSIS!)
- How do high-level missions break down into specific programs?
- What are the seasonal spending patterns across quarters?
- Which budget functions have the most dramatic year-over-year changes?

### **Agency Performance Analysis**
- Which agencies are most efficient in their spending?
- How do agencies specialize across different budget functions?
- What are the patterns in agency growth and portfolio changes?
- How do agencies coordinate within budget functions?

### **Integration Analysis**
- How do budget priorities flow through the federal hierarchy?
- What are the relationships between functions, agencies, and recipients?
- Where are the gaps or overlaps in federal spending?
- What optimization opportunities exist?

## Analysis Outputs

Each notebook produces:
- **Data insights** with statistical summaries
- **Visualizations** showing key patterns and trends
- **Quality assessments** identifying data strengths/limitations
- **Next step recommendations** for continued analysis

## Expected Insights

- **Government Priorities**: Clear view of where federal money goes
- **Agency Effectiveness**: Performance metrics and efficiency comparisons
- **Spending Patterns**: Trends, cycles, and policy impacts
- **Network Effects**: How entities interact within the funding ecosystem
- **Policy Implications**: Data-driven recommendations for optimization

## Related Analysis

- **Pipeline B Geographic Analysis**: [`../geographic-analysis/`] (if created)
- **Data Collection**: [`../pipeline-a-hierarchical/`] - Source data and collection notebooks
- **Data Validation**: [`../pipeline-a-hierarchical/QuarterToOne.ipynb`] - Data consolidation process

## Notes

- **Large Files**: Some datasets may be excluded from Git due to size
- **Generation**: Run Pipeline A collection notebooks if data is missing
- **Performance**: Consider data sampling for initial exploration if files are very large
- **Updates**: Re-run analysis when new fiscal year data becomes available

---

**Status**: Foundation analysis ready | Entity analysis in development | Integration analysis planned
