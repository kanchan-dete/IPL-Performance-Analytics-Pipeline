# IPL Performance Analytics & Data Pipeline

An end-to-end data engineering and analytics pipeline built to ingest large-scale sports datasets, perform robust data cleaning and schema enforcement using Python (Pandas), and load structured ball-by-ball records into a relational SQLite database for advanced analytics.

---

## 🛠️ Tech Stack
* **Language:** Python
* **Data Processing & Cleansing:** Pandas, Lambda Functions
* **Data Storage / Warehouse:** SQLite (Relational Database)
* **Logging & Monitoring:** Python `logging` module with structured tracking

---

## 🔄 Pipeline Workflow

1. **Extract:** 
   * Ingests raw ball-by-ball cricket match delivery records from CSV sources (`raw_ipl_matches.csv`).
2. **Transform:**
   * **Imputation:** Fills missing batsman, bowler, and venue names with default tags (`Unknown Player`, `Neutral Venue`).
   * **Type Casting & Validation:** Enforces strict numeric types on runs and wickets, dropping corrupted fields safely.
   * **Feature Engineering:** Computes secondary metrics such as boundary indicators (`is_boundary`) from raw run values.
   * **Deduplication:** Filters out redundant rows to maintain database hygiene.
3. **Load:**
   * Automatically initializes a relational schema (`fact_ipl_deliveries`) with defined columns.
   * Executes high-performance bulk insertions into the SQLite data warehouse.

---

## 📁 Project File Structure
```text
IPL-Performance-Analytics-Pipeline/
│
├── ipl_etl_pipeline.py       # Main Python ETL script with logging and class-based architecture
├── raw_ipl_matches.csv       # Sample raw match and delivery source data
└── README.md                 # Project documentation
