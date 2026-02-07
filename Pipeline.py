import pandas as pd
import sqlite3
import os # Import the os module

# -------------------- EXTRACT --------------------
def extract_data():
    customers = pd.read_csv("data/raw/customers.csv")
    products = pd.read_csv("data/raw/products.csv")
    orders = pd.read_csv("data/raw/orders.csv")

    print("✅ Data extracted successfully")
    return customers, products, orders

# -------------------- TRANSFORM --------------------
def transform_data(customers, products, orders):
    # Convert date
    orders["order_date"] = pd.to_datetime(orders["order_date"])

    # Merge all tables
    df = orders.merge(customers, on="customer_id", how="left") \
               .merge(products, on="product_id", how="left")

    # Revenue column
    df["revenue"] = df["quantity"] * df["price"]

    # Monthly aggregation
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)

    print("✅ Data transformed successfully")
    return df

# -------------------- VALIDATE --------------------
def validate_data(df):
    assert df.isnull().sum().sum() == 0, "❌ NULL values found"
    assert df.duplicated().sum() == 0, "❌ Duplicate records found"
    assert (df["revenue"] >= 0).all(), "❌ Negative revenue found"
    print("✅ Data validation passed")

# -------------------- LOAD --------------------
def load_to_db(df):
    os.makedirs("database", exist_ok=True) # Ensure the database directory exists
    conn = sqlite3.connect("database/ecommerce.db")
    df.to_sql("fact_sales", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Data loaded into database successfully")

# -------------------- PIPELINE --------------------
def run_pipeline():
    customers, products, orders = extract_data()
    df = transform_data(customers, products, orders)
    validate_data(df)
    load_to_db(df)
    print("\n🎯 FULL PIPELINE EXECUTED SUCCESSFULLY")

# Run pipeline
if __name__ == "__main__":
    run_pipeline()
