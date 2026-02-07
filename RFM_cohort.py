import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# -------------------- Load Data --------------------
def load_sales_data():
    conn = sqlite3.connect("database/ecommerce.db")
    df = pd.read_sql("SELECT * FROM fact_sales", conn)
    conn.close()
    # Convert 'order_date' to datetime objects after loading from DB
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

# -------------------- RFM Analysis --------------------
def calculate_rfm(df):
    # Latest date in dataset for recency calculation
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)

    # RFM metrics
    rfm = df.groupby("customer_id").agg({
        "order_date": lambda x: (snapshot_date - x.max()).days,  # Recency
        "order_id": "nunique",                                   # Frequency
        "revenue": "sum"                                         # Monetary
    }).reset_index()

    rfm.rename(columns={
        "order_date": "Recency",
        "order_id": "Frequency",
        "revenue": "Monetary"
    }, inplace=True)

    # Merge customer names
    rfm = rfm.merge(df[["customer_id", "customer_name"]].drop_duplicates(), on="customer_id")

    # RFM scoring (1-5, higher = better)
    # For Recency:
    # Get the bin edges first, then use pd.cut with explicit labels
    _, recency_bins = pd.qcut(rfm["Recency"], 5, duplicates='drop', retbins=True)
    rfm["R_Score"] = pd.cut(rfm["Recency"], bins=recency_bins, labels=range(len(recency_bins)-1, 0, -1), include_lowest=True)

    # For Frequency:
    _, frequency_bins = pd.qcut(rfm["Frequency"], 5, duplicates='drop', retbins=True)
    rfm["F_Score"] = pd.cut(rfm["Frequency"], bins=frequency_bins, labels=range(1, len(frequency_bins)), include_lowest=True)

    # For Monetary:
    _, monetary_bins = pd.qcut(rfm["Monetary"], 5, duplicates='drop', retbins=True)
    rfm["M_Score"] = pd.cut(rfm["Monetary"], bins=monetary_bins, labels=range(1, len(monetary_bins)), include_lowest=True)

    # Combine scores
    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

    # Segment customers based on RFM score
    def segment_customer(row):
        # Ensure scores are integers for comparison
        r_score = int(row["R_Score"]) if pd.notna(row["R_Score"]) else 0
        f_score = int(row["F_Score"]) if pd.notna(row["F_Score"]) else 0
        m_score = int(row["M_Score"]) if pd.notna(row["M_Score"]) else 0

        if r_score >= 4 and f_score >= 4 and m_score >= 4:
            return "VIP"
        elif r_score >= 3 and f_score >= 3:
            return "Loyal"
        elif r_score <= 2 and f_score >= 3:
            return "At-Risk"
        else:
            return "Others"

    rfm["Segment"] = rfm.apply(segment_customer, axis=1)

    # Save RFM table
    os.makedirs("reports", exist_ok=True)
    rfm.to_csv("reports/rfm_analysis.csv", index=False)

    print("✅ RFM Analysis completed")
    return rfm

# -------------------- Cohort Analysis --------------------
def cohort_analysis(df):
    # Ensure order_date is datetime
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["order_month"] = df["order_date"].dt.to_period("M")

    # Assign cohort = customer first order month
    df["cohort_month"] = df.groupby("customer_id")["order_date"].transform("min").dt.to_period("M")

    # Cohort table: number of unique customers per cohort per month
    cohort_data = df.groupby(["cohort_month", "order_month"])["customer_id"].nunique().reset_index()

    cohort_counts = cohort_data.pivot(index="cohort_month", columns="order_month", values="customer_id")

    # Retention rate
    cohort_size = cohort_counts.iloc[:,0]
    retention = cohort_counts.divide(cohort_size, axis=0)

    # Save CSV
    retention.to_csv("reports/cohort_retention.csv")

    # Plot heatmap
    plt.figure(figsize=(12,6))
    sns.heatmap(retention, annot=True, fmt=".0%", cmap="YlGnBu")
    plt.title("Cohort Retention Rate")
    plt.ylabel("Cohort Month")
    plt.xlabel("Order Month")
    plt.tight_layout()
    plt.savefig("reports/cohort_retention.png")
    plt.close()

    print("✅ Cohort Analysis completed")
    return retention

# -------------------- RUN ANALYSIS --------------------
if __name__ == "__main__":
    df = load_sales_data()

    # RFM
    rfm = calculate_rfm(df)

    # Cohort
    retention = cohort_analysis(df)

    print("\n🎯 RFM + Cohort Analysis executed successfully")
