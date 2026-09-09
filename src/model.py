import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score, f1_score,
                             precision_score, recall_score,
                             confusion_matrix)
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

# Settings
# Lower threshold means we catch more delinquent customers
# 0.40 instead of default 0.50 — better for collections use case
THRESHOLD = 0.40

# Columns the model learns from
FEATURE_COLS = [
    "Age", "Income", "Credit_Score",
    "Credit_Utilization", "Missed_Payments",
    "Loan_Balance", "Debt_to_Income_Ratio",
    "Account_Tenure", "Payment_Risk_Score",
    "Consecutive_Miss",
    "Month_1", "Month_2", "Month_3",
    "Month_4", "Month_5", "Month_6",
]

TARGET = "Delinquent_Account"

def prepare_data(df):
    """Split data into train and test sets."""
    df = df.copy()
    # Convert text categories to numbers using one-hot encoding
    # This turns Employment_Status into separate 0/1 columns
    df = pd.get_dummies(df, columns=["Employment_Status", "Credit_Card_Type"], drop_first=True)

    # Get the new encoded column names
    encoded = [c for c in df.columns
               if c.startswith("Employment_Status_")
               or c.startswith("Credit_Card_Type_")]
    features = FEATURE_COLS + encoded
    features = [f for f in features if f in df.columns]
    X = df[features]
    y = df[TARGET]

    # Split: 80% for training, 20% for testing
    # stratify=y keeps the 84:16 ratio in both splits
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
    print(f"Train set: {X_train.shape}")
    print(f"Test set:  {X_test.shape}")
    print(f"Train delinquency rate: {y_train.mean()*100:.1f}%")

    # Apply SMOTE to balance the training data
    # Without this the model mostly sees non-delinquent customers
    # SMOTE creates extra synthetic delinquent examples
    smote = SMOTE(random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)
    print(f"After SMOTE — Train: {X_train.shape}")
    print(f"After SMOTE — Delinquency rate: {y_train.mean()*100:.1f}%")
    return X_train, X_test, y_train, y_test, features


def evaluate(model, X_test, y_test, model_name):
    """Print evaluation results for one model."""
    # Get probability scores (0.0 to 1.0)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # Apply our custom threshold
    y_pred = (y_proba >= THRESHOLD).astype(int)
    auc  = roc_auc_score(y_test, y_proba)
    f1   = f1_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec  = recall_score(y_test, y_pred)
    cm   = confusion_matrix(y_test, y_pred)
    print(f"\n--- {model_name} (threshold={THRESHOLD}) ---")
    print(f"  AUC-ROC   : {auc:.4f}  (want > 0.75)")
    print(f"  Recall    : {rec:.4f}  (want > 0.70)")
    print(f"  Precision : {prec:.4f}")
    print(f"  F1 Score  : {f1:.4f}  (want > 0.55)")
    print(f"  Confusion Matrix:")
    print(f"    TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"    FN={cm[1,0]}  TP={cm[1,1]}")

    return {
        "model":     model_name,
        "auc":       round(auc, 4),
        "recall":    round(rec, 4),
        "precision": round(prec, 4),
        "f1":        round(f1, 4),
        "threshold": THRESHOLD
    }


def train(df):
    """Main function — trains both models, saves the best one."""
    print("\nPreparing data...")
    X_train, X_test, y_train, y_test, features = prepare_data(df)

    # Model 1: Logistic Regression (baseline)
    print("\nTraining Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_results = evaluate(lr_model, X_test, y_test, "Logistic Regression")

    #Model 2: XGBoost (main model) 
    print("\nTraining XGBoost...")
    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        scale_pos_weight=5,    # gives extra weight to delinquent class
        random_state=42,
        eval_metric="logloss",
        verbosity=0
    )
    xgb_model.fit(X_train, y_train)
    xgb_results = evaluate(xgb_model, X_test, y_test, "XGBoost")

    #Save model 
    Path("outputs/model").mkdir(parents=True, exist_ok=True)
    joblib.dump(xgb_model, "outputs/model/xgb_model.pkl")
    print("\nModel saved to outputs/model/xgb_model.pkl")

    #Save metrics to JSON
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    all_results = {
        "logistic_regression": lr_results,
        "xgboost": xgb_results
    }
    with open("outputs/reports/metrics.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("Metrics saved to outputs/reports/metrics.json")
    return xgb_model, features

# Run directly to test
if __name__ == "__main__":

    df = pd.read_csv("excel data/featured.csv")
    print(f"Loaded: {df.shape}")

    model, feature_cols = train(df)
    print("\nModel training complete.")