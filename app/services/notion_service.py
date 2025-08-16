from typing import Dict, Any, List, Optional

# from app.models import Category, Product, Customer, Supplier, Store, Order, OrderItem, Stock, StockMovement
from core.config import get_notion_client, get_db_map

notion = get_notion_client()
db = get_db_map()

# ---- Low-level helpers ----
def create_page(db_id: str, properties: Dict[str, Any]) -> dict:
    return notion.pages.create(parent={"database_id": db_id}, properties=properties)


def update_page(page_id: str, properties: Dict[str, Any]) -> dict:
    return notion.pages.update(page_id=page_id, properties=properties)


def find_by_title(db_id: str, title_prop: str, title: str) -> Optional[dict]:
    res = notion.databases.query(database_id=db_id, filter={
        "property": title_prop,
        "title": {"equals": title}
    })
    results = res.get('results', [])
    return results[0] if results else None


def list_pages(db_name: str, page_size: int = 50) -> List[dict]:
    db_id = db.get(db_name)
    if not db_id:
        raise ValueError(f"Database '{db_name}' not found in configuration.")
    res = notion.databases.query(database_id=db_id, page_size=page_size)
    return res.get('results', [])


def get_database_count(db_name: str) -> int:
    return len(list_pages(db_name))

# ---- Domain helpers (align with your TSX flows) ----
# def ensure_customer(name: str, phone: str = '', email: str = '', address: str = '') -> str:
#     db = DB['customer']
#     page = find_by_title(db, 'Customer', name)
#     if page:
#         return page['id']
#     props = {
#         'Customer': _title(name),
#         'Phone': {"phone_number": phone or None},
#         'Email': {"email": email or None},
#         'Address': _rich(address or ''),
#     }
#     return create_page(db, props)['id']


# def ensure_store(name: str, type_: str = 'Marketplace', website: str = '') -> str:
#     db = DB['stores']
#     page = find_by_title(db, 'Store', name)
#     if page:
#         return page['id']
#     props = {
#         'Store': _title(name),
#         'Type': _select(type_),
#         'Website': {"url": website or None},
#     }
#     return create_page(db, props)['id']


# def create_stock_if_missing(product_id: str) -> str:
#     res = notion_client.databases.query(database_id=DB['stock'], filter={
#         "property": "Product",
#         "relation": {"contains": product_id},
#     })
#     if res.get('results'):
#         return res['results'][0]['id']
#     props = {
#         'Product': _relation(product_id),
#         'Initial Qty': _number(0),
#         'Current Qty': _number(0),
#     }
#     return create_page(DB['stock'], props)['id']


# def adjust_stock(product_id: str, qty_delta: float, iso_date: str, movement_type: str, notes: str = '', order_id: str = ''):
#     # Movement
#     mv_props = {
#         'Date': _date_iso(iso_date),
#         'Product': _relation(product_id),
#         'Type': _select(movement_type),
#         'Quantity': _number(abs(qty_delta)),
#         'Notes': _rich(notes),
#     }
#     if order_id:
#         mv_props['Order'] = _relation(order_id)
#     create_page(DB['stock_movements'], mv_props)

#     # Balance
#     stock_id = create_stock_if_missing(product_id)
#     stock_page = notion_client.pages.retrieve(stock_id)
#     current = stock_page['properties']['Current Qty'].get('number') or 0
#     new_value = current + qty_delta
#     update_page(stock_id, {
#         'Current Qty': _number(new_value),
#         'Last Update': _date_iso(iso_date),
#     })


# def create_order(order_title: str, iso_date: str, store_id: str, customer_id: str, payment: str, status: str, items: List[dict]) -> dict:
#     order = create_page(DB['orders'], {
#         'Order ID': _title(order_title),
#         'Date': _date_iso(iso_date),
#         'Store': _relation(store_id),
#         'Customer': _relation(customer_id),
#         'Payment Method': _select(payment),
#         'Status': _select(status),
#         'Total Value': _number(0),
#     })
#     order_id = order['id']

#     total = 0.0
#     for it in items:
#         qty = float(it['quantity'])
#         unit = float(it['unit_price'])
#         line_total = qty * unit
#         total += line_total
#         create_page(DB['order_items'], {
#             'Order': _relation(order_id),
#             'Product': _relation(it['product_id']),
#             'Quantity': _number(qty),
#             'Unit Price': _number(unit),
#             'Total': _number(line_total),
#         })
#         adjust_stock(it['product_id'], -qty, iso_date, 'Out', notes=f'Order {order_title}', order_id=order_id)

#     update_page(order_id, {'Total Value': _number(total)})
#     return {"order_id": order_id, "total": total}
