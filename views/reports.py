
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from database.products import get_all_products
from database.inventory import get_warehouses
from database.reports import get_movement_report


# ==========================================
# PAGE HEADER
# ==========================================

st.title("📈 Reports & Analytics")
st.caption("Analyze inventory movements and export reports.")

# ==========================================
# LOAD FILTER OPTIONS
# ==========================================

try:
    products = get_all_products()
    warehouses = get_warehouses()

except Exception:
    st.error("Unable to load report filters.")
    st.stop()


product_options = {
    p["product_id"]: f"{p['sku']} - {p['name']}"
    for p in products
}

warehouse_options = {
    w["warehouse_id"]: w["name"]
    for w in warehouses
}


# ==========================================
# REPORT FILTERS
# ==========================================

st.subheader("Report Filters")

today = date.today()

col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=today - timedelta(days=30)
    )

with col2:
    end_date = st.date_input(
        "End Date",
        value=today
    )

col3, col4, col5 = st.columns(3)

with col3:
    warehouse_id = st.selectbox(
        "Warehouse",
        options=[None] + list(warehouse_options.keys()),
        format_func=lambda value: (
            "All Warehouses"
            if value is None
            else warehouse_options[value]
        )
    )

with col4:
    product_id = st.selectbox(
        "Product",
        options=[None] + list(product_options.keys()),
        format_func=lambda value: (
            "All Products"
            if value is None
            else product_options[value]
        )
    )

with col5:
    movement_type = st.selectbox(
        "Movement Type",
        options=[None, "IN", "OUT"],
        format_func=lambda value: {
            None: "All Movements",
            "IN": "Stock Entries",
            "OUT": "Stock Exits"
        }[value]
    )


# ==========================================
# VALIDATE DATE RANGE
# ==========================================

if start_date > end_date:
    st.warning("Start Date must be before End Date.")
    st.stop()


# ==========================================
# LOAD REPORT
# ==========================================

try:
    movements = get_movement_report(
        start_date=start_date,
        end_date=end_date,
        warehouse_id=warehouse_id,
        product_id=product_id,
        movement_type=movement_type
    )

except Exception:
    st.error("Unable to generate movement report.")
    st.stop()


# ==========================================
# REPORT METRICS
# ==========================================

total_movements = len(movements)

entries = sum(
    1 for m in movements
    if m["movement_type"] == "IN"
)

exits = sum(
    1 for m in movements
    if m["movement_type"] == "OUT"
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Movements", total_movements)
col2.metric("Stock Entries", entries)
col3.metric("Stock Exits", exits)

st.divider()


# ==========================================
# REPORT RESULTS
# ==========================================

st.subheader("Movement Report")

if movements:

    df = pd.DataFrame(movements)

    st.dataframe(
        df,
        hide_index=True,
        width="stretch"
    )

    # ======================================
    # DAILY ACTIVITY CHART
    # ======================================

    st.subheader("Daily Movement Activity")

    chart_df = df.copy()

    chart_df["movement_date"] = pd.to_datetime(
        chart_df["created_at"]
    ).dt.date

    chart_df = (
        chart_df.groupby(
            ["movement_date", "movement_type"]
        )
        .size()
        .unstack(fill_value=0)
    )

    chart_df = chart_df.reindex(
        columns=["IN", "OUT"],
        fill_value=0
    )

    chart_df = chart_df.rename(
        columns={
            "IN": "Entries",
            "OUT": "Exits"
        }
    )

    st.bar_chart(chart_df)

    # ======================================
    # CSV EXPORT
    # ======================================

    st.divider()

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="📥 Download CSV Report",
        data=csv_data,
        file_name=(
            f"stockflow_report_"
            f"{start_date}_{end_date}.csv"
        ),
        mime="text/csv",
        type="primary"
    )

else:
    st.info("No movements found for the selected filters.")
