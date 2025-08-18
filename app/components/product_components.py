import time

import streamlit as st

from services.notion_service import list_pages
from services.category_service import create_category_on_notion
from services.product_service import create_product_on_notion
from models import Product, Category


def open_product_dialog():
    st.session_state["product_dialog_open"] = True


@st.dialog(
    title="Create New Product",
    width="large",
    on_dismiss="ignore"
)
def create_product_dialog() -> None:
    """New product dialog"""

    try:
        categories = [Category.from_dict(c) for c in list_pages("category", page_size=100)]
        category_options = [c.name for c in categories]
    except Exception as e:
        st.error(f"Error fetching categories: {e}")
        category_options = []

    st.subheader("Required Inputs")
    name = st.text_input("Name")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    category = st.selectbox(
        label="Category",
        options=category_options,
        accept_new_options=True,
        placeholder="Select a category"
    )

    st.subheader("Optional Inputs")
    print_time = st.number_input("Print Time", min_value=0.0, format="%.2f")

    if st.button("Create Product", type="primary", use_container_width=True):
        # Create category if not exists
        if category not in category_options:
            category_id = create_category_on_notion(Category(name=category)).get("id")
        else:
            category_id = next(c.notion_id for c in categories if c.name == category)

        new_product = Product(
            name=name,
            price=price,
            print_time=print_time if print_time else 0,
            category=[category_id]
        )

        with st.spinner("Creating product..."):
            create_product_on_notion(new_product)
            time.sleep(1)
    
        st.session_state["product_dialog_open"] = False
        st.rerun()
