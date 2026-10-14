
import pandas as pd
import streamlit as st

from services.dashboard_api import (
    get_dashboard_metrics_from_api,
    get_daily_activity_from_api,
    DashboardAPIError
)

from services.movements_api import (
    get_movements_from_api,
    MovementAPIError
)

from services.inventory_api import (
    get_low_stock_from_api,
    InventoryAPIError
)


# ==========================================
# PAGE HEADER
# ==========================================

st.title("📊 StockFlow Dashboard")
st.caption(
    "Inventory Management & Business Overview"
)


# ==========================================
# LOAD DATA FROM FASTAPI
# ==========================================

try:
    metrics = get_dashboard_metrics_from_api()
    activity = get_daily_activity_from_api()
    movements = get_movements_from_api()
    low_stock = get_low_stock_from_api()

except (
    DashboardAPIError,
    MovementAPIError,
    InventoryAPIError
) as error:
    st.error(
        f"Unable to load dashboard information: {error}"
    )
    st.stop()


# ==========================================
# KEY PERFORMANCE INDICATORS
# ==========================================

st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.metric(
            "Active Products",
            metrics["active_products"]
        )

with col2:
    with st.container(border=True):
        st.metric(
            "Warehouses",
            metrics["active_warehouses"]
        )

with col3:
    with st.container(border=True):
        st.metric(
            "Low Stock Alerts",
            metrics["low_stock_alerts"]
        )

with col4:
    with st.container(border=True):
        st.metric(
            "Total Movements",
            metrics["total_movements"]
        )


# ==========================================
# DAILY MOVEMENT ACTIVITY
# ==========================================

st.subheader("📈 Movement Activity")
st.caption("Number of stock entries and exits per day")

with st.container(border=True):

    if activity:

        df_activity = pd.DataFrame(activity)

        df_activity["movement_date"] = pd.to_datetime(
            df_activity["movement_date"]
        )

        df_activity = df_activity.set_index(
            "movement_date"
        )

        # Seven calendar days, including zero-activity days.
        days = pd.date_range(
            end=pd.Timestamp.today().normalize(),
            periods=7,
            freq="D"
        )

        df_activity = df_activity.reindex(
            days,
            fill_value=0
        )

        df_activity = df_activity.rename(
            columns={
                "entries": "Entries",
                "exits": "Exits"
            }
        )

        df_activity.index = df_activity.index.strftime(
            "%b %d"
        )

        st.bar_chart(
            df_activity[["Entries", "Exits"]],
            x_label="Date",
            y_label="Movements",
            width="stretch",
            height=300
        )

    else:
        st.info(
            "No inventory movements in the last 7 days."
        )


# ==========================================
# RECENT MOVEMENTS & STOCK ALERTS
# ==========================================

col_left, col_right = st.columns(
    2,
    gap="medium"
)


# ==========================================
# RECENT MOVEMENTS
# ==========================================

with col_left:

    with st.container(border=True):

        st.subheader("🕘 Recent Movements")

        if movements:

            df_movements = pd.DataFrame(
                movements[:5]
            )

            df_movements = df_movements[[
                "created_at",
                "sku",
                "movement_type",
                "quantity",
                "unit"
            ]].copy()

            df_movements["created_at"] = (
                pd.to_datetime(
                    df_movements["created_at"]
                ).dt.strftime("%Y-%m-%d %H:%M")
            )

            df_movements.columns = [
                "Date",
                "SKU",
                "Type",
                "Quantity",
                "Unit"
            ]

            st.dataframe(
                df_movements,
                hide_index=True,
                width="stretch"
            )

        else:
            st.info("No movements registered yet.")


# ==========================================
# LOW STOCK ALERTS
# ==========================================

with col_right:

    with st.container(border=True):

        st.subheader("⚠️ Low Stock Alerts")

        if low_stock:

            df_alerts = pd.DataFrame(low_stock)

            # JSON responses may contain decimal strings.
            df_alerts["quantity"] = pd.to_numeric(
                df_alerts["quantity"]
            )

            df_alerts["min_stock"] = pd.to_numeric(
                df_alerts["min_stock"]
            )

            df_alerts["missing_quantity"] = (
                df_alerts["min_stock"]
                - df_alerts["quantity"]
            )

            df_alerts = df_alerts.sort_values(
                by="missing_quantity",
                ascending=False
            )

            df_alerts = df_alerts[[
                "sku",
                "warehouse",
                "quantity",
                "missing_quantity"
            ]].head(5)

            df_alerts.columns = [
                "SKU",
                "Warehouse",
                "Stock",
                "Missing"
            ]

            st.dataframe(
                df_alerts,
                hide_index=True,
                width="stretch"
            )

            st.caption(
                f"{len(low_stock)} low stock alerts detected."
            )

        else:
            st.success(
                "All active products meet "
                "their minimum stock levels."
            )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "StockFlow | Inventory Management System | v2.0.0-dev"
)
