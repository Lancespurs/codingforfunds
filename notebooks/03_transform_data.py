# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Notebook 03 — Transform Data (Silver Layer)
# MAGIC
# MAGIC **What this notebook does:**
# MAGIC - Reads the raw Bronze table using SQL
# MAGIC - Casts columns to the correct data types with `CAST`
# MAGIC - Filters out bad / incomplete records with `WHERE`
# MAGIC - Adds derived columns (`discounted_price`, `revenue`, `order_year`, `order_month`)
# MAGIC - Uses a **CTE** (Common Table Expression) to keep the SQL readable
# MAGIC - Saves the result as a **Silver Delta table**
# MAGIC
# MAGIC **Prerequisite:** Run Notebook 02 first.

# COMMAND ----------

# MAGIC %md
# MAGIC ## What is the Silver Layer?
# MAGIC
# MAGIC The **Silver layer** is where raw data gets cleaned and standardised.
# MAGIC Think of it as the "trustworthy" version of the data — still detailed,
# MAGIC but safe to use for analysis without worrying about bad values.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Set the Default Catalog & Schema

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG sales_catalog;
# MAGIC USE SCHEMA  retail;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Preview the Bronze Table

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM   bronze_orders
# MAGIC LIMIT  10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Count Rows Before Cleaning
# MAGIC
# MAGIC It is good practice to record how many rows exist before filtering,
# MAGIC so you know how much data was dropped.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS rows_before_cleaning
# MAGIC FROM   bronze_orders;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Build the Silver Table with SQL
# MAGIC
# MAGIC We use a **CTE** (WITH clause) to break the transformation into readable stages:
# MAGIC
# MAGIC | CTE | What it does |
# MAGIC |---|---|
# MAGIC | `typed` | Casts every column to its correct type, filters bad rows |
# MAGIC | `enriched` | Adds `discounted_price` |
# MAGIC | Final `SELECT` | Adds `revenue`, `order_year`, `order_month` |
# MAGIC
# MAGIC ### Key SQL concepts used here
# MAGIC - `CAST(col AS type)` — converts a column to a different data type
# MAGIC - `TO_DATE(col, 'format')` — converts a string to a date
# MAGIC - `BETWEEN x AND y` — checks that a value is within a range
# MAGIC - `IS NOT NULL` — filters out missing values
# MAGIC - `ROUND(expr, 2)` — rounds a number to 2 decimal places
# MAGIC - `YEAR()` / `MONTH()` — extract parts from a date

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE silver_orders
# MAGIC USING DELTA
# MAGIC COMMENT 'Silver layer — cleaned and enriched sales orders'
# MAGIC AS
# MAGIC
# MAGIC -- Stage 1: cast every column to the correct type and remove bad rows
# MAGIC WITH typed AS (
# MAGIC     SELECT
# MAGIC         order_id,
# MAGIC         customer_id,
# MAGIC         product,
# MAGIC         category,
# MAGIC         region,
# MAGIC         CAST(quantity     AS INT)    AS quantity,
# MAGIC         CAST(unit_price   AS DOUBLE) AS unit_price,
# MAGIC         CAST(discount_pct AS INT)    AS discount_pct,
# MAGIC         TO_DATE(order_date, 'yyyy-MM-dd') AS order_date,
# MAGIC         status
# MAGIC     FROM bronze_orders
# MAGIC     WHERE order_date   IS NOT NULL              -- must have a date
# MAGIC       AND CAST(quantity     AS INT)    > 0      -- quantity must be positive
# MAGIC       AND CAST(unit_price   AS DOUBLE) > 0      -- price must be positive
# MAGIC       AND CAST(discount_pct AS INT) BETWEEN 0 AND 100  -- discount 0–100%
# MAGIC       AND status IS NOT NULL                    -- status must exist
# MAGIC ),
# MAGIC
# MAGIC -- Stage 2: calculate the price after applying the discount
# MAGIC enriched AS (
# MAGIC     SELECT
# MAGIC         *,
# MAGIC         ROUND(unit_price * (1 - discount_pct / 100.0), 2) AS discounted_price
# MAGIC     FROM typed
# MAGIC )
# MAGIC
# MAGIC -- Final output: add revenue and convenient date-part columns
# MAGIC SELECT
# MAGIC     order_id,
# MAGIC     customer_id,
# MAGIC     product,
# MAGIC     category,
# MAGIC     region,
# MAGIC     quantity,
# MAGIC     unit_price,
# MAGIC     discount_pct,
# MAGIC     discounted_price,
# MAGIC     ROUND(quantity * discounted_price, 2) AS revenue,
# MAGIC     order_date,
# MAGIC     YEAR(order_date)  AS order_year,
# MAGIC     MONTH(order_date) AS order_month,
# MAGIC     status
# MAGIC FROM enriched;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Count Rows After Cleaning
# MAGIC
# MAGIC Compare this to the count before cleaning to see how many rows were dropped.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT COUNT(*) AS rows_after_cleaning
# MAGIC FROM   silver_orders;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 — Preview the Silver Data

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM   silver_orders
# MAGIC LIMIT  10;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7 — Verify Column Types

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE silver_orders;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 8 — Quick Data Quality Check
# MAGIC
# MAGIC A few summary queries to confirm the data looks sensible before moving on.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Total revenue across all cleaned orders
# MAGIC SELECT ROUND(SUM(revenue), 2) AS total_revenue
# MAGIC FROM   silver_orders;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Order count and revenue breakdown by status
# MAGIC SELECT
# MAGIC     status,
# MAGIC     COUNT(*)              AS order_count,
# MAGIC     ROUND(SUM(revenue), 2) AS total_revenue
# MAGIC FROM   silver_orders
# MAGIC GROUP BY status
# MAGIC ORDER BY order_count DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Order count by region
# MAGIC SELECT
# MAGIC     region,
# MAGIC     COUNT(*) AS order_count
# MAGIC FROM   silver_orders
# MAGIC GROUP BY region
# MAGIC ORDER BY order_count DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## All Done!
# MAGIC
# MAGIC Clean, enriched data is now in the **Silver layer** as `silver_orders`.
# MAGIC
# MAGIC **Next step:** Run **Notebook 04** to build aggregated Gold tables for reporting.

# COMMAND ----------
