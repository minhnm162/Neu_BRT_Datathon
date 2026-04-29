# Aggregated Tables Guide

This folder contains processed CSV files intended for business analysis, Power BI, EDA, and forecasting review. Raw competition files in `dataset/` are not modified.

## 1. `order_lines_enriched.csv`

**Purpose:** Main transaction-level table for revenue, product mix, customer, region, and channel analysis.

**Grain:** One row per order item line.

**Built from:**

- `order_items`
- `orders`
- `products`
- `customers`
- `geography`

**Important derived columns:**

- `line_revenue = quantity * unit_price`
- `line_revenue_after_discount`
- `line_cogs = quantity * cogs`
- `line_margin`

**Power BI use cases:**

- Revenue by region, category, segment, size, product, device, source.
- Margin analysis by category or customer segment.
- AOV and order-item mix.

**Note:** This file is large and should not be pushed to normal GitHub without Git LFS or splitting.

## 2. `returns_enriched.csv`

**Purpose:** Return and refund analysis with product and order context.

**Grain:** One row per return record.

**Built from:**

- `returns`
- `products`
- `orders`

**Useful fields:**

- `return_reason`
- `return_quantity`
- `refund_amount`
- `category`
- `segment`
- `size`
- `order_source`
- `device_type`

**Power BI use cases:**

- Return count and refund amount by category, segment, size.
- Top return reasons.
- Return pressure by product group or channel.

## 3. `inventory_monthly_enriched.csv`

**Purpose:** Monthly inventory and operations analysis.

**Grain:** One row per month, category, and segment.

**Built from:**

- `inventory`

**Useful fields:**

- `stock_on_hand`
- `units_received`
- `units_sold`
- `stockout_days`
- `avg_days_of_supply`
- `avg_fill_rate`
- `stockout_flag_share`
- `overstock_flag_share`
- `reorder_flag_share`
- `avg_sell_through_rate`

**Power BI use cases:**

- Stockout trend by category and segment.
- Overstock and slow-moving inventory analysis.
- Fill-rate and sell-through monitoring.

## 4. `daily_sales_features_final_grain.csv`

**Purpose:** Daily forecasting feature table and time-series analysis table.

**Grain:** One row per date.

**Built from:**

- `sales`
- `promotions`

**Feature groups:**

- Calendar features: `day_of_week`, `month`, `quarter`, `year`, `is_weekend`.
- Revenue and COGS lag features.
- Rolling mean and rolling standard deviation features.
- EWM features.
- Promotion calendar features.

**Power BI use cases:**

- Daily revenue and COGS trend.
- Seasonality analysis by weekday, month, quarter.
- Promotion calendar overlay.
- Forecasting feature review.

**Note:** For a clean dashboard, use only business-facing fields first, such as `Date`, `Revenue`, `COGS`, calendar fields, and promotion fields. Lag and rolling columns are mainly for modeling.

## 5. `daily_sales_reconciliation.csv`

**Purpose:** Audit check proving the daily sales target matches transaction-level revenue.

**Grain:** One row summary.

**Fields:**

- `checked_days`
- `matching_days`
- `all_days_match`
- `note`

**Current meaning:**

All 3,833 checked days match: `sales.Revenue` equals `sum(quantity * unit_price)` by `order_date`.

**Power BI use cases:**

Usually not needed for dashboard visuals. Use it as a data-quality evidence table in documentation.

## 6. `table_grain_map.csv`

**Purpose:** Metadata describing the grain and primary use of each processed table.

**Grain:** One row per processed CSV file.

**Fields:**

- `table`
- `grain`
- `primary_use`

**Power BI use cases:**

Usually not loaded into the dashboard model. Use it as a reference to avoid mixing incompatible grains.

## Recommended Power BI Loading Strategy

For business dashboards, start with:

- `order_lines_enriched.csv`
- `returns_enriched.csv`
- `inventory_monthly_enriched.csv`
- `daily_sales_features_final_grain.csv`

Keep these as separate fact-style tables unless you have a clear dimensional model. Avoid joining daily, monthly, return-record, and order-line grains directly without a date/product/category bridge, because that can duplicate metrics.

For documentation and audit only:

- `daily_sales_reconciliation.csv`
- `table_grain_map.csv`
