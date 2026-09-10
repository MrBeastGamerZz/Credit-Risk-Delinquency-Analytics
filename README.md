# Credit Risk & Delinquency Analytics

> An end-to-end data analytics and machine learning project that identifies customer delinquency risk, segments at-risk portfolios, and delivers actionable collections intelligence — built across Excel, SQL, Python, and Power BI.

---

## Project Overview

This project analyses the credit behaviour of 500 customers to predict which ones are most likely to miss payments beyond the 30-day threshold — a key metric in credit portfolio management. Starting from raw data exploration all the way through to an interactive collections dashboard, it replicates the kind of end-to-end analytical workflow used by data and risk teams in financial services.

The project was built in 8 structured phases, each using the tool most appropriate for that stage of the analytical pipeline.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| **Excel** | Exploratory data analysis, data cleaning, pivot table analysis |
| **SQL (SQLite)** | Data querying, aggregation, rule-based risk scoring, view creation |
| **Python** | Preprocessing, feature engineering, ML modelling, SHAP explainability |
| **Power BI** | Interactive stakeholder dashboard with slicers and KPI cards |

**Python Libraries:** `pandas` · `numpy` · `scikit-learn` · `xgboost` · `imbalanced-learn` · `shap` · `matplotlib` · `seaborn` · `joblib` · `sqlite3`

---

## Repository Structure

```
Credit-Risk-Delinquency-Analytics_Project/
│
├── excel data/
│   ├── eda in excel/
│   │   └── Delinquency_prediction_dataset.xlsx   ← Phase 1: EDA workbook (raw + cleaned + pivots)
│   ├── processed/
│   │   └── Cleaned_dataset.csv                   ← Excel-cleaned output used in Python
│   └── raw/
│       ├── Delinquency_prediction_dataset.xlsx    ← Original raw dataset
│       ├── featured.csv                           ← Feature-engineered dataset
│       └── fully_cleaned.csv                      ← Final cleaned dataset
│
├── outputs/
│   ├── model/
│   │   └── xgb_model.pkl                         ← Trained XGBoost model
│   ├── plots/
│   │   ├── 01_employment.png                      ← Delinquency rate by employment status
│   │   ├── 02_missed_payments.png                 ← Delinquency rate vs missed payments
│   │   ├── 03_credit_utilization.png              ← Credit utilization distribution
│   │   ├── 04_age_group.png                       ← Delinquency rate by age group
│   │   ├── 05_payment_risk_score.png              ← Delinquency rate by payment risk score
│   │   ├── 06_risk_tier.png                       ← Risk tier breakdown
│   │   ├── 07_shap_importance.png                 ← SHAP global feature importance
│   │   ├── 08_shap_direction.png                  ← SHAP feature impact direction
│   │   └── 09_shap_waterfall.png                  ← SHAP waterfall for highest-risk customer
│   └── reports/
│       ├── dashboard_data.csv                     ← Final dataset powering Power BI dashboard
│       ├── metrics.json                           ← Model evaluation results (AUC, F1, Recall)
│       └── shap_summary.csv                       ← Per-customer SHAP values + top risk factor
│
├── powerbi/
│   └── risk_engine_dashboards.pbix               ← Phase 8: Interactive collections dashboard
│
├── sql/
│   ├── SQL_queries.sql                            ← Phase 2: All queries + view definition
│   └── geldium.db                                 ← SQLite database (customers + scored_customers)
│
├── src/
│   ├── preprocessor.py                            ← Phase 3: Data cleaning pipeline
│   ├── feature_engineer.py                        ← Phase 4: Feature creation
│   ├── eda_plots.py                               ← Phase 4: EDA chart generation
│   ├── model.py                                   ← Phase 5: Model training and evaluation
│   ├── explainer.py                               ← Phase 6: SHAP explainability
│   └── exporter.py                                ← Phase 7: Score export to SQL and CSV
│
├── .gitattributes
└── README.md
```

---

## Project Phases

### Phase 1 — Excel: Exploratory Data Analysis
- Profiled all 19 columns across 500 customer records
- Standardised `Employment_Status` from 6 inconsistent label variants to 4 clean categories
- Filled missing values using median imputation: `Income` (39 missing), `Loan_Balance` (29 missing), `Credit_Score` (2 missing)
- Created `Age Bracket` derived column for segment analysis
- Built pivot tables: delinquency rate by age group, employment status, card type, and missed payments count
- Flagged anomalies: 4 records with `Credit_Utilization` above 100%, 46 records with contradictory credit score vs missed payment combinations

### Phase 2 — SQL: Querying and Risk Scoring
- Loaded cleaned dataset into SQLite via DB Browser
- Wrote queries answering 4 key business questions: portfolio overview, delinquency by segment, missed payment patterns, and cross-segment risk
- Built a rule-based risk scoring CTE assigning each customer a risk point total based on missed payments, credit utilization, and employment status
- Created `customer_risk_view` — a pre-computed view combining customer profile, payment risk score, and rule-based tier, used as the Power BI data foundation

### Phase 3 — Python: Preprocessing
- Capped 4 records where `Credit_Utilization` exceeded 1.0 (impossible values)
- Encoded `Month_1` through `Month_6` from text (On-time/Late/Missed) to numeric (0/1/2)
- Confirmed zero missing values post-processing
- Output: `fully_cleaned.csv`

### Phase 4 — Python: Feature Engineering and EDA Visuals
- Created `Payment_Risk_Score`: sum of all 6 encoded month columns (range 0–12)
- Created `Consecutive_Miss`: count of months with value = 2 (fully missed)
- Created `Risk_Tier`: rule-based bucket (High / Medium / Low) based on payment risk score
- Generated 6 EDA charts saved to `outputs/plots/`
- Output: `featured.csv`

### Phase 5 — Python: Model Training and Evaluation
- Train/test split: 80/20 stratified to preserve 84:16 class imbalance ratio
- Applied SMOTE on training set only to balance the delinquent class
- Trained **Logistic Regression** as interpretable baseline
- Trained **XGBoost** as primary model with `scale_pos_weight=5` for imbalance handling
- Evaluated at calibrated threshold of **0.40** (lower than default 0.50 to prioritise Recall)
- Saved model to `outputs/model/xgb_model.pkl` and metrics to `outputs/reports/metrics.json`

| Metric | Logistic Regression | XGBoost |
|---|---|---|
| AUC-ROC | baseline | > 0.75 |
| Recall | baseline | > 0.70 |
| F1 Score | baseline | > 0.55 |

### Phase 6 — Python: SHAP Explainability
- Calculated SHAP values using `TreeExplainer` on the trained XGBoost model
- Generated global feature importance bar chart and direction dot plot
- Generated SHAP waterfall chart explaining the single highest-risk customer's score
- Exported per-customer SHAP values with `Top_Risk_Factor` column to `shap_summary.csv`
- Every flagged customer has a plain-language explanation of why they were scored high risk

### Phase 7 — Python + SQL: Export Results
- Scored all 500 customers using the trained model
- Assigned ML risk tier: High Risk (≥ 0.60), Medium Risk (0.40–0.59), Low Risk (< 0.40)
- Merged ML scores with SHAP top risk factors per customer
- Wrote `scored_customers` table back to `geldium.db`
- Exported `dashboard_data.csv` as the single data source for Power BI

### Phase 8 — Power BI: Collections Dashboard
Three-page interactive dashboard built on `dashboard_data.csv`:

- **Page 1 — Portfolio Overview:** KPI cards (total customers, delinquency rate, high-risk count, avg risk score), delinquency rate by employment status, risk tier donut chart, missed payments column chart
- **Page 2 — Risk Segment Explorer:** Four slicers (Risk Tier, Employment Status, Card Type, Age Bracket) filtering all visuals dynamically — delinquency rate by city, risk score vs credit utilization scatter chart
- **Page 3 — Top Risk Customers:** Sortable table of customers ranked by ML risk score with conditional colour formatting, top risk factor column, and most common risk driver bar chart

---

## Key Findings

- **16% overall delinquency rate** across the 500-customer portfolio (80 delinquent customers)
- **Payment behaviour** is the strongest delinquency signal — customers with a Payment Risk Score > 9 show a **29.4% delinquency rate**, nearly double the portfolio average
- **Unemployed customers** carry the highest delinquency rate at **19.4%** vs 11.5% for Retired customers
- **Business cardholders** are the highest-risk card segment at **21.3%** delinquency rate
- **Age group 46–60** shows the highest delinquency rate at **21.7%** — an unexpected finding that runs counter to the assumption that younger customers are always highest risk
- **No single feature dominates** — pairwise correlations between individual variables and the target are all below 0.07, confirming that a multivariate ML model outperforms simple rule-based scoring

---

## Ethical Considerations

- `Employment_Status` is never used as a sole trigger — payment behaviour must confirm the risk signal
- `Age` is excluded as a direct model feature and used only for post-hoc fairness monitoring
- Every flagged customer has a SHAP explanation — no black-box decisions
- Collections officers retain full override authority — the model prioritises, people decide
- False Positive Rate monitored across demographic groups — deviations above 15 percentage points trigger a fairness audit

---

## How to Run the Python Pipeline

**1. Clone the repo**
```bash
git clone https://github.com/MrBeastGamerZz/Credit-Risk-Delinquency-Analytics_Project.git
cd Credit-Risk-Delinquency-Analytics_Project
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run each phase**
```bash
python src/preprocessor.py
python src/feature_engineer.py
python src/eda_plots.py
python src/model.py
python src/explainer.py
python src/exporter.py
```

**4. Open the dashboard**

Open `powerbi/risk_engine_dashboards.pbix` in Power BI Desktop.

---

## Requirements

```
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.5.1
xgboost==2.1.0
imbalanced-learn==0.12.3
shap==0.45.1
matplotlib==3.9.1
seaborn==0.13.2
joblib==1.4.2
openpyxl==3.1.2
```

---

## Context

This project was developed as part of the **Tata iQ GenAI-Powered Data Analytics Job Simulation** on Forage (August 2026), in the role of an AI Transformation Consultant advising a fictional financial services client on reducing credit card delinquency through AI-driven intervention strategies.

The simulation involved four structured deliverables:
- **Task 1** — Exploratory Data Analysis and Risk Profiling (Word report)
- **Task 2** — Predictive Model Plan using GenAI assistance (Word report)
- **Task 3** — Business Summary Report and Collections Strategy (2-page Word report)
- **Task 4** — AI-Powered Collections System presentation (PowerPoint deck)

The portfolio project above extends those simulation deliverables into a fully coded, end-to-end technical implementation across all four tools.

---

## Author

**Manjunath**
Data Analytics Portfolio Project · 2026
[GitHub Profile](https://github.com/MrBeastGamerZz)
