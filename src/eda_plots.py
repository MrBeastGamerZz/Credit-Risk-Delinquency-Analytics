import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
# All charts go here
OUTPUT_DIR = Path("outputs/plots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_all(df):
    chart_1_employment(df)
    chart_2_missed_payments(df)
    chart_3_credit_utilization(df)
    chart_4_age_group(df)
    chart_5_payment_risk_score(df)
    chart_6_risk_tier(df)
    print("All 6 charts saved to outputs/plots/")

#Chart 1: Delinquency Rate by Employment Status
def chart_1_employment(df):
    # Calculate delinquency rate per employment group
    rates = df.groupby("Employment_Status")["Delinquent_Account"].mean() * 100
    rates = rates.sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(rates.index, rates.values, color=["#C0392B", "#E67E22", "#3498DB", "#27AE60"])
    # Add percentage label on top of each bar
    for i, val in enumerate(rates.values):
        ax.text(i, val + 0.3, f"{val:.1f}%",
                ha="center", fontsize=11, fontweight="bold")
    # Dotted line showing the overall average (16%)
    ax.axhline(y=16, color="black", linestyle="--", alpha=0.5, label="Portfolio avg 16%")
    ax.set_title("Delinquency Rate by Employment Status", fontsize=14)
    ax.set_ylabel("Delinquency Rate (%)")
    ax.set_xlabel("Employment Status")
    ax.legend()

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "01_employment.png", dpi=150)
    plt.close()
    print("Chart 1 saved")

#Chart 2: Delinquency Rate by Missed Payments Count
def chart_2_missed_payments(df):
    rates = df.groupby("Missed_Payments")["Delinquent_Account"].mean() * 100
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(rates.index, rates.values, marker="o", linewidth=2.5, color="#C0392B", markersize=8)
    ax.fill_between(rates.index, rates.values, alpha=0.15, color="#C0392B")
    # Add percentage label above each point
    for x, y in zip(rates.index, rates.values):
        ax.annotate(f"{y:.1f}%", (x, y),
                    textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=10)
    ax.set_title("Delinquency Rate vs Missed Payments", fontsize=14)
    ax.set_ylabel("Delinquency Rate (%)")
    ax.set_xlabel("Number of Missed Payments in Last 12 Months")
    ax.set_xticks(rates.index)

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "02_missed_payments.png", dpi=150)
    plt.close()
    print("Chart 2 saved")

#Chart 3: Credit Utilization Distribution
def chart_3_credit_utilization(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    # Two overlapping histograms — one for each group
    df[df["Delinquent_Account"] == 0]["Credit_Utilization"].hist(
        bins=20, ax=ax, alpha=0.6,
        color="#3498DB", label="Not Delinquent")
    df[df["Delinquent_Account"] == 1]["Credit_Utilization"].hist(
        bins=20, ax=ax, alpha=0.6,
        color="#C0392B", label="Delinquent")
    ax.set_title("Credit Utilization by Delinquency Status", fontsize=14)
    ax.set_xlabel("Credit Utilization (0 = 0%, 1 = 100%)")
    ax.set_ylabel("Number of Customers")
    ax.legend()

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "03_credit_utilization.png", dpi=150)
    plt.close()
    print("Chart 3 saved")

# Chart 4: Delinquency Rate by Age Group
def chart_4_age_group(df):
    # Use the Age Bracket column you created in Excel
    col = "Age Bracket"
    order = ["18-30", "31-45", "46-60", "61+"]
    rates = df.groupby(col)["Delinquent_Account"].mean() * 100
    rates = rates.reindex(order)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(rates.index, rates.values, color=["#27AE60", "#3498DB", "#C0392B", "#9B59B6"])
    for bar, val in zip(bars, rates.values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"{val:.1f}%", ha="center",
                fontsize=11, fontweight="bold")
    ax.axhline(y=16, color="black", linestyle="--", alpha=0.5, label="Portfolio avg 16%")
    ax.set_title("Delinquency Rate by Age Group", fontsize=14)
    ax.set_ylabel("Delinquency Rate (%)")
    ax.set_xlabel("Age Group")
    ax.legend()

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "04_age_group.png", dpi=150)
    plt.close()
    print("Chart 4 saved")

# Chart 5: Delinquency Rate by Payment Risk Score 
def chart_5_payment_risk_score(df):
    rates = df.groupby("Payment_Risk_Score")["Delinquent_Account"].mean() * 100
    # Colour each bar by risk level
    bar_colors = []
    for score in rates.index:
        if score <= 5:
            bar_colors.append("#27AE60")   # green = low risk
        elif score <= 9:
            bar_colors.append("#E67E22")   # orange = medium
        else:
            bar_colors.append("#C0392B")   # red = high risk
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(rates.index, rates.values, color=bar_colors)
    ax.set_title("Delinquency Rate by Payment Risk Score (0–12)", fontsize=14)
    ax.set_ylabel("Delinquency Rate (%)")
    ax.set_xlabel("Payment Risk Score")
    ax.set_xticks(rates.index)

    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "05_payment_risk_score.png", dpi=150)
    plt.close()
    print("Chart 5 saved")

#Chart 6: Customer Count and Delinquency Rate by Risk Tier
def chart_6_risk_tier(df):
    tier_counts = df["Risk_Tier"].value_counts()
    tier_rates  = df.groupby("Risk_Tier")["Delinquent_Account"].mean() * 100
    tier_order = ["High Risk", "Medium Risk", "Low Risk"]
    tier_counts = tier_counts.reindex(tier_order)
    tier_rates  = tier_rates.reindex(tier_order)
    colors = ["#C0392B", "#E67E22", "#27AE60"]

    # Two side-by-side charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    # Left: how many customers in each tier
    ax1.bar(tier_counts.index, tier_counts.values, color=colors)
    ax1.set_title("Customers per Risk Tier", fontsize=13)
    ax1.set_ylabel("Number of Customers")

    # Right: delinquency rate in each tier
    bars = ax2.bar(tier_rates.index, tier_rates.values, color=colors)
    ax2.set_title("Delinquency Rate per Risk Tier", fontsize=13)
    ax2.set_ylabel("Delinquency Rate (%)")
    for bar, val in zip(bars, tier_rates.values):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.3,
                 f"{val:.1f}%", ha="center", fontweight="bold")

    fig.suptitle("Risk Tier Analysis — Geldium", fontsize=14)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "06_risk_tier.png", dpi=150)
    plt.close()
    print("Chart 6 saved")

# Run directly to test 
if __name__ == "__main__":

    df = pd.read_csv("excel data/featured.csv")
    print(f"Loaded: {df.shape}")
    plot_all(df)
    print("\nCompleted...")