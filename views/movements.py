
import pandas as pd
import streamlit as st

from decimal import Decimal

from services.products_api import (
    get_products_from_api,
    ProductAPIError
)

from services.inventory_api import (
    get_warehouses_from_api,
    InventoryAPIError
)

from services.movements_api import (
    register_movement_from_api,
    get_movements_from_api,
    MovementAPIError
)


# ==========================================
# PAGE HEADER
# ==========================================

st.title("🔄 Stock Movements")
st.caption("Register stock entries and exits.")


# ==========================================
# LOAD PRODUCTS AND WAREHOUSES VIA HTTP
# ==========================================

try:
    products = [
        p for p in get_products_from_api()
        if p["is_active"]
    ]

    warehouses = [
        w for w in get_warehouses_from_api()
        if w["is_active"]
    ]

except (ProductAPIError, InventoryAPIError) as error:
    st.error(
        f"Unable to load products or warehouses: {error}"
    )
    st.stop()


# ==========================================
# SUCCESS MESSAGE
# ==========================================

if "movement_message" in st.session_state:
    st.success(
        st.session_state.pop("movement_message")
    )


# ==========================================
# NEW MOVEMENT FORM
# ==========================================

st.subheader("Register New Movement")

if not products or not warehouses:
    st.warning(
        "Active products and warehouses are required."
    )

else:
    product_options = {
        p["product_id"]: p
        for p in products
    }

    warehouse_options = {
        w["warehouse_id"]: w
        for w in warehouses
    }

    with st.form("new_movement_form"):

        movement_type = st.radio(
            "Movement Type",
            options=["IN", "OUT"],
            format_func=lambda value: (
                "📥 Stock Entry"
                if value == "IN"
                else "📤 Stock Exit"
            ),
            horizontal=True
        )

        selected_product = st.selectbox(
            "Product",
            options=list(product_options.keys()),
            format_func=lambda product_id: (
                f"{product_options[product_id]['sku']} - "
                f"{product_options[product_id]['name']}"
            )
        )

        selected_warehouse = st.selectbox(
            "Warehouse",
            options=list(warehouse_options.keys()),
            format_func=lambda warehouse_id: (
                warehouse_options[warehouse_id]["name"]
            )
        )

        quantity = st.number_input(
            "Quantity",
            min_value=0.01,
            value=1.0,
            step=0.01,
            format="%.2f"
        )

        notes = st.text_area(
            "Notes",
            max_chars=500,
            placeholder="Reason for this movement"
        )

        submitted = st.form_submit_button(
            "Register Movement",
            type="primary"
        )

    if submitted:

        try:
            result = register_movement_from_api(
                product_id=selected_product,
                warehouse_id=selected_warehouse,
                movement_type=movement_type,
                quantity=Decimal(str(quantity)),
                notes=notes.strip()
            )

            movement_id = result["movement_id"]

            st.session_state["movement_message"] = (
                f"Movement #{movement_id} "
                f"registered successfully!"
            )

            st.rerun()

        except MovementAPIError as error:
            st.warning(str(error))


# ==========================================
# MOVEMENT HISTORY
# ==========================================

st.divider()
st.subheader("Movement History")

try:
    movements = get_movements_from_api()

    if movements:

        df = pd.DataFrame(movements)

        st.dataframe(
            df,
            hide_index=True,
            width="stretch"
        )

        st.caption(
            f"Showing {len(movements)} movements."
        )

    else:
        st.info("No stock movements registered yet.")

except MovementAPIError as error:
    st.error(
        f"Unable to load movement history: {error}"
    )
