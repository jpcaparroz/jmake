import streamlit as st

from services.notion_service import get_database_count
from components.order_chart import show_orders_chart


st.set_page_config(page_title='JMAKE', page_icon='🖨️', layout='wide')

st.title('JMAKE — Dashboard')
col1, col2, col3, col4 = st.columns(4)


@st.cache_data
def load_data() -> dict:
    response = {
        'product_count': get_database_count('product'),
        'order_count': get_database_count('order')
    }

    return response

data = load_data()



col1.metric('Orders', data['order_count'], border=True)
col2.metric('Products', data['product_count'], border=True)
# col2.metric('Revenue', f"R$ {revenue:,.2f}")
# col3.metric('Items sold', int(items_sold))
# col4.metric('Low stock (<=2)', low_stock)

show_orders_chart(st)

st.sidebar.header('Navigation')
# st.page_link('pages/1_Orders.py', label='Orders')
# st.page_link('pages/2_Products.py', label='Products')
# st.page_link('pages/3_Customers.py', label='Customers')
# st.page_link('pages/4_Stores.py', label='Stores')
# st.page_link('pages/5_Costs.py', label='Costs')
# st.page_link('pages/6_Stock.py', label='Stock')
# st.page_link('pages/7_Settings.py', label='Settings')
