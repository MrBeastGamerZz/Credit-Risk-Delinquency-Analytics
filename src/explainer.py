import pandas as pd
import numpy as np
import shap
import joblib
import matplotlib.pyplot as plt
from pathlib import Path


def explain(df, feature_cols):
    """
    Explain the model predictions using SHAP.
    df must be the featured dataset.
    feature_cols must be the same list from model training.
    """

    # Load the saved model
    model = joblib.load("outputs/model/xgb_model.pkl")
    print("Model loaded")

    # Prepare features — same encoding as training
    df_enc = pd.get_dummies(
        df,
        columns=["Employment_Status", "Credit_Card_Type"],
        drop_first=True
    )
    X = df_enc[[c for c in feature_cols if c in df_enc.columns]]
    print(f"Features ready: {X.shape}")

    #Calculate SHAP values
    # This tells us how much each feature pushed each score up or down
    print("Calculating SHAP values... (takes about 30 seconds)")
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    print("SHAP values done")

    Path("outputs/plots").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)

    # Chart 1: Which features matter most overall 
    plt.figure(figsize=(10, 7))
    shap.summary_plot(
        shap_values, X,
        plot_type="bar",
        show=False,
        max_display=12
    )
    plt.title("Top Features by Importance (SHAP)", fontsize=14)
    plt.tight_layout()
    plt.savefig("outputs/plots/07_shap_importance.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 7 saved: SHAP importance")

    # Chart 2: Direction of impact for each feature
    # Red = pushes score toward delinquent
    # Blue = pushes score away from delinquent
    plt.figure(figsize=(10, 7))
    shap.summary_plot(shap_values, X, show=False, max_display=12)
    plt.title("Feature Impact Direction (SHAP)", fontsize=14)
    plt.tight_layout()
    plt.savefig("outputs/plots/08_shap_direction.png",
                dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 8 saved: SHAP direction")

    #Chart 3: Explain one specific customer
    # We pick the highest risk customer to explain
    risk_scores  = model.predict_proba(X)[:, 1]
    highest_idx  = np.argmax(risk_scores)
    highest_score = risk_scores[highest_idx]

    print(f"Explaining highest risk customer")
    print(f"  Index: {highest_idx}, Score: {highest_score:.3f}")

    plt.figure(figsize=(10, 5))
    shap.waterfall_plot(
        shap.Explanation(
            values=shap_values[highest_idx],
            base_values=explainer.expected_value,
            data=X.iloc[highest_idx],
            feature_names=X.columns.tolist()
        ),
        show=False
    )
    plt.title(f"Why This Customer Is High Risk — Score: {highest_score:.3f}", fontsize=13)
    plt.tight_layout()
    plt.savefig("outputs/plots/09_shap_waterfall.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 9 saved: SHAP waterfall")

    #Export SHAP data to CSV for Power BI
    shap_df = pd.DataFrame(shap_values, columns=X.columns)
    shap_df["Customer_ID"]        = df["Customer_ID"].values
    shap_df["Risk_Score"]         = risk_scores
    shap_df["Delinquent_Account"] = df["Delinquent_Account"].values

    # Which feature had the biggest impact on each customer's score
    shap_df["Top_Risk_Factor"] = (
        shap_df[X.columns.tolist()].abs().idxmax(axis=1)
    )

    shap_df.to_csv("outputs/reports/shap_summary.csv", index=False)
    print("SHAP summary saved to outputs/reports/shap_summary.csv")

    return shap_df


# Run directly to test
if __name__ == "__main__":
    import json

    df = pd.read_csv("excel data/featured.csv")
    print(f"Loaded: {df.shape}")

    # Load feature list from saved metrics
    with open("outputs/reports/metrics.json") as f:
        metrics = json.load(f)

    # Re-create the feature list the same way as model.py
    FEATURE_COLS = [
        "Age", "Income", "Credit_Score",
        "Credit_Utilization", "Missed_Payments",
        "Loan_Balance", "Debt_to_Income_Ratio",
        "Account_Tenure", "Payment_Risk_Score",
        "Consecutive_Miss",
        "Month_1", "Month_2", "Month_3",
        "Month_4", "Month_5", "Month_6",
    ]
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

    shap_df = explain(df, feature_cols)
    print("\nCompleted...")