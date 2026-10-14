
import streamlit as st

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
# NAVIGATION
# ==========================================

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

navigation = st.navigation(pages)

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("📦 StockFlow")
st.sidebar.caption("Inventory Management System")
st.sidebar.divider()

st.sidebar.caption("Version 0.1.0")

# ==========================================
# RUN SELECTED PAGE
# ==========================================

navigation.run()
