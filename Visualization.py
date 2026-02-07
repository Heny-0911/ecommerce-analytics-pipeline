import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sqlite3

# Load data
conn = sqlite3.connect("database/ecommerce.db")
df = pd.read_sql("SELECT * FROM fact_sales", conn)
conn.close()

os.makedirs("reports", exist_ok=True)

# Top 10 Products
top_products = df.groupby("product_name")["revenue"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(x=top_products.values, y=top_products.index, palette="viridis")
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Product")
plt.tight_layout()
plt.savefig("reports/top_products_bar.png")
plt.close()

# Top 10 Customers
top_customers = df.groupby("customer_name")["revenue"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(x=top_customers.values, y=top_customers.index, palette="magma")
plt.title("Top 10 Customers by Revenue")
plt.xlabel("Revenue")
plt.ylabel("Customer")
plt.tight_layout()
plt.savefig("reports/top_customers_bar.png")
plt.close()
