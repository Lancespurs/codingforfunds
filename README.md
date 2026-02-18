# Databricks Sales Analytics — Beginner's Guide

A beginner-friendly project that walks you through loading, transforming, and analysing **retail sales data** inside **Databricks** using **Unity Catalog**.

---

## What You Will Learn

- How Databricks notebooks work
- The **Medallion Architecture** (Bronze → Silver → Gold)
- How to create a **Unity Catalog** catalog and schema
- How to read, clean, and transform data with **PySpark**
- How to save results as **Delta tables** in the catalog
- How to run basic analytics and visualise results

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Databricks workspace | Free trial at [databricks.com](https://databricks.com) |
| Unity Catalog enabled | Ask your workspace admin if unsure |
| A running cluster | Runtime 13.3 LTS or higher recommended |
| No local setup needed | Everything runs inside Databricks |

---

## Repo Structure

```
codingforfunds/
├── README.md                    ← You are here
└── notebooks/
    ├── 01_setup_catalog.py      ← Step 1: Create catalog & schema
    ├── 02_ingest_raw_data.py    ← Step 2: Load raw data (Bronze)
    ├── 03_transform_data.py     ← Step 3: Clean & enrich data (Silver)
    └── 04_analyze_and_report.py ← Step 4: Aggregate & visualise (Gold)
```

---

## The Medallion Architecture

This project follows the industry-standard **Medallion Architecture** — a layered approach to organising data:

```
Raw Source Data
      │
      ▼
 [ BRONZE ]  ── Raw data, loaded as-is, nothing changed
      │
      ▼
 [ SILVER ]  ── Cleaned, typed, enriched data
      │
      ▼
 [  GOLD  ]  ── Aggregated, ready for reporting & dashboards
```

Each layer is stored as a **Delta table** in Unity Catalog.

---

## How to Use These Notebooks

### Step 1 — Import the notebooks into Databricks

1. Open your Databricks workspace
2. Click **Workspace** in the left sidebar
3. Click the **⋮** menu next to a folder → **Import**
4. Select each `.py` file from this repo and import it

### Step 2 — Attach a cluster

Open any notebook and select a running cluster from the top dropdown.

### Step 3 — Run in order

Run the notebooks **in order** (01 → 02 → 03 → 04). Each notebook builds on the previous one.

> **Tip:** Use **Run All** (top toolbar) to execute every cell in a notebook at once.

### Step 4 — Explore the catalog

After running all notebooks, go to **Catalog** in the left sidebar to see your tables under:

```
sales_catalog
└── retail
    ├── bronze_orders       ← raw data
    ├── silver_orders       ← cleaned data
    ├── gold_top_products   ← top-selling products
    ├── gold_sales_by_region
    └── gold_monthly_revenue
```

---

## Sample Data

The notebooks generate **synthetic retail sales data** so you do not need any external files. The data includes:

- `order_id` — unique order identifier
- `customer_id` — customer identifier
- `product` — product name
- `category` — product category
- `region` — sales region (North, South, East, West)
- `quantity` — units ordered
- `unit_price` — price per unit
- `discount_pct` — discount percentage applied
- `order_date` — date of order
- `status` — order status (Completed, Returned, Pending)

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `CatalogNotFoundException` | Make sure Unity Catalog is enabled in your workspace |
| `AnalysisException: Table not found` | Run notebooks in order starting from 01 |
| Cluster not attached | Select a cluster from the dropdown at the top of the notebook |
| Permission denied on catalog | Ask your Databricks admin to grant you `CREATE CATALOG` privilege |

---

## Next Steps After Completing This Project

- Connect a real data source (CSV upload, cloud storage, API)
- Schedule notebooks to run automatically using **Databricks Workflows**
- Build a **dashboard** on top of the Gold tables
- Explore **Databricks SQL** for querying with plain SQL
- Learn about **Auto Loader** for streaming ingestion
