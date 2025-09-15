import streamlit as st
import pandas as pd

from components.product_components import (create_product_dialog, create_product_dialog_state,
                                           edit_product_dialog, edit_product_dialog_state,
                                           delete_product_dialog, delete_product_dialog_state)
from services.notion_service import list_pages, get_page_name_by_id
from core.config import get_settings
from models import Product

# --- Page configuration ---
st.set_page_config(page_icon="💾", layout="wide")
st.title("Customers")
st.divider()

# --- Layout: Quick Actions ---
col1, col2 = st.columns(2)

col1.subheader("Quick Actions")

with col1:
    with st.container(border=False):
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])

        with btn_col1:
            # Button to open create product dialog
            if st.button(label="New Product", help="Create a new product", icon=":material/add:"):
                create_product_dialog_state(True)

        with btn_col2:
            # Button to open edit product dialog
            if st.button(label="Edit Product", help="Edit an existing product", icon=":material/edit:"):
                edit_product_dialog_state(True)

        with btn_col3:
            # Button to open delete product dialog
            if st.button(label="Delete Product", help="Delete an existing product", icon=":material/delete:"):
                delete_product_dialog_state(True)

# Show create product dialog if state is active
if st.session_state.get("create_product_dialog_open", False):
    create_product_dialog()
if st.session_state.get("edit_product_dialog_open", False):
    edit_product_dialog()
if st.session_state.get("delete_product_dialog_open", False):
    delete_product_dialog()

# --- Function to load products ---
@st.cache_data
def load_products() -> pd.DataFrame:
    """
    Load products from Notion and convert category IDs to names.
    """
    products = pd.concat(
        [Product.from_dict(p).to_dataframe() for p in list_pages("product")],
        ignore_index=True,
    )
    # Replace category ID with the first category name
    products["Category"] = products["Category"].apply(lambda c: get_page_name_by_id(c[0]) if c else None)
    return products

data = load_products()


# --- Metrics ---
# Show total number of products
col2.metric(label="Products", value=len(data), border=True)


# --- Render DataFrame ---
columns_to_show = [
    "ID",
    "Name",
    "Price",
    "Category",
    "Stock Qty",
    "Print Time",
    "Created Time",
    "Last Edited Time",
]

# Display products in a dataframe with proper column configurations
st.dataframe(
    data[columns_to_show],
    hide_index=True,
    column_config={
        "ID": st.column_config.TextColumn(),
        "Name": st.column_config.TextColumn(),
        "Price": st.column_config.NumberColumn(format=get_settings().ST_PRODUCT_PRICE_NUMBER_FORMAT),
        "Category": st.column_config.TextColumn(),
        "Stock Qty": st.column_config.NumberColumn(),
        "Print Time": st.column_config.NumberColumn(),
        "Created Time": st.column_config.DateColumn(format=get_settings().ST_PRODUCT_CREATED_TIME_FORMAT),
        "Last Edited Time": st.column_config.DateColumn(format=get_settings().ST_PRODUCT_LAST_EDITED_TIME_FORMAT),
    },
)
