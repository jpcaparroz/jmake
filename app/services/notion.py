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
