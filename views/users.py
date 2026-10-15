
import streamlit as st
import pandas as pd

from services.users_api import (
    get_users_from_api,
    create_user_from_api,
    UserAPIError
)


# ==========================================
# ACCESS CONTROL
# ==========================================

current_user = st.session_state.get("current_user")
access_token = st.session_state.get("access_token")

if (
    not current_user
    or not access_token
    or current_user.get("role") != "admin"
):
    st.error("You do not have permission to access this page.")
    st.stop()


# ==========================================
# PAGE HEADER
# ==========================================

st.title("👥 Users Management")
st.caption("Manage StockFlow user accounts and access roles.")

st.divider()


# ==========================================
# USER LIST
# ==========================================

st.subheader("Registered Users")

try:
    users = get_users_from_api()

    if users:
        df = pd.DataFrame(users)

        display_columns = [
            "user_id",
            "username",
            "role",
            "is_active",
            "created_at"
        ]

        df = df[display_columns]

        df = df.rename(
            columns={
                "user_id": "ID",
                "username": "Username",
                "role": "Role",
                "is_active": "Active",
                "created_at": "Created At"
            }
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No users found.")

except UserAPIError as error:
    st.error(f"Unable to load users: {error}")
    st.stop()


# ==========================================
# CREATE USER
# ==========================================

st.divider()
st.subheader("Create New User")

with st.form("create_user_form", clear_on_submit=True):

    username = st.text_input(
        "Username",
        placeholder="e.g. warehouse_operator",
        max_chars=50
    )

    password = st.text_input(
        "Password",
        type="password",
        help="Minimum 12 characters."
    )

    role = st.selectbox(
        "Role",
        options=["viewer", "operator", "admin"],
        format_func=lambda value: value.capitalize()
    )

    submitted = st.form_submit_button(
        "Create User",
        type="primary",
        use_container_width=True
    )

if submitted:
    if not username.strip() or not password:
        st.warning("Username and password are required.")

    elif len(password) < 12:
        st.warning("Password must contain at least 12 characters.")

    else:
        try:
            result = create_user_from_api(
                username=username.strip(),
                password=password,
                role=role
            )

            st.success(
                f"User '{result['username']}' created successfully."
            )

            st.rerun()

        except UserAPIError as error:
            if error.status_code == 409:
                st.warning("This username already exists.")
            elif error.status_code == 422:
                st.error(
                    "Invalid user information. "
                    "Check the username and password."
                )
            elif error.status_code in (401, 403):
                st.error("Your session is invalid or lacks permission.")
            else:
                st.error(f"Unable to create user: {error}")
