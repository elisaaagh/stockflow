
import pandas as pd
import streamlit as st

from database.dashboard import (
    get_dashboard_metrics,
    get_daily_activity
)

from database.movements import get_movements


# ==========================================
# HEADER
# ==========================================

st.title("📊 StockFlow Dashboard")
st.caption("Inventory Management & Business Overview")

# ==========================================
# LOAD DATA
# ==========================================

try:
    metrics = get_dashboard_metrics()
    activity = get_daily_activity()
    movements = get_movements()

except Exception:
    st.error("Unable to load dashboard data.")
    st.stop()


# ==========================================
# KEY PERFORMANCE INDICATORS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Active Products",
    metrics["active_products"]
)

col2.metric(
    "Warehouses",
    metrics["active_warehouses"]
)

col3.metric(
    "Low Stock Alerts",
    metrics["low_stock_alerts"]
)

col4.metric(
    "Total Movements",
    metrics["total_movements"]
)

st.divider()


# ==========================================
# MOVEMENT ACTIVITY
# ==========================================

st.subheader("📈 Movement Activity")
st.caption("Number of entries and exits by day")

if activity:

    df_activity = pd.DataFrame(activity)

    df_activity["movement_date"] = pd.to_datetime(
        df_activity["movement_date"]
    )

    df_activity = df_activity.set_index(
        "movement_date"
    )

    # Include days with no movements.
    days = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=7
    )

    df_activity = df_activity.reindex(
        days,
        fill_value=0
    )

    st.bar_chart(
        df_activity[["entries", "exits"]]
    )

else:
    st.info("No movements in the last 7 days.")


# ==========================================
# RECENT MOVEMENTS
# ==========================================

st.divider()
st.subheader("🕘 Recent Movements")

if movements:

    df_movements = pd.DataFrame(
        movements[:10]
    )

    st.dataframe(
        df_movements,
        hide_index=True,
        width="stretch"
    )

else:
    st.info("No movements registered yet.")


# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption("StockFlow | Inventory Management System")
