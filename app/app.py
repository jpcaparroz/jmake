import streamlit as st
from app.services.notion_service import DB, list_pages

st.set_page_config(page_title='JMAKE', page_icon='🖨️', layout='wide')

st.title('JMAKE — Dashboard')
col1, col2, col3, col4 = st.columns(4)

orders = list_pages(DB['orders']) if DB['orders'] else []
items = list_pages(DB['order_items']) if DB['order_items'] else []
stock = list_pages(DB['stock']) if DB['stock'] else []

total_orders = len(orders)
revenue = sum([(o['properties'].get('Total Value',{}).get('number') or 0) for o in orders])
items_sold = sum([(i['properties'].get('Quantity',{}).get('number') or 0) for i in items])
low_stock = sum([1 for s in stock if (s['properties'].get('Current Qty',{}).get('number') or 0) <= 2])

col1.metric('Orders', total_orders)
col2.metric('Revenue', f"R$ {revenue:,.2f}")
col3.metric('Items sold', int(items_sold))
col4.metric('Low stock (<=2)', low_stock)

st.sidebar.header('Navigation')
st.page_link('pages/1_Orders.py', label='Orders')
st.page_link('pages/2_Products.py', label='Products')
st.page_link('pages/3_Customers.py', label='Customers')
st.page_link('pages/4_Stores.py', label='Stores')
st.page_link('pages/5_Costs.py', label='Costs')
st.page_link('pages/6_Stock.py', label='Stock')
st.page_link('pages/7_Settings.py', label='Settings')
st.page_link('pages/integrations.py', label='Integrations')
