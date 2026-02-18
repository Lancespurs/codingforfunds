# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Notebook 02 — Ingest Raw Data (Bronze Layer)
# MAGIC
# MAGIC **What this notebook does:**
# MAGIC - Generates synthetic retail sales data using Python (no file upload needed)
# MAGIC - Registers the data as a **temporary view** so SQL can access it
# MAGIC - Uses SQL to save it as a **Bronze Delta table** in the catalog — raw and unmodified
# MAGIC
# MAGIC **Prerequisite:** Run Notebook 01 first.

# COMMAND ----------

# MAGIC %md
# MAGIC ## What is the Bronze Layer?
# MAGIC
# MAGIC The **Bronze layer** stores data **exactly as it arrives** — no changes, no fixes.
# MAGIC This is your safety net: if anything goes wrong downstream, you can always
# MAGIC come back to the original raw data.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Set the Default Catalog & Schema

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG sales_catalog;
# MAGIC USE SCHEMA  retail;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Generate Sample Sales Data
# MAGIC
# MAGIC We use Python's built-in `random` library to create 1,000 realistic-looking
# MAGIC sales orders. In a real project this data would come from a CSV file,
# MAGIC a database, or an API.
# MAGIC
# MAGIC Python is used here only because data generation needs programming logic
# MAGIC (loops, random values). Everything after this step is SQL.

# COMMAND ----------

import random
from datetime import date, timedelta
from pyspark.sql import Row

# Seed the random generator so results are reproducible every run
random.seed(42)

# --- Reference data ---
PRODUCTS = [
    ("Laptop",        "Electronics",  899.99),
    ("Smartphone",    "Electronics",  599.99),
    ("Headphones",    "Electronics",   79.99),
    ("Office Chair",  "Furniture",    249.99),
    ("Standing Desk", "Furniture",    449.99),
    ("Notebook",      "Stationery",     4.99),
    ("Pen Set",       "Stationery",     9.99),
    ("Coffee Maker",  "Appliances",    49.99),
    ("Blender",       "Appliances",    39.99),
    ("Backpack",      "Accessories",   59.99),
]

REGIONS  = ["North", "South", "East", "West"]
# Completed appears 3× so it is more likely — mirrors real-world data distributions
STATUSES = ["Completed", "Completed", "Completed", "Returned", "Pending"]

START_DATE = date(2024, 1, 1)

# --- Build 1,000 raw order rows ---
raw_rows = []
for order_id in range(1, 1001):
    product_name, category, unit_price = random.choice(PRODUCTS)
    quantity     = random.randint(1, 10)
    discount_pct = random.choice([0, 0, 0, 5, 10, 15, 20])  # mostly no discount
    region       = random.choice(REGIONS)
    status       = random.choice(STATUSES)
    order_date   = str(START_DATE + timedelta(days=random.randint(0, 364)))
    customer_id  = f"CUST-{random.randint(1, 200):04d}"

    raw_rows.append(Row(
        order_id     = order_id,
        customer_id  = customer_id,
        product      = product_name,
        category     = category,
        region       = region,
        quantity     = quantity,
        unit_price   = unit_price,
        discount_pct = discount_pct,
        order_date   = order_date,  # stored as STRING on purpose — this is raw data
        status       = status,
    ))

print(f"Generated {len(raw_rows):,} raw order rows.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Register as a Temporary View
# MAGIC
# MAGIC A **temporary view** is a named, in-memory table that only exists for this
# MAGIC Databricks session. It lets us hand data from Python over to SQL without
# MAGIC having to save it anywhere first.

# COMMAND ----------

# Create a Spark DataFrame from the Python list and expose it as a SQL view
df_raw = spark.createDataFrame(raw_rows)
df_raw.createOrReplaceTempView("raw_orders_temp")

print("Temporary view 'raw_orders_temp' is ready for SQL.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Preview the Raw Data with SQL

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Have a look at the first 10 rows before saving anything
# MAGIC SELECT *
# MAGIC FROM   raw_orders_temp
# MAGIC LIMIT  10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Check the Column Types
# MAGIC
# MAGIC Notice that `order_date` is a **string** here — we stored it that way
# MAGIC intentionally to reflect how raw data often arrives (no guarantees on types).
# MAGIC We will fix that in Notebook 03.

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE raw_orders_temp;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Save as a Bronze Delta Table
# MAGIC
# MAGIC `CREATE OR REPLACE TABLE ... AS SELECT` (also called **CTAS**) creates a
# MAGIC Delta table from the result of a query in one step.
# MAGIC
# MAGIC We select every column exactly as-is — no transformations, no fixes.
# MAGIC That is the whole point of the Bronze layer.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE sales_catalog.retail.bronze_orders
# MAGIC USING DELTA
# MAGIC COMMENT 'Bronze layer — raw sales orders, loaded as-is'
# MAGIC AS
# MAGIC SELECT *
# MAGIC FROM   raw_orders_temp;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Verify the Table

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Check row count
# MAGIC SELECT COUNT(*) AS total_rows
# MAGIC FROM   sales_catalog.retail.bronze_orders;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Confirm table exists in the schema
# MAGIC SHOW TABLES IN sales_catalog.retail;

# COMMAND ----------

# MAGIC %md
# MAGIC ## All Done!
# MAGIC
# MAGIC Raw data is now in the **Bronze layer** as `bronze_orders`.
# MAGIC
# MAGIC **Next step:** Run **Notebook 03** to clean and enrich the data (Silver layer).

# COMMAND ----------
