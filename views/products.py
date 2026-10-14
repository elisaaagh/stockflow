
import streamlit as st

from decimal import Decimal
from psycopg.errors import UniqueViolation

from database.products import (
    get_all_products,
    create_product,
    update_product,
    change_product_status
)

from services.products_api import get_products_from_api


# ==========================================
# PAGE HEADER
# ==========================================

st.title("📦 Product Management")
st.caption("Manage your product catalog.")

# ==========================================
# LOAD PRODUCTS
# ==========================================


try:
    products = get_products_from_api()

except Exception:
    st.error(
        "Unable to load products from StockFlow API. "
        "Verify that FastAPI is running on port 8000."
    )
    st.stop()



# ==========================================
# FEEDBACK MESSAGES
# ==========================================

if "product_message" in st.session_state:
    st.success(st.session_state.pop("product_message"))


# ==========================================
# PRODUCT METRICS
# ==========================================

total_products = len(products)

active_products = sum(
    1 for p in products if p["is_active"]
)

inactive_products = total_products - active_products

col1, col2, col3 = st.columns(3)

col1.metric("Total Products", total_products)
col2.metric("Active Products", active_products)
col3.metric("Inactive Products", inactive_products)

st.divider()


# ==========================================
# PRODUCT CATALOG
# ==========================================

st.subheader("Product Catalog")

st.dataframe(
    products,
    hide_index=True,
    width="stretch"
)

st.divider()


# ==========================================
# MANAGEMENT TABS
# ==========================================

tab1, tab2, tab3 = st.tabs([
    "➕ Register Product",
    "✏️ Edit Product",
    "🔄 Product Status"
])

UNITS = ["Pieza", "Bulto", "M3", "KG", "TN"]


# ==========================================
# TAB 1 - REGISTER PRODUCT
# ==========================================

with tab1:

    st.subheader("Register New Product")

    with st.form("register_product_form"):

        sku = st.text_input("SKU", max_chars=30)

        name = st.text_input(
            "Product Name",
            max_chars=150
        )

        description = st.text_area("Description")

        unit = st.selectbox("Unit", UNITS)

        min_stock = st.number_input(
            "Minimum Stock",
            min_value=0.0,
            value=0.0
        )

        submitted = st.form_submit_button(
            "Save Product",
            type="primary"
        )

    if submitted:

        sku = sku.strip().upper()
        name = name.strip()

        if not sku or not name:
            st.warning("SKU and name are required.")

        else:
            try:
                product_id = create_product(
                    sku=sku,
                    name=name,
                    description=description.strip(),
                    unit=unit,
                    min_stock=Decimal(str(min_stock))
                )

                st.session_state["product_message"] = (
                    f"Product created! ID: {product_id}"
                )

                st.rerun()

            except UniqueViolation:
                st.error("This SKU already exists.")

            except Exception:
                st.error("Unable to save product.")


# ==========================================
# TAB 2 - EDIT PRODUCT
# ==========================================

with tab2:

    st.subheader("Edit Existing Product")

    if products:

        product_options = {
            p["product_id"]: p
            for p in products
        }

        selected_id = st.selectbox(
            "Select Product",
            options=list(product_options.keys()),
            format_func=lambda product_id: (
                f"{product_options[product_id]['sku']} - "
                f"{product_options[product_id]['name']}"
            ),
            key="edit_product"
        )

        selected = product_options[selected_id]

        with st.form(
            "edit_product_form",
            enter_to_submit=False
        ):

            new_name = st.text_input(
                "Product Name",
                value=selected["name"],
                max_chars=150
            )

            new_description = st.text_area(
                "Description",
                value=selected["description"] or ""
            )

            available_units = list(UNITS)

            if selected["unit"] not in available_units:
                available_units.append(selected["unit"])

            new_unit = st.selectbox(
                "Unit",
                available_units,
                index=available_units.index(selected["unit"])
            )

            new_min_stock = st.number_input(
                "Minimum Stock",
                min_value=0.0,
                value=float(selected["min_stock"])
            )

            update_submitted = st.form_submit_button(
                "Update Product",
                type="primary"
            )

        if update_submitted:

            if not new_name.strip():
                st.warning("Product name is required.")

            else:
                try:
                    updated = update_product(
                        product_id=selected_id,
                        name=new_name.strip(),
                        description=new_description.strip(),
                        unit=new_unit,
                        min_stock=Decimal(str(new_min_stock))
                    )

                    if updated:
                        st.session_state["product_message"] = (
                            "Product updated successfully!"
                        )
                        st.rerun()
                    else:
                        st.warning("Product not found.")

                except Exception:
                    st.error("Unable to update product.")

    else:
        st.info("No products available.")


# ==========================================
# TAB 3 - PRODUCT STATUS
# ==========================================

with tab3:

    st.subheader("Activate / Deactivate Product")

    if products:

        status_options = {
            p["product_id"]: p
            for p in products
        }

        status_id = st.selectbox(
            "Select Product",
            options=list(status_options.keys()),
            format_func=lambda product_id: (
                f"{status_options[product_id]['sku']} - "
                f"{status_options[product_id]['name']}"
            ),
            key="status_product"
        )

        status_product = status_options[status_id]
        current_status = status_product["is_active"]

        if current_status:
            st.success("Current Status: ACTIVE")
        else:
            st.warning("Current Status: INACTIVE")

        with st.form("product_status_form"):

            new_status = st.radio(
                "Product Status",
                options=[True, False],
                format_func=lambda value: (
                    "Active" if value else "Inactive"
                ),
                index=0 if current_status else 1
            )

            status_submitted = st.form_submit_button(
                "Save Status",
                type="primary"
            )

        if status_submitted:

            if new_status == current_status:
                st.info("No changes detected.")

            else:
                try:
                    updated = change_product_status(
                        status_id,
                        new_status
                    )

                    if updated:
                        st.session_state["product_message"] = (
                            "Product status updated!"
                        )
                        st.rerun()
                    else:
                        st.error("Product not found.")

                except Exception:
                    st.error("Unable to change product status.")

    else:
        st.info("No products available.")
