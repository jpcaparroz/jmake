import os

from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')

if not NOTION_API_KEY:
    raise RuntimeError('NOTION_API_KEY missing in environment')

notion_client = Client(auth=NOTION_API_KEY)

DB = {
    'product': os.getenv('DB_PRODUCT_ID'),
    'category': os.getenv('DB_CATEGORY_ID'),
    'customer': os.getenv('DB_CUSTOMER_ID'),
    'supplier': os.getenv('DB_SUPPLIER_ID'),
    'store': os.getenv('DB_STORE_ID'),
    'order': os.getenv('DB_ORDER_ID'),
    'order_item': os.getenv('DB_ORDER_ITEM_ID'),
    'cost': os.getenv('DB_COST_ID'),
    'stock': os.getenv('DB_STOCK_ID'),
    'stock_movement': os.getenv('DB_STOCK_MOVEMENT_ID'),
}

DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'America/Sao_Paulo')
DEFAULT_DATE_FORMAT = os.getenv('DEFAULT_DATE_FORMAT', '%d/%m/%Y %H:%M:%S')
