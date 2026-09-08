import pandas as pd
from pathlib import Path

def engineer_features(df):
    df = df.copy()
    month_cols = ["Month_1", "Month_2", "Month_3","Month_4", "Month_5", "Month_6"]

    # New Feature 1: Payment_Risk_Score
    # Add up all 6 month columns
    # Each month is 0, 1, or 2 — so total range is 0 to 12
    # Higher score = worse payment history
    df["Payment_Risk_Score"] = df[month_cols].sum(axis=1)
    print(f"Payment_Risk_Score created")
    print(f"  Min: {df['Payment_Risk_Score'].min()}")
    print(f"  Max: {df['Payment_Risk_Score'].max()}")

    #New Feature 2: Consecutive_Miss
    # Count how many months had value = 2 (fully Missed)
    # Late payments (1) are not counted here — only full misses
    df["Consecutive_Miss"] = (df[month_cols] == 2).sum(axis=1)
    print(f"Consecutive_Miss created")
    print(f"  Max months fully missed: {df['Consecutive_Miss'].max()}")

    #New Feature 3: Risk_Tier 
    # Simple rule to put each customer in a risk bucket
    # Based on their Payment_Risk_Score
    def get_tier(score):
        if score > 9:
            return "High Risk"
        elif score > 5:
            return "Medium Risk"
        else:
            return "Low Risk"
    df["Risk_Tier"] = df["Payment_Risk_Score"].apply(get_tier)
    print(f"Risk_Tier created")
    print(df["Risk_Tier"].value_counts().to_string())
    print(f"Feature engineering done. New shape: {df.shape}")
    return df

#Run directly to test 
if __name__ == "__main__":

    df = pd.read_csv("excel data/fully_cleaned.csv")
    print(f"Loaded: {df.shape}")

    df = engineer_features(df)

    Path("excel data").mkdir(parents=True, exist_ok=True)
    df.to_csv("excel data/featured.csv", index=False)
    print("Saved to data/...featured.csv")