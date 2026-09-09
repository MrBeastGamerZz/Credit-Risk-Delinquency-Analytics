import pandas as pd
from pathlib import Path

def preprocess(df):
    # Always work on a copy so original data is safe
    df = df.copy()

    #Fix 1: Cap Credit_Utilization at 1.0
    # 4 records have values above 1.0 (impossible — max is 100%)
    # Excel didn't fix these, so Python handles it here
    over_100 = (df["Credit_Utilization"] > 1.0).sum()
    df["Credit_Utilization"] = df["Credit_Utilization"].clip(upper=1.0)
    print(f"Credit_Utilization: capped {over_100} records at 1.0")

    #Fix 2: Encode Month columns from text to numbers
    # ML models can't read text — they need numbers
    # On-time = 0, Late = 1, Missed = 2
    encode_map = {"On-time": 0, "Late": 1, "Missed": 2}
    month_cols = ["Month_1", "Month_2", "Month_3","Month_4", "Month_5", "Month_6"]

    for col in month_cols:
        df[col] = df[col].map(encode_map)
    print(f"Month columns encoded: On-time=0, Late=1, Missed=2")

    # Check: confirm no missing values 
    # Excel already filled them — this just double checks
    total_missing = df.isnull().sum().sum()
    print(f"Missing values remaining: {total_missing}")
    print(f"Preprocessing done. Shape: {df.shape}")
    return df

# Run this file directly to test 
if __name__ == "__main__":
    # Load the cleaned CSV from Excel
    df_raw = pd.read_csv("excel data/processed/Cleaned_dataset.csv")
    print(f"Loaded: {df_raw.shape}")
    # Clean it
    df_clean = preprocess(df_raw)
    # Save to processed folder
    Path("data").mkdir(parents=True, exist_ok=True)
    df_clean.to_csv("excel data/fully_cleaned.csv", index=False)
    print("Saved to excel data/fully_cleaned.csv")