
import streamlit as st

from services.auth_api import (
    login_user,
    get_authenticated_user,
    AuthenticationError
)

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="StockFlow",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# SESSION MANAGEMENT
# ==========================================

def logout():
    """Clear the current login session."""
    st.session_state.pop("access_token", None)
    st.session_state.pop("current_user", None)


def show_login():
    """Display the login form."""

    st.title("📦 StockFlow")
    st.caption("Inventory Management System")

    st.divider()

    col_left, col_center, col_right = st.columns(
        [1, 1.5, 1]
    )

    with col_center:
        with st.container(border=True):
            st.subheader("🔐 Sign In")
            st.write(
                "Enter your credentials to access StockFlow."
            )

            with st.form("login_form"):
                username = st.text_input(
                    "Username",
                    autocomplete="username"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    autocomplete="current-password"
                )

                submitted = st.form_submit_button(
                    "Sign In",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                if not username.strip() or not password:
                    st.warning(
                        "Username and password are required."
                    )
                    return

                try:
                    result = login_user(
                        username=username.strip().lower(),
                        password=password
                    )

                    token = result["access_token"]
                    user = get_authenticated_user(token)

                    st.session_state["access_token"] = token
                    st.session_state["current_user"] = user

                    st.rerun()

                except AuthenticationError as error:
                    st.error(str(error))


# ==========================================
# VERIFY CURRENT SESSION
# ==========================================

token = st.session_state.get("access_token")


if token:
    try:
        current_user = get_authenticated_user(token)
        st.session_state["current_user"] = current_user

    except AuthenticationError as error:
        # An invalid token must not retain a local session.
        if "invalid or has expired" in str(error).lower():
            logout()
            st.warning(
                "Your session has expired. Please sign in again."
            )
        else:
            st.error(str(error))
            st.stop()


# ==========================================
# LOGIN GATE
# ==========================================

if not st.session_state.get("access_token"):
    show_login()
    st.stop()



# ==========================================
# NAVIGATION
# ==========================================

current_user = st.session_state["current_user"]
user_role = current_user["role"]

pages = {
    "General": [
        st.Page(
            "views/dashboard.py",
            title="Dashboard",
            icon="📊",
            default=True
        )
    ],
    "Management": [
        st.Page(
            "views/products.py",
            title="Products",
            icon="📦"
        ),
        st.Page(
            "views/inventory.py",
            title="Inventory",
            icon="🏬"
        ),
        st.Page(
            "views/movements.py",
            title="Movements",
            icon="🔄"
        )
    ],
    "Analytics": [
        st.Page(
            "views/reports.py",
            title="Reports",
            icon="📈"
        )
    ]
}

# Only administrators can access user management.
if user_role == "admin":
    pages["Administration"] = [
        st.Page(
            "views/users.py",
            title="Users Management",
            icon="👥"
        )
    ]

navigation = st.navigation(pages)



# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("📦 StockFlow")
st.sidebar.caption("Inventory Management System")
st.sidebar.divider()

user = st.session_state["current_user"]

st.sidebar.write(f"**User:** {user['username']}")
st.sidebar.write(f"**Role:** {user['role'].capitalize()}")

if st.sidebar.button(
    "🚪 Log Out",
    use_container_width=True
):
    logout()
    st.rerun()

st.sidebar.divider()
st.sidebar.caption("Version 2.0.0-dev")


# ==========================================
# RUN SELECTED PAGE
# ==========================================

navigation.run()
