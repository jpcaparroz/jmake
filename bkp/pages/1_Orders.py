import streamlit as st
from datetime import datetime
from services.notion_service import DB, slist_pages, ensure_customer, ensure_store, create_order

st.title('Orders')

stores = list_pages(DB['stores']) if DB['stores'] else []
customers = list_pages(DB['customers']) if DB['customers'] else []
products = list_pages(DB['products']) if DB['products'] else []

store_map = { p['properties']['Store']['title'][0]['plain_text']: p['id'] for p in stores if p['properties'].get('Store',{}).get('title') }
customer_map = { p['properties']['Customer']['title'][0]['plain_text']: p['id'] for p in customers if p['properties'].get('Customer',{}).get('title') }
product_map = { p['properties']['Product']['title'][0]['plain_text']: p['id'] for p in products if p['properties'].get('Product',{}).get('title') }

with st.form('new_order'):
    st.subheader('New Order')
    colA, colB = st.columns(2)

    store_name = colA.selectbox('Store', options=list(store_map.keys()) + ['+ New store'])
    if store_name == '+ New store':
        store_name = colA.text_input('New store name')
        store_type = colA.selectbox('Type', options=['Marketplace','Online','Physical'])
        store_id = None
    else:
        store_id = store_map.get(store_name)
        store_type = 'Marketplace'

    cust_name = colB.selectbox('Customer', options=list(customer_map.keys()) + ['+ New customer'])
    if cust_name == '+ New customer':
        cust_name = colB.text_input('New customer name')
        cust_phone = colB.text_input('Phone')
        cust_email = colB.text_input('Email')
        cust_id = None
    else:
        cust_id = customer_map.get(cust_name)
        cust_phone = cust_email = ''

    date_str = st.date_input('Date', value=datetime.today()).isoformat()
    pay_method = st.selectbox('Payment Method', options=['PIX','Credit Card','Debit Card','Cash','Other'])
    status = st.selectbox('Status', options=['Pending','Paid','Cancelled'])

    st.markdown('### Items')
    item_rows = st.number_input('How many different products?', min_value=1, max_value=50, value=1)

    items = []
    for i in range(int(item_rows)):
        st.markdown(f'**Item {i+1}**')
        p = st.selectbox(f'Product #{i+1}', options=list(product_map.keys()), key=f'p{i}')
        q = st.number_input(f'Quantity #{i+1}', min_value=1.0, value=1.0, key=f'q{i}')
        up = st.number_input(f'Unit Price #{i+1}', min_value=0.0, value=0.0, key=f'u{i}')
        items.append({'product_name': p, 'quantity': q, 'unit_price': up})

    submitted = st.form_submit_button('Create Order')

    if submitted:
        if not store_id:
            store_id = ensure_store(store_name, type_=store_type)
        if not cust_id:
            cust_id = ensure_customer(cust_name, phone=cust_phone, email=cust_email)

        mapped = []
        for it in items:
            pid = product_map.get(it['product_name'])
            if not pid:
                st.error(f"Product not found: {it['product_name']}")
                st.stop()
            mapped.append({'product_id': pid, 'quantity': it['quantity'], 'unit_price': it['unit_price']})

        code = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        result = create_order(code, date_str, store_id, cust_id, pay_method, status, mapped)
        st.success(f"Order created! Total: R$ {result['total']:.2f}")

st.divider()
st.subheader('Recent Orders')
orders = list_pages(DB['orders']) if DB['orders'] else []
for o in orders:
    oid = o['properties']['Order ID']['title'][0]['plain_text'] if o['properties'].get('Order ID',{}).get('title') else '—'
    total = o['properties'].get('Total Value',{}).get('number') or 0
    st.write(f"{oid} — Total R$ {total:.2f}")

# =============================
# pages/2_Products.py
# =============================
import streamlit as st
from app.services.notion_service import DB, create_page, list_pages, _title, _select, _number, adjust_stock
from datetime import datetime

st.title('Products')

with st.form('new_product'):
    name = st.text_input('Product name', '')
    category = st.text_input('Category', '')
    price = st.number_input('Sale Price', min_value=0.0, value=0.0)
    sku = st.text_input('SKU', '')
    submitted = st.form_submit_button('Create Product')
    if submitted and name:
        props = {
            'Product': _title(name),
            'Category': _select(category or None),
            'Sale Price': _number(price),
            'SKU': {"rich_text": [{"text": {"content": sku}}]},
        }
        create_page(DB['products'], props)
        st.success('Product created!')

st.divider()
st.subheader('Quick stock input (In)')
products = list_pages(DB['products']) if DB['products'] else []
product_map = { p['properties']['Product']['title'][0]['plain_text']: p['id'] for p in products if p['properties'].get('Product',{}).get('title') }

with st.form('stock_in'):
    pname = st.selectbox('Product', options=list(product_map.keys()))
    qty = st.number_input('Quantity', min_value=1.0, value=1.0)
    date_str = st.date_input('Date', value=datetime.today()).isoformat()
    go = st.form_submit_button('Add movement (In)')
    if go:
        adjust_stock(product_map[pname], qty, date_str, 'In', notes='Manual input')
        st.success('Stock updated!')

st.divider()
st.subheader('All products')
for p in products:
    name = p['properties']['Product']['title'][0]['plain_text'] if p['properties'].get('Product',{}).get('title') else '—'
    price = p['properties'].get('Sale Price',{}).get('number') or 0
    st.write(f"{name} — R$ {price:.2f}")
