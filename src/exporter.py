import pandas as pd
import numpy as np
import joblib
import sqlite3
from pathlib import Path

THRESHOLD = 0.40

FEATURE_COLS = [
    "Age", "Income", "Credit_Score",
    "Credit_Utilization", "Missed_Payments",
    "Loan_Balance", "Debt_to_Income_Ratio",
    "Account_Tenure", "Payment_Risk_Score",
    "Consecutive_Miss",
    "Month_1", "Month_2", "Month_3",
    "Month_4", "Month_5", "Month_6",
]

def export_scores(df, feature_cols, shap_df):
    """
    Score all customers.
    Write results to SQLite database.
    Export final CSV for Power BI.
    """
    # Load model
    model = joblib.load("outputs/model/xgb_model.pkl")
    print("Model loaded")

    # Prepare features — same encoding as training
    df_enc = pd.get_dummies(
        df,
        columns=["Employment_Status", "Credit_Card_Type"],
        drop_first=True
    )
    X = df_enc[[c for c in feature_cols if c in df_enc.columns]]

    # Score every customer
    risk_scores = model.predict_proba(X)[:, 1]

    # Assign tier based on score
    risk_tiers = []
    for score in risk_scores:
        if score >= 0.60:
            risk_tiers.append("High Risk")
        elif score >= 0.40:
            risk_tiers.append("Medium Risk")
        else:
            risk_tiers.append("Low Risk")

    print(f"Scored {len(risk_scores)} customers")

    #Build the output table
    output = df[[
        "Customer_ID", "Age", "Employment_Status",
        "Credit_Card_Type", "Location", "Income",
        "Credit_Score", "Credit_Utilization",
        "Missed_Payments", "Loan_Balance",
        "Debt_to_Income_Ratio", "Account_Tenure",
        "Payment_Risk_Score", "Delinquent_Account"
    ]].copy()

    output["ML_Risk_Score"] = risk_scores.round(4)
    output["ML_Risk_Tier"]  = risk_tiers

    # Add top SHAP factor from Phase 6
    if shap_df is not None:
        output = output.merge(
            shap_df[["Customer_ID", "Top_Risk_Factor"]],
            on="Customer_ID",
            how="left"
        )

    # Show tier distribution
    print("Risk tier split:")
    print(output["ML_Risk_Tier"].value_counts().to_string())

    # Save to SQLite
    conn = sqlite3.connect("sql/geldium.db")
    output.to_sql("scored_customers", conn,
                  if_exists="replace", index=False)
    conn.close()
    print("scored_customers table written to sql/geldium.db")

    # Export final CSV for Power BI
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    output.to_csv("outputs/reports/dashboard_data.csv", index=False)
    print(f"dashboard_data.csv saved")
    print(f"Shape: {output.shape}")
    return output


# Run directly to test
if __name__ == "__main__":

    df = pd.read_csv("excel data/featured.csv")
    print(f"Loaded: {df.shape}")

    # Load SHAP summary from Phase 6
    shap_df = pd.read_csv("outputs/reports/shap_summary.csv")

    # Rebuild feature list
    df_enc = pd.get_dummies(
        df,
        columns=["Employment_Status", "Credit_Card_Type"],
        drop_first=True
    )
    encoded = [c for c in df_enc.columns
               if c.startswith("Employment_Status_")
               or c.startswith("Credit_Card_Type_")]
    feature_cols = FEATURE_COLS + encoded
    feature_cols = [f for f in feature_cols if f in df_enc.columns]

    final_df = export_scores(df, feature_cols, shap_df)
    print("\nCompleted...")