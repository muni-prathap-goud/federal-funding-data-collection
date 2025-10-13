# 📊 Pipeline A: Hierarchical Federal Funding Data Collection

## Overview
A **6-stage hierarchical data pipeline** that systematically collects federal spending data across organizational levels, creating a complete picture from high-level budget categories down to individual transactions.

## Hierarchical Flow
```
Budget Function → Budget Subfunction → Agency → Federal Account → Recipient → Award
```

## 📋 Processing Stages

### 🧩 Stage 1: Budget Functions
**Purpose**: Top-level federal spending categories (e.g., National Defense, Health, Education)
- **Notebook**: `budget_function_subfunction_hierarchical_mapping.ipynb`
- **API Endpoint**: `/api/v2/spending/` with `type="budget_function"`
- **Output**: Quarterly budget function data with 3-digit codes

### 🧩 Stage 2: Budget Subfunctions  
**Purpose**: Detailed breakdown of each budget function into specific programs
- **Notebook**: `Function and Subfunction.ipynb`
- **API Endpoint**: `/api/v2/spending/` with `type="budget_subfunction"`
- **Input**: Budget function data from Stage 1
- **Output**: Subfunction spending data with hierarchical relationships

### 🧩 Stage 3: Agencies
**Purpose**: Federal agencies responsible for spending within each subfunction
- **Notebook**: Integrated within subfunction collection
- **API Endpoint**: `/api/v2/spending/` with `type="agency"`
- **Input**: Budget subfunction filters
- **Output**: Agency-level spending data

### 🧩 Stage 4: Federal Accounts
**Purpose**: Treasury accounts where federal funds are actually stored and managed
- **Notebooks**: 
  - `federal_account.ipynb` - Basic federal account collection
  - `federal_account_agency.ipynb` - Federal accounts with agency relationships
- **API Endpoint**: `/api/v2/spending/` with `type="federal_account"`
- **Input**: Agency data from Stage 3
- **Output**: Federal account details with treasury account codes

### 🧩 Stage 5: Recipients
**Purpose**: Entities that received federal funding (companies, universities, states, nonprofits)
- **Notebook**: `recipient.ipynb`
- **API Endpoint**: `/api/v2/spending/` with `type="recipient"`
- **Input**: Federal account data from Stage 4
- **Output**: Recipient details with UEI/DUNS codes and obligation amounts

### 🧩 Stage 6: Awards
**Purpose**: Individual grants, contracts, and payments made to recipients
- **Notebook**: `awards.ipynb`
- **API Endpoint**: `/api/v2/spending/` with `type="award"`
- **Input**: Federal account data from Stage 4
- **Output**: Award-level transaction data

## 🔗 Hierarchical Relationships

| Level | Parent Key | Child Key | Relationship |
|-------|------------|-----------|--------------|
| Budget Function | `budget_function_code` | `budget_subfunction_code` | One-to-many |
| Budget Subfunction | `budget_subfunction_code` | `agency_id` | One-to-many |
| Agency | `agency_id` | `federal_account_code` | One-to-many |
| Federal Account | `federal_account_code` | `recipient_id` | One-to-many |
| Recipient | `recipient_id` | `award_id` | One-to-many |

## 💡 What This Pipeline Answers

| Dataset | Level | Key Question |
|---------|-------|-------------|
| Budget Functions | High-level | How much money goes into each federal mission area? |
| Budget Subfunctions | Mid-level | How is spending split into specific programs? |
| Agencies | Organizational | Which agencies are responsible for the spending? |
| Federal Accounts | Financial | Which treasury accounts fund the spending? |
| Recipients | Entity-level | Who received the federal funds? |
| Awards | Transaction-level | What exact awards or contracts were made? |

## 🚀 Usage

### Execution Order
Run notebooks in the following sequence for complete data collection:

1. **Budget Functions & Subfunctions**: `Function and Subfunction.ipynb`
2. **Federal Accounts**: 
   - `federal_account.ipynb` (basic collection)
   - OR `federal_account_agency.ipynb` (with agency relationships)
3. **Recipients**: `recipient.ipynb`
4. **Awards**: `awards.ipynb`

### Key Features
- **🚀 Parallel Processing**: ThreadPoolExecutor with 10-50 concurrent workers
- **🔄 Intelligent Retry System**: Period-scoped failure recovery
- **🛡️ Defensive Programming**: Robust error handling and file corruption protection
- **📅 Quarter-Only Strategy**: Focused data collection approach
- **🔑 Composite Key Deduplication**: Prevents duplicate records across runs

## 📊 Expected Outputs

### Final Consolidated Datasets (after running data-consolidation pipeline):
- **`agency_ALL_FY.csv`** (681KB) - Complete agency directory with spending data
- **`federal_accounts_ALL_FY.csv`** (6.1MB) - Treasury account information  
- **`federal_accounts_with_agency_ALL_FY.csv`** (7.5MB) - Enhanced federal account data
- **`recipients_ALL_FY.csv`** (1.5GB) - Complete recipient database
- **`awards_ALL_FY.csv`** (610MB) - Individual awards/contracts/grants data

## 🎯 Analysis Capabilities

This hierarchical data enables:
- **Budget allocation analysis** across federal missions
- **Agency performance evaluation** within specific program areas
- **Recipient network analysis** showing funding relationships
- **Award pattern recognition** and contract analysis
- **Multi-level aggregation** from transactions to budget functions
- **Trend analysis** across organizational hierarchy levels

---

**Next Step**: After collecting hierarchical data, run the [Data Consolidation Pipeline](../data-consolidation/) to create analysis-ready consolidated datasets.
