
import streamlit as st

from decimal import Decimal

from services.products_api import (
    get_products_from_api,
    create_product_from_api,
    update_product_from_api,
    change_product_status_from_api,
    ProductAPIError
)

# ==========================================
# USER PERMISSIONS
# ==========================================

current_user = st.session_state.get("current_user", {})
user_role = current_user.get("role")

can_manage_products = user_role == "admin"

# ==========================================
# PAGE HEADER
# ==========================================

st.title("📦 Product Management")
st.caption("Manage products through StockFlow REST API.")


# ==========================================
# LOAD PRODUCTS FROM FASTAPI
# ==========================================

try:
    products = get_products_from_api()

except ProductAPIError as error:
    st.error(str(error))
    st.stop()


# ==========================================
# FEEDBACK
# ==========================================

if "product_message" in st.session_state:
    st.success(
        st.session_state.pop("product_message")
    )


# ==========================================
# METRICS
# ==========================================

total = len(products)

active = sum(
    1 for product in products
    if product["is_active"]
)

inactive = total - active

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.metric("Total Products", total)

with col2:
    with st.container(border=True):
        st.metric("Active Products", active)

with col3:
    with st.container(border=True):
        st.metric("Inactive Products", inactive)

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
UNITS = ["Pieza", "Bulto", "M3", "KG", "TN"]

if can_manage_products:

    tab_create, tab_edit, tab_status = st.tabs([
        "➕ Register Product",
        "✏️ Edit Product",
        "🔄 Product Status"
    ])


    # ==========================================
    # CREATE PRODUCT
    # ==========================================

    with tab_create:

        st.subheader("Register New Product")

        with st.form("create_product_form"):

            sku = st.text_input(
                "SKU",
                max_chars=30
            )

            name = st.text_input(
                "Product Name",
                max_chars=150
            )

            description = st.text_area("Description")

            unit = st.selectbox("Unit", UNITS)

            min_stock = st.number_input(
                "Minimum Stock",
                min_value=0.0,
                value=0.0,
                format="%.2f"
            )

            submitted = st.form_submit_button(
                "Save Product",
                type="primary"
            )

        if submitted:

            if not sku.strip() or not name.strip():
                st.warning("SKU and name are required.")

            else:
                try:
                    created = create_product_from_api(
                        sku=sku.strip().upper(),
                        name=name.strip(),
                        description=description.strip(),
                        unit=unit,
                        min_stock=Decimal(str(min_stock))
                    )

                    st.session_state["product_message"] = (
                        f"Product {created['sku']} created successfully!"
                    )

                    st.rerun()

                except ProductAPIError as error:
                    st.error(str(error))


    # ==========================================
    # EDIT PRODUCT
    # ==========================================

    with tab_edit:

        st.subheader("Edit Existing Product")

        if products:

            product_options = {
                product["product_id"]: product
                for product in products
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

            available_units = UNITS.copy()

            if selected["unit"] not in available_units:
                available_units.append(selected["unit"])

            with st.form("edit_product_form"):

                new_name = st.text_input(
                    "Product Name",
                    value=selected["name"],
                    max_chars=150
                )

                new_description = st.text_area(
                    "Description",
                    value=selected["description"] or ""
                )

                new_unit = st.selectbox(
                    "Unit",
                    available_units,
                    index=available_units.index(
                        selected["unit"]
                    )
                )

                new_min_stock = st.number_input(
                    "Minimum Stock",
                    min_value=0.0,
                    value=float(selected["min_stock"]),
                    format="%.2f"
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
                        updated = update_product_from_api(
                            product_id=selected_id,
                            name=new_name.strip(),
                            description=new_description.strip(),
                            unit=new_unit,
                            min_stock=Decimal(str(new_min_stock))
                        )

                        st.session_state["product_message"] = (
                            f"Product {updated['sku']} updated successfully!"
                        )

                        st.rerun()

                    except ProductAPIError as error:
                        st.error(str(error))

        else:
            st.info("No products available.")


    # ==========================================
    # PRODUCT STATUS
    # ==========================================

    with tab_status:

        st.subheader("Activate / Deactivate Product")

        if products:

            status_options = {
                product["product_id"]: product
                for product in products
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

            selected_product = status_options[status_id]

            current_status = selected_product["is_active"]

            if current_status:
                st.success("Current Status: ACTIVE")
            else:
                st.warning("Current Status: INACTIVE")

            with st.form("status_form"):

                new_status = st.radio(
                    "Product Status",
                    options=[True, False],
                    index=0 if current_status else 1,
                    format_func=lambda value: (
                        "Active" if value else "Inactive"
                    )
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
                        updated = change_product_status_from_api(
                            product_id=status_id,
                            is_active=new_status
                        )

                        st.session_state["product_message"] = (
                            f"Product {updated['sku']} "
                            "status updated successfully!"
                        )

                        st.rerun()

                    except ProductAPIError as error:
                        st.error(str(error))

        else:
            st.info("No products available.")
else:
    st.info(
        "You have read-only access to the product catalog."
    )