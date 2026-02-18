# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # Notebook 01 — Catalog & Schema Setup
# MAGIC
# MAGIC **What this notebook does:**
# MAGIC - Creates a Unity Catalog **catalog** called `sales_catalog`
# MAGIC - Creates a **schema** (also called a database) called `retail` inside it
# MAGIC - Explains the Medallion Architecture we will follow
# MAGIC
# MAGIC **Run this notebook first before any other notebook.**

# COMMAND ----------

# MAGIC %md
# MAGIC ## The Medallion Architecture
# MAGIC
# MAGIC We organise data in three layers:
# MAGIC
# MAGIC | Layer | Name | Purpose |
# MAGIC |---|---|---|
# MAGIC | 1 | **Bronze** | Raw data loaded exactly as received |
# MAGIC | 2 | **Silver** | Cleaned, typed, and enriched data |
# MAGIC | 3 | **Gold** | Aggregated data ready for reports & dashboards |
# MAGIC
# MAGIC Each layer is stored as a **Delta table** inside Unity Catalog.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Create the Catalog
# MAGIC
# MAGIC A **catalog** is the top-level container in Unity Catalog.
# MAGIC Think of it like a filing cabinet — everything goes inside it.
# MAGIC
# MAGIC > **Note:** You need the `CREATE CATALOG` privilege to run this.
# MAGIC > If you get a permission error, ask your Databricks admin.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- IF NOT EXISTS means this will not fail if you run the notebook a second time
# MAGIC CREATE CATALOG IF NOT EXISTS sales_catalog
# MAGIC COMMENT 'Top-level catalog for the sales analytics project';

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Create the Schema
# MAGIC
# MAGIC A **schema** (or database) lives inside a catalog.
# MAGIC Think of it like a folder inside the filing cabinet.
# MAGIC All our tables (Bronze, Silver, Gold) will live in this schema.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS sales_catalog.retail
# MAGIC COMMENT 'Retail sales data — Bronze, Silver, and Gold tables';

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Set the Default Catalog & Schema
# MAGIC
# MAGIC Setting defaults means we can write `table_name` instead of
# MAGIC `sales_catalog.retail.table_name` in the rest of this notebook.

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG sales_catalog;
# MAGIC USE SCHEMA  retail;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Verify Setup
# MAGIC
# MAGIC Let's confirm the schema exists by listing everything inside the catalog.

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Show all schemas inside our catalog
# MAGIC SHOW SCHEMAS IN sales_catalog;

# COMMAND ----------

# MAGIC %md
# MAGIC ## All Done!
# MAGIC
# MAGIC Your catalog and schema are ready.
# MAGIC
# MAGIC **Next step:** Run **Notebook 02** to load raw sales data into the Bronze layer.

# COMMAND ----------
