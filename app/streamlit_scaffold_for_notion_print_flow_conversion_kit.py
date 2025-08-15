# =============================
# README_migration.md
# =============================
"""
Goal: Convert a TSX/Next.js front-end (notion-print-flow) into a Python Streamlit app that keeps the same flows and connects to Notion via notion-client.

Status: This kit is ready-to-run and easy to extend once the TSX repo structure is known. Drop your Notion DB IDs in .env and launch. Then map each TSX page/component to a Streamlit page or widget using the checklist below.

---
Quick start
---
1) pip install -r requirements.txt
2) Copy .env.sample to .env and fill:
   - NOTION_API_KEY, DB_* IDs
3) streamlit run app.py

---
What you’ll map from TSX -> Streamlit
---
- Routes/pages -> Streamlit multipage (app.py + pages/)
- React state/hooks -> st.session_state
- Forms -> st.form
- Tables/Lists -> st.dataframe / st.table
- Dialogs/Toasts -> st.toast()/st.success()/st.error()
- API/Fetch -> direct notion-client calls in services/notion.py
- Navigation -> st.page_link + sidebar

---
Migration checklist (fill as you port)
---
[ ] Identify pages/routes in TSX (e.g. /orders, /products)
[ ] List reusable components (tables, item editor, filters)
[ ] Inventory of Notion DBs + properties used
[ ] Map each API call to a function in services/notion.py
[ ] Reproduce page layouts with Streamlit columns/expanders
[ ] Recreate forms and validation
[ ] Wire data mutations (create/update/delete)
[ ] Add success/error feedback
[ ] Test end-to-end flows (create order, add items, stock adjust)

"""

# =============================
# requirements.txt
# =============================
"""
streamlit
notion-client
python-dotenv
"""

# =============================
# .env.sample
# =============================
"""
NOTION_API_KEY=
DB_PRODUCTS_ID=
DB_CUSTOMERS_ID=
DB_STORES_ID=
DB_ORDERS_ID=
DB_ORDER_ITEMS_ID=
DB_COSTS_ID=
DB_STOCK_ID=
DB_STOCK_MOVEMENTS_ID=
"""

# =============================
# services/notion.py
# =============================
from notion_client import Client
from dotenv import load_dotenv
import os
from typing import Dict, Any, List, Optional

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
if not NOTION_API_KEY:
    raise RuntimeError('NOTION_API_KEY missing in environment')

client = Client(auth=NOTION_API_KEY)

DB = {
    'products': os.getenv('DB_PRODUCTS_ID'),
    'customers': os.getenv('DB_CUSTOMERS_ID'),
    'stores': os.getenv('DB_STORES_ID'),
    'orders': os.getenv('DB_ORDERS_ID'),
    'order_items': os.getenv('DB_ORDER_ITEMS_ID'),
    'costs': os.getenv('DB_COSTS_ID'),
    'stock': os.getenv('DB_STOCK_ID'),
    'stock_movements': os.getenv('DB_STOCK_MOVEMENTS_ID'),
}

# ---- Low-level helpers ----

def _title(text: str):
    return {"title": [{"text": {"content": text}}]}


def _rich(text: str):
    return {"rich_text": [{"text": {"content": text}}]}


def _number(n: float):
    return {"number": float(n)}


def _select(name: str | None):
    return {"select": {"name": name}} if name else {"select": None}


def _date_iso(iso: str):
    return {"date": {"start": iso}}


def _relation(page_id: str):
    return {"relation": [{"id": page_id}]} if page_id else {"relation": []}


def create_page(db_id: str, properties: Dict[str, Any]) -> dict:
    return client.pages.create(parent={"database_id": db_id}, properties=properties)


def update_page(page_id: str, properties: Dict[str, Any]) -> dict:
    return client.pages.update(page_id=page_id, properties=properties)


def find_by_title(db_id: str, title_prop: str, title: str) -> Optional[dict]:
    res = client.databases.query(database_id=db_id, filter={
        "property": title_prop,
        "title": {"equals": title}
    })
    results = res.get('results', [])
    return results[0] if results else None


def list_pages(db_id: str, page_size: int = 50) -> List[dict]:
    res = client.databases.query(database_id=db_id, page_size=page_size)
    return res.get('results', [])

# ---- Domain helpers (align with your TSX flows) ----

def ensure_customer(name: str, phone: str = '', email: str = '', address: str = '') -> str:
    db = DB['customers']
    page = find_by_title(db, 'Customer', name)
    if page:
        return page['id']
    props = {
        'Customer': _title(name),
        'Phone': {"phone_number": phone or None},
        'Email': {"email": email or None},
        'Address': _rich(address or ''),
    }
    return create_page(db, props)['id']


def ensure_store(name: str, type_: str = 'Marketplace', website: str = '') -> str:
    db = DB['stores']
    page = find_by_title(db, 'Store', name)
    if page:
        return page['id']
    props = {
        'Store': _title(name),
        'Type': _select(type_),
        'Website': {"url": website or None},
    }
    return create_page(db, props)['id']


def create_stock_if_missing(product_id: str) -> str:
    res = client.databases.query(database_id=DB['stock'], filter={
        "property": "Product",
        "relation": {"contains": product_id},
    })
    if res.get('results'):
        return res['results'][0]['id']
    props = {
        'Product': _relation(product_id),
        'Initial Qty': _number(0),
        'Current Qty': _number(0),
    }
    return create_page(DB['stock'], props)['id']


def adjust_stock(product_id: str, qty_delta: float, iso_date: str, movement_type: str, notes: str = '', order_id: str = ''):
    # Movement
    mv_props = {
        'Date': _date_iso(iso_date),
        'Product': _relation(product_id),
        'Type': _select(movement_type),
        'Quantity': _number(abs(qty_delta)),
        'Notes': _rich(notes),
    }
    if order_id:
        mv_props['Order'] = _relation(order_id)
    create_page(DB['stock_movements'], mv_props)

    # Balance
    stock_id = create_stock_if_missing(product_id)
    stock_page = client.pages.retrieve(stock_id)
    current = stock_page['properties']['Current Qty'].get('number') or 0
    new_value = current + qty_delta
    update_page(stock_id, {
        'Current Qty': _number(new_value),
        'Last Update': _date_iso(iso_date),
    })


def create_order(order_title: str, iso_date: str, store_id: str, customer_id: str, payment: str, status: str, items: List[dict]) -> dict:
    order = create_page(DB['orders'], {
        'Order ID': _title(order_title),
        'Date': _date_iso(iso_date),
        'Store': _relation(store_id),
        'Customer': _relation(customer_id),
        'Payment Method': _select(payment),
        'Status': _select(status),
        'Total Value': _number(0),
    })
    order_id = order['id']

    total = 0.0
    for it in items:
        qty = float(it['quantity'])
        unit = float(it['unit_price'])
        line_total = qty * unit
        total += line_total
        create_page(DB['order_items'], {
            'Order': _relation(order_id),
            'Product': _relation(it['product_id']),
            'Quantity': _number(qty),
            'Unit Price': _number(unit),
            'Total': _number(line_total),
        })
        adjust_stock(it['product_id'], -qty, iso_date, 'Out', notes=f'Order {order_title}', order_id=order_id)

    update_page(order_id, {'Total Value': _number(total)})
    return {"order_id": order_id, "total": total}

# =============================
# app.py
# =============================
import streamlit as st
from services.notion import DB, list_pages

st.set_page_config(page_title='Notion Print Flow — Streamlit', page_icon='🧱', layout='wide')

st.title('Notion Print Flow — Dashboard')
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

# =============================
# pages/1_Orders.py
# =============================
import streamlit as st
from datetime import datetime
from services.notion import DB, list_pages, ensure_customer, ensure_store, create_order

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
from services.notion import DB, create_page, list_pages, _title, _select, _number, adjust_stock
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

# =============================
# pages/3_Customers.py
# =============================
import streamlit as st
from services.notion import DB, create_page, list_pages, _title

st.title('Customers')
with st.form('new_cust'):
    name = st.text_input('Customer name')
    phone = st.text_input('Phone')
    email = st.text_input('Email')
    address = st.text_area('Address')
    go = st.form_submit_button('Create')
    if go and name:
        props = {
            'Customer': _title(name),
            'Phone': {"phone_number": phone or None},
            'Email': {"email": email or None},
            'Address': {"rich_text": [{"text": {"content": address or ''}}]},
        }
        create_page(DB['customers'], props)
        st.success('Customer created!')

st.divider()
st.subheader('All customers')
for c in list_pages(DB['customers']):
    n = c['properties']['Customer']['title'][0]['plain_text'] if c['properties'].get('Customer',{}).get('title') else '—'
    st.write(n)

# =============================
# pages/4_Stores.py
# =============================
import streamlit as st
from services.notion import DB, create_page, list_pages, _title, _select

st.title('Stores')
with st.form('new_store'):
    name = st.text_input('Store name')
    type_ = st.selectbox('Type', options=['Marketplace','Online','Physical'])
    website = st.text_input('Website')
    go = st.form_submit_button('Create')
    if go and name:
        props = {
            'Store': _title(name),
            'Type': _select(type_),
            'Website': {"url": website or None},
        }
        create_page(DB['stores'], props)
        st.success('Store created!')

st.divider()
st.subheader('All stores')
for s in list_pages(DB['stores']):
    n = s['properties']['Store']['title'][0]['plain_text'] if s['properties'].get('Store',{}).get('title') else '—'
    st.write(n)

# =============================
# pages/5_Costs.py
# =============================
import streamlit as st
from datetime import datetime
from services.notion import DB, list_pages, create_page, _date_iso, _relation, _number, _select, _rich

st.title('Costs')
products = list_pages(DB['products']) if DB['products'] else []
product_map = { p['properties']['Product']['title'][0]['plain_text']: p['id'] for p in products if p['properties'].get('Product',{}).get('title') }

with st.form('new_cost'):
    date_str = st.date_input('Date', value=datetime.today()).isoformat()
    ctype = st.selectbox('Cost Type', options=['Material','Energy','Packaging','Maintenance','Other'])
    value = st.number_input('Value', min_value=0.0, value=0.0)
    prod_name = st.selectbox('Product (optional)', options=['— None —'] + list(product_map.keys()))
    notes = st.text_area('Notes', '')
    go = st.form_submit_button('Create cost')
    if go:
        props = {
            'Date': _date_iso(date_str),
            'Cost Type': _select(ctype),
            'Value': _number(value),
            'Notes': _rich(notes),
        }
        if prod_name != '— None —':
            props['Product'] = _relation(product_map[prod_name])
        create_page(DB['costs'], props)
        st.success('Cost created!')

st.divider()
st.subheader('Recent costs')
for c in list_pages(DB['costs']):
    ctype = c['properties'].get('Cost Type',{}).get('select',{}).get('name','—')
    val = c['properties'].get('Value',{}).get('number') or 0
    st.write(f"{ctype}: R$ {val:.2f}")

# =============================
# pages/6_Stock.py
# =============================
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

# =============================
# pages/7_Settings.py
# =============================
import streamlit as st
from services.notion import DB, client

st.title('Settings')

st.write('Loaded Database IDs:')
for k, v in DB.items():
    st.write(f"- {k}: {v}")

if st.button('Test Notion connection'):
    try:
        client.search(query='')
        st.success('Notion API reachable!')
    except Exception as e:
        st.error(f'Error: {e}')
