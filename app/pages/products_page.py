import streamlit as st
import pandas as pd

from services.notion_service import get_database_count, list_pages
from components.product_components import create_product_dialog, open_product_dialog
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
def load_data() -> dict:
    response = {"product_count": get_database_count("product")}

    return response


data = load_data()

# Products Count Metric
col2.metric("Products", data["product_count"], border=True)

# Dataframe as Table
products = pd.concat(
    [Product.from_dict(p).to_dataframe() for p in list_pages("product")],
    ignore_index=True,
)
st.dataframe(
    products[
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
        "Price": st.column_config.NumberColumn(),
        "Category": st.column_config.ListColumn(),
        "Stock Qty": st.column_config.NumberColumn(),
        "Print Time": st.column_config.NumberColumn(),
        "Created Time": st.column_config.DateColumn(),
        "Last Edited Time": st.column_config.DateColumn(),
    },
)
