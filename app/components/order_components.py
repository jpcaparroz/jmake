import streamlit as st
import pandas as pd

from core.config import get_settings
from services.notion_service import list_pages
from models import Product, Customer, Store


def create_order_dialog_state(state: bool) -> None:
    st.session_state["create_order_dialog_open"] = state


@st.dialog(
    title="Create New Order",
    width="large",
    on_dismiss="ignore"
)
def create_order_dialog() -> None:
    """New order dialog"""

    # --- Fetch products ---
    try:
        products = [Product.from_dict(p) for p in list_pages("product", page_size=100)]
        product_options = [p.name for p in products]
        product_map = {p.name: p for p in products}  # 🔑 nome -> Product
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        product_options = []
        product_map = {}

    # --- Fetch customers ---
    try:
        customers = [Customer.from_dict(c) for c in list_pages("customer", page_size=100)]
        customer_options = [c.name for c in customers]
    except Exception as e:
        st.error(f"Error fetching customers: {e}")
        customer_options = []

    # --- Fetch stores ---
    try:
        stores = [Store.from_dict(c) for c in list_pages("store", page_size=100)]
        store_options = [c.name for c in stores]
    except Exception as e:
        st.error(f"Error fetching stores: {e}")
        store_options = []

    # --- Required Inputs ---
    st.subheader("Required Inputs")
    date = st.date_input(
        label="Order Date",
        value="today",
        format=get_settings().ST_DATE_FORMAT,
    )
    order_customer = st.selectbox(
        label="Customer",
        index=None,
        options=customer_options,
        placeholder='Select a custommer',
        accept_new_options=False
    )
    order_store = st.selectbox(
        label="Store",
        index=None,
        options=store_options,
        placeholder='Select a store',
        accept_new_options=False
    )

    # --- Editor de produtos (apenas colunas editáveis) ---
    if "order_df" not in st.session_state:
        st.session_state["order_df"] = pd.DataFrame([{
            "Product": None,
            "Quantity": 1,
            "Suggested Price": 0.0,
            "Price": 0.0,
            "Total": 0.0
        }])

    edited = st.data_editor(
        data=st.session_state["order_df"],
        num_rows="dynamic",
        column_config={
            "Product": st.column_config.SelectboxColumn(
                "Product", options=product_options, required=True
            ),
            "Quantity": st.column_config.NumberColumn(
                "Quantity", min_value=1, step=1, default=1
            ),
            "Suggested Price": st.column_config.NumberColumn(
                "Suggested Price", disabled=True, default=0.0, format=get_settings().ST_ORDER_NUMBER_FORMAT
            ),
            "Price": st.column_config.NumberColumn(
                "Price", default=0.0, required=True, format=get_settings().ST_ORDER_NUMBER_FORMAT
            ),
            "Total": st.column_config.NumberColumn(
                "Total", disabled=True, default=0.0, format=get_settings().ST_ORDER_NUMBER_FORMAT
            )
        },
        key="order_editor"
    )

    if not edited.empty:
        edited["Suggested Price"] = edited["Product"].map(
            lambda name: product_map[name].price if name in product_map else 0.0
        )
        edited["Total"] = edited["Quantity"] * edited["Price"]

    # --- salva de volta ---
    st.session_state["order_df"] = edited

    st.metric(
        label="Total Order",
        value=f"R$ {edited['Total'].sum():.2f}",
    )

    # --- Campos opcionais ---
    st.subheader("Optional Inputs")
    description = st.text_area("Description", height=100)

    # --- Botão criar pedido ---
    # if st.button("Create Order", type="primary", use_container_width=True):
    #     new_order = Order(
    #         name=f"Order {datetime.now().strftime(get_settings().DEFAULT_DATE_FORMAT)}",
    #         order_date=date,
    #         store_id=order_store,
    #         customer_id=order_customer,
    #         total_value=edited["Total"].sum(),
    #     )
    #
    #     with st.spinner("Creating order..."):
    #         create_order_on_notion(new_order)
    #         time.sleep(1)
    #
    #     st.session_state["order_dialog_open"] = False
    #     st.rerun()

