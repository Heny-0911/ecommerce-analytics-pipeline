import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

# -------------------- KPI CALCULATION --------------------
def calculate_kpis():
    # Connect to DB
    conn = sqlite3.connect("database/ecommerce.db")
    df = pd.read_sql("SELECT * FROM fact_sales", conn)
    conn.close()

    # Create reports directory
    os.makedirs("reports", exist_ok=True)

    # -------------------- 1️⃣ Total Revenue --------------------
    total_revenue = df["revenue"].sum()
    print(f"Total Revenue: ${total_revenue:,.2f}")

    # -------------------- 2️⃣ Monthly Sales Trend --------------------
    monthly_sales = df.groupby("order_month")["revenue"].sum().reset_index()
    monthly_sales.to_csv("reports/monthly_sales.csv", index=False)

    # Plot Monthly Trend
    plt.figure(figsize=(10,5))
    plt.plot(monthly_sales["order_month"], monthly_sales["revenue"], marker='o')
    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("reports/monthly_sales_trend.png")
    plt.close()

    # -------------------- 3️⃣ Top Products --------------------
    top_products = df.groupby("product_name")["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
    top_products.to_csv("reports/top_products.csv", index=False)

    # -------------------- 4️⃣ Top Customers --------------------
    top_customers = df.groupby("customer_name")["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
    top_customers.to_csv("reports/top_customers.csv", index=False)

    # -------------------- 5️⃣ Repeat Customer Rate --------------------
    repeat_customers = df.groupby("customer_id")["order_id"].nunique()
    repeat_rate = (repeat_customers > 1).sum() / repeat_customers.count() * 100
    print(f"Repeat Customer Rate: {repeat_rate:.2f}%")

    # -------------------- 6️⃣ Customer Lifetime Value (CLV) --------------------
    clv = df.groupby("customer_id")["revenue"].sum().reset_index()
    clv = clv.merge(df[["customer_id", "customer_name"]].drop_duplicates(), on="customer_id")
    clv.to_csv("reports/customer_lifetime_value.csv", index=False)

    print("✅ KPI Reports Generated Successfully!")

# -------------------- RUN KPI --------------------
if __name__ == "__main__":
    calculate_kpis()
    print("\n🎯 FULL KPI ANALYTICS EXECUTED SUCCESSFULLY")
