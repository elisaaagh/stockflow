
import pandas as pd
import streamlit as st

from services.inventory_api import (
    get_warehouses_from_api,
    get_inventory_from_api,
    get_low_stock_from_api,
    InventoryAPIError
)


# ==========================================
# PAGE HEADER
# ==========================================

st.title("🏬 Inventory Management")
st.caption("Monitor stock availability across warehouses.")


# ==========================================
# LOAD DATA FROM FASTAPI
# ==========================================

try:
    inventory = get_inventory_from_api()
    warehouses = get_warehouses_from_api()
    low_stock = get_low_stock_from_api()

except InventoryAPIError as error:
    st.error(str(error))
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

warehouse_options = {
    w["warehouse_id"]: w["name"]
    for w in warehouses
}

selected_warehouse_id = st.selectbox(
    "Filter by Warehouse",
    options=[None] + list(warehouse_options.keys()),
    format_func=lambda warehouse_id: (
        "All Warehouses"
        if warehouse_id is None
        else warehouse_options[warehouse_id]
    )
)

search = st.text_input(
    "Search Product",
    placeholder="Search by SKU or product name"
)


# ==========================================
# FILTER DATA
# ==========================================

filtered_inventory = inventory.copy()

if selected_warehouse_id is not None:
    filtered_inventory = [
        item for item in filtered_inventory
        if item["warehouse_id"] == selected_warehouse_id
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

    alerts_df["quantity"] = pd.to_numeric(
        alerts_df["quantity"]
    )

    alerts_df["min_stock"] = pd.to_numeric(
        alerts_df["min_stock"]
    )

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
