import streamlit as st

from services.notion_service import get_database_count
from components.product_components import create_product_dialog, create_product_dialog_state
from components.order_components import create_order_dialog, create_order_dialog_state
from components.order_chart import show_orders_chart


# Main page configs
st.set_page_config(page_icon='🏡', layout='wide')
st.title('Home')

st.divider()

# Layout
col1, col2, col3, col4 = st.columns(4)


# Quick Actions
col1.subheader("Quick Actions")

if col1.button(label="New Product",
               help="Create a new product",
               icon=":material/add:"):
    create_product_dialog_state(True)
    
if st.session_state.get("create_product_dialog_open", False):
    create_product_dialog()

if col1.button(label="New Order",
               help="Create a new order",
               icon=":material/add:"):
    create_order_dialog_state(True)
    
if st.session_state.get("create_order_dialog_open", False):
    create_order_dialog()


# Metrics Cached Data
@st.cache_data
def load_data() -> dict:
    response = {
        'product_count': get_database_count('product'),
        'order_count': get_database_count('order')
    }

    return response

data = load_data()

col1.metric('Orders', data['order_count'], border=True)
col1.metric('Products', data['product_count'], border=True)

show_orders_chart(st)
