import streamlit as st
import pandas as pd

from components.product_components import create_product_dialog, open_product_dialog
from services.notion_service import list_pages, get_page_name_by_id
from core.config import get_settings
from models import Product

# Main page configs
st.set_page_config(page_icon="💾", layout="wide")
st.title("Products")

st.divider()

# Layout
col1, col2 = st.columns(2)


col1.subheader("Quick Actions")

if col1.button(label="New Product", help="Create a new product", icon=":material/add:"):
    open_product_dialog()

if st.session_state.get("product_dialog_open", False):
    create_product_dialog()


# Metrics Cached Data
@st.cache_data
def load_data() -> dict:
    products = pd.concat(
        [Product.from_dict(p).to_dataframe() for p in list_pages("product")],
        ignore_index=True,
    )

    # Swap Category IDs for Names
    products["Category"] = products["Category"].apply(lambda c: get_page_name_by_id(c))

    return products

data = load_data()

# Products Count Metric
col2.metric(
    label="Products", 
    value=len(data), 
    border=True)

# Dataframe as Table
st.dataframe(
    data[
        [
            "ID",
            "Name",
            "Price",
            "Category",
            "Stock Qty",
            "Print Time",
            "Created Time",
            "Last Edited Time",
        ]
    ],
    column_config={
        "ID": st.column_config.TextColumn(),
        "Name": st.column_config.TextColumn(),
        "Price": st.column_config.NumberColumn(format=get_settings().ST_PRODUCT_PRICE_NUMBER_FORMAT),
        "Category": st.column_config.ListColumn(),
        "Stock Qty": st.column_config.NumberColumn(),
        "Print Time": st.column_config.NumberColumn(),
        "Created Time": st.column_config.DateColumn(format=get_settings().ST_PRODUCT_CREATED_TIME_FORMAT),
        "Last Edited Time": st.column_config.DateColumn(format=get_settings().ST_PRODUCT_LAST_EDITED_TIME_FORMAT),
    },
)
