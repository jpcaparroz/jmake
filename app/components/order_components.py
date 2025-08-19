import time
from datetime import datetime

import streamlit as st
import pandas as pd

from core.config import get_settings
from services.notion_service import list_pages
from services.order_service import create_order_on_notion
from models import Order, Product, Customer, Store


def open_order_dialog():
    st.session_state["order_dialog_open"] = True


@st.dialog(
    title="Create New Order",
    width="large",
    on_dismiss="ignore"
)
def create_order_dialog() -> None:
    """New order dialog"""

    try:
        products = [Product.from_dict(p) for p in list_pages("product", page_size=100)]
        product_options = [p.name for p in products]
        product_map = {p.name: p for p in products}  # 🔑 mapa nome -> Product
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        product_options = []
        product_map = {}

    try:
        customers = [Customer.from_dict(c) for c in list_pages("customer", page_size=100)]
        customer_options = [c.name for c in customers]
    except Exception as e:
        st.error(f"Error fetching customers: {e}")
        customer_options = []

    try:
        stores = [Store.from_dict(c) for c in list_pages("store", page_size=100)]
        store_options = [c.name for c in stores]
    except Exception as e:
        st.error(f"Error fetching stores: {e}")
        store_options = []

    # --- Campos principais ---
    st.subheader("Required Inputs")
    date = st.date_input("Order Date", value="today")
    order_customer = st.selectbox("Customer", options=customer_options)
    order_store = st.selectbox("Store", options=store_options)

    # --- Editor de produtos ---
    product_init_df = pd.DataFrame([
        {"Product": None, "Quantity": 1, "Suggested Price": 0.0, "Total": 0.0}
    ])

    edited = st.data_editor(
        product_init_df,
        num_rows="dynamic",
        column_config={
            "Product": st.column_config.SelectboxColumn("Product", options=product_options, required=True),
            "Quantity": st.column_config.NumberColumn("Quantity", min_value=1, step=1),
            "Suggested Price": st.column_config.NumberColumn("Suggested Price", disabled=True),
            "Total": st.column_config.NumberColumn("Total", disabled=True)
        },
        key="order_editor"
    )

    # --- Recalcular preços e totais ---
    for i, row in edited.iterrows():
        product_name = row["Product"]
        if product_name in product_map:  # agora compara com o dict
            product_price = product_map[product_name].price or 0.0
            edited.at[i, "Suggested Price"] = product_price
            edited.at[i, "Total"] = product_price * row["Quantity"]

    # --- Mostrar resultado atualizado ---
    st.write("📦 Order Items")
    st.dataframe(edited)

    st.metric("Total Order", edited["Total"].sum())



    st.subheader("Optional Inputs")
    description = st.text_area("Description", height=100)

    # if st.button("Create Order", type="primary", use_container_width=True):
    #     # Create category if not exists
    #     # if category not in category_options:
    #     #     category_id = create_category_on_notion(Category(name=category)).get("id")
    #     # else:
    #     #     category_id = next(c.notion_id for c in categories if c.name == category)

    #     new_order = Order(
    #         name=f"Order {datetime.now().strftime(get_settings().DEFAULT_DATE_FORMAT)}",
    #         order_date=date,
    #         store_id=order_store,
    #         customer_id=order_customer,
    #         total_value=0.0
    #     )

    #     with st.spinner("Creating order..."):
    #         create_order_on_notion(new_order)
    #         time.sleep(1)
    
    #     st.session_state["order_dialog_open"] = False
        # st.rerun()
