# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Notebook 04 — Analyze & Report (Gold Layer)
# MAGIC
# MAGIC **What this notebook does:**
# MAGIC - Reads the clean Silver table using SQL
# MAGIC - Builds three aggregated **Gold tables** that answer real business questions:
# MAGIC   1. Which products sell the most?
# MAGIC   2. How does revenue break down by region?
# MAGIC   3. What does monthly revenue look like over the year?
# MAGIC - All transformations are written in SQL using `GROUP BY`, `SUM`, `COUNT`, etc.
# MAGIC
# MAGIC **Prerequisite:** Run Notebooks 01, 02, and 03 first.

# COMMAND ----------

# MAGIC %md
# MAGIC ## What is the Gold Layer?
# MAGIC
# MAGIC The **Gold layer** contains data that is pre-aggregated and ready to be
# MAGIC consumed by dashboards, reports, or business users.
# MAGIC Gold tables answer specific business questions — they are **small and fast**
# MAGIC compared to the Silver layer.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Set the Default Catalog & Schema

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG sales_catalog;
# MAGIC USE SCHEMA  retail;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Filter to Completed Orders Only
# MAGIC
# MAGIC Before building the Gold tables, let's confirm how many completed orders
# MAGIC we have. We only count `Completed` orders toward revenue — returned and
# MAGIC pending orders should not be included.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     status,
# MAGIC     COUNT(*) AS order_count
# MAGIC FROM   silver_orders
# MAGIC GROUP BY status
# MAGIC ORDER BY order_count DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table 1 — Top Products by Revenue
# MAGIC
# MAGIC **Business question:** Which products are generating the most money?
# MAGIC
# MAGIC ### Key SQL concepts used here
# MAGIC - `GROUP BY` — groups rows by one or more columns so we can aggregate
# MAGIC - `SUM()` — adds up all values in a group
# MAGIC - `COUNT(DISTINCT col)` — counts unique values (avoids double-counting)
# MAGIC - `AVG()` — calculates the average
# MAGIC - `ORDER BY ... DESC` — sorts from largest to smallest

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold_top_products
# MAGIC USING DELTA
# MAGIC COMMENT 'Gold layer — total revenue and units sold per product'
# MAGIC AS
# MAGIC SELECT
# MAGIC     product,
# MAGIC     category,
# MAGIC     ROUND(SUM(revenue), 2)          AS total_revenue,
# MAGIC     SUM(quantity)                    AS units_sold,
# MAGIC     COUNT(DISTINCT order_id)         AS order_count,
# MAGIC     ROUND(AVG(discounted_price), 2)  AS avg_selling_price
# MAGIC FROM   silver_orders
# MAGIC WHERE  status = 'Completed'
# MAGIC GROUP BY product, category
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Preview the result
# MAGIC SELECT *
# MAGIC FROM   gold_top_products;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table 2 — Revenue by Region
# MAGIC
# MAGIC **Business question:** Which regions are our strongest markets?

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold_sales_by_region
# MAGIC USING DELTA
# MAGIC COMMENT 'Gold layer — revenue and customer breakdown by sales region'
# MAGIC AS
# MAGIC SELECT
# MAGIC     region,
# MAGIC     ROUND(SUM(revenue), 2)          AS total_revenue,
# MAGIC     COUNT(DISTINCT order_id)         AS order_count,
# MAGIC     COUNT(DISTINCT customer_id)      AS unique_customers,
# MAGIC     ROUND(AVG(revenue), 2)           AS avg_order_value
# MAGIC FROM   silver_orders
# MAGIC WHERE  status = 'Completed'
# MAGIC GROUP BY region
# MAGIC ORDER BY total_revenue DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM   gold_sales_by_region;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Table 3 — Monthly Revenue Trend
# MAGIC
# MAGIC **Business question:** How is revenue trending month by month?
# MAGIC
# MAGIC This is the classic time-series view that almost every business needs.
# MAGIC
# MAGIC ### New SQL concepts used here
# MAGIC - `LPAD(expr, length, pad)` — pads a string on the left, e.g. `3` → `'03'`
# MAGIC - `CAST(col AS STRING)` — converts a number to text so we can concatenate it
# MAGIC - `CONCAT(a, b, c)` — joins strings together

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE gold_monthly_revenue
# MAGIC USING DELTA
# MAGIC COMMENT 'Gold layer — monthly revenue trend for 2024'
# MAGIC AS
# MAGIC SELECT
# MAGIC     order_year,
# MAGIC     order_month,
# MAGIC     -- Build a readable label like "2024-03" for charts
# MAGIC     CONCAT(
# MAGIC         CAST(order_year  AS STRING), '-',
# MAGIC         LPAD(CAST(order_month AS STRING), 2, '0')
# MAGIC     )                                        AS year_month,
# MAGIC     ROUND(SUM(revenue), 2)                   AS monthly_revenue,
# MAGIC     COUNT(DISTINCT order_id)                  AS order_count,
# MAGIC     COUNT(DISTINCT customer_id)               AS unique_customers
# MAGIC FROM   silver_orders
# MAGIC WHERE  status = 'Completed'
# MAGIC GROUP BY order_year, order_month
# MAGIC ORDER BY order_year, order_month;

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT *
# MAGIC FROM   gold_monthly_revenue;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Final Catalog Summary
# MAGIC
# MAGIC Let's confirm all five tables are present in our schema.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN sales_catalog.retail;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Cross-Table Summary Query
# MAGIC
# MAGIC A single query that pulls the key headline numbers across all Gold tables.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC     'Top product'         AS metric,
# MAGIC     product               AS value
# MAGIC FROM gold_top_products
# MAGIC ORDER BY total_revenue DESC
# MAGIC LIMIT 1
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC     'Top region'          AS metric,
# MAGIC     region                AS value
# MAGIC FROM gold_sales_by_region
# MAGIC ORDER BY total_revenue DESC
# MAGIC LIMIT 1
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC     'Best month'          AS metric,
# MAGIC     year_month            AS value
# MAGIC FROM gold_monthly_revenue
# MAGIC ORDER BY monthly_revenue DESC
# MAGIC LIMIT 1;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Congratulations!
# MAGIC
# MAGIC You have built a complete SQL-driven data pipeline in Databricks:
# MAGIC
# MAGIC ```
# MAGIC Raw Python data  (generated in Notebook 02)
# MAGIC        │
# MAGIC        ▼
# MAGIC  bronze_orders        ← CTAS from temp view
# MAGIC        │
# MAGIC        ▼  (CAST, WHERE, CTEs)
# MAGIC  silver_orders        ← CTAS with type fixing & derived columns
# MAGIC        │
# MAGIC        ├──► gold_top_products       ← GROUP BY product
# MAGIC        ├──► gold_sales_by_region    ← GROUP BY region
# MAGIC        └──► gold_monthly_revenue    ← GROUP BY year, month
# MAGIC ```
# MAGIC
# MAGIC **What to explore next:**
# MAGIC - Go to **Catalog** in the left sidebar and browse your tables
# MAGIC - Click on a table to see its schema, sample data, and lineage
# MAGIC - Try editing one of the SQL queries above to ask a different question
# MAGIC - Add a new Gold table for a business question you care about

# COMMAND ----------
