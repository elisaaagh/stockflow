
import pandas as pd
import streamlit as st

from database.inventory import (
    get_warehouses,
    get_inventory,
    get_low_stock
)


# ==========================================
# PAGE HEADER
# ==========================================

st.title("🏬 Inventory Management")
st.caption("Monitor stock availability across warehouses.")


# ==========================================
# LOAD DATA
# ==========================================

try:
    inventory = get_inventory()
    warehouses = get_warehouses()
    low_stock = get_low_stock()

except Exception:
    st.error("Unable to load inventory data.")
    st.stop()


# ==========================================
# DASHBOARD METRICS
# ==========================================

total_products = len(set(
    item["product_id"] for item in inventory
))

total_warehouses = len(warehouses)
low_stock_count = len(low_stock)

col1, col2, col3 = st.columns(3)

col1.metric("Total Products", total_products)
col2.metric("Warehouses", total_warehouses)
col3.metric("Low Stock Alerts", low_stock_count)

st.divider()


# ==========================================
# INVENTORY FILTERS
# ==========================================

st.subheader("Warehouse Inventory")

warehouse_names = [w["name"] for w in warehouses]

selected_warehouse = st.selectbox(
    "Filter by Warehouse",
    ["All Warehouses"] + warehouse_names
)

search = st.text_input(
    "Search Product",
    placeholder="Search by SKU or product name"
)


# ==========================================
# FILTER DATA
# ==========================================

filtered_inventory = inventory.copy()

if selected_warehouse != "All Warehouses":
    filtered_inventory = [
        item for item in filtered_inventory
        if item["warehouse"] == selected_warehouse
    ]

if search.strip():
    query = search.strip().lower()

    filtered_inventory = [
        item for item in filtered_inventory
        if query in item["sku"].lower()
        or query in item["product"].lower()
    ]


# ==========================================
# INVENTORY TABLE
# ==========================================

if filtered_inventory:

    df = pd.DataFrame(filtered_inventory)

    df = df[[
        "sku",
        "product",
        "warehouse",
        "unit",
        "quantity",
        "min_stock",
        "stock_status",
        "is_active"
    ]]

    st.dataframe(
        df,
        hide_index=True,
        width="stretch"
    )

    st.caption(
        f"Showing {len(filtered_inventory)} inventory records."
    )

else:
    st.info("No inventory records match your filters.")


# ==========================================
# LOW STOCK ALERTS
# ==========================================

st.divider()
st.subheader("⚠️ Low Stock Alerts")

if low_stock:

    alerts_df = pd.DataFrame(low_stock)

    alerts_df["missing_quantity"] = (
        alerts_df["min_stock"] - alerts_df["quantity"]
    )

    alerts_df = alerts_df[[
        "sku",
        "product",
        "warehouse",
        "quantity",
        "min_stock",
        "missing_quantity"
    ]]

    st.dataframe(
        alerts_df,
        hide_index=True,
        width="stretch"
    )

else:
    st.success("No low stock alerts.")
