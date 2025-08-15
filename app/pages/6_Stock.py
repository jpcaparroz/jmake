import streamlit as st
from services.notion import DB, list_pages, adjust_stock
from datetime import datetime

st.title('Stock')
stock = list_pages(DB['stock']) if DB['stock'] else []

st.subheader('Current stock')
for s in stock:
    qty = s['properties'].get('Current Qty',{}).get('number') or 0
    rel = s['properties'].get('Product',{}).get('relation',[])
    pid = rel[0]['id'] if rel else '—'
    st.write(f"ProductId {pid} — Qty: {qty}")

st.divider()
st.subheader('Manual movement')
products = list_pages(DB['products']) if DB['products'] else []
product_map = { p['properties']['Product']['title'][0]['plain_text']: p['id'] for p in products if p['properties'].get('Product',{}).get('title') }

with st.form('manual_move'):
    pname = st.selectbox('Product', options=list(product_map.keys()))
    mtype = st.selectbox('Type', options=['In','Out'])
    qty = st.number_input('Quantity', min_value=1.0, value=1.0)
    date_str = st.date_input('Date', value=datetime.today()).isoformat()
    go = st.form_submit_button('Apply movement')
    if go:
        delta = qty if mtype=='In' else -qty
        adjust_stock(product_map[pname], delta, date_str, mtype, notes='Manual movement')
        st.success('Stock updated!')
