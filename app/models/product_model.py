import json
from datetime import datetime
from typing import Optional, Dict, List

from utils.notion_utils import extract_properties_to_easy_dict
from core.config import get_settings


settings = get_settings()


class Product:
    """Product class representation"""

    def __init__(self,
                 name: str,
                 product_id: Optional[str] = None,
                 price: Optional[float] = 0.0,
                 stock: Optional[List[str]]  = None,
                 category: Optional[List[str]] = None,
                 stock_qty: Optional[int] = None,
                 print_time: Optional[float] = 0.0,
                 created_time: Optional[datetime] = None,
                 last_edited_time: Optional[datetime] = None,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = settings.DB_PRODUCT_ID
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock
        self.category = category
        self.stock_qty = stock_qty
        self.print_time = print_time
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.product_id,
            "Name": self.name,
            "Price": self.price,
            "Stock": self.stock,
            "Category": self.category,
            "Stock Qty": self.stock_qty,
            "Print Time": self.print_time,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, product_as_json: str) -> 'Product':
        product_as_dict = json.loads(product_as_json)
        return cls.from_dict(product_as_dict)

    @classmethod
    def from_dict(cls, product_as_dict: Dict) -> 'Product':
        props = extract_properties_to_easy_dict(product_as_dict)

        return cls(
            notion_id=product_as_dict.get('id'),
            product_id=props.get('ID'),
            name=props.get('Name'),
            price=props.get('Price'),
            stock=props.get('Stock', []),
            category=props.get('Category', []),
            stock_qty=props.get('Stock Qty'),
            print_time=props.get('Print Time'),
            created_time=props.get('Created time'),
            last_edited_time=props.get('Last edited time')
        )

    def get_parent(self) -> dict:
        return {
            "type": "database_id",
            "database_id": self.database_id
        }

    def get_icon(self) -> dict:
        return {
            "type": "external",
            "external": {
                "url": "https://www.notion.so/icons/barcode_gray.svg"
            }
        }

    def get_notion_json(self) -> dict:
        return {
            "Name": {
                "type": "title",
                "title": [{
                    "type": "text",
                    "text": {"content": self.name}
                }]
            },
            "Price": {
                "type": "number",
                "number": self.price if self.price is not None else 0.0
            },
            "Category": {
                "type": "relation",
                "relation": [{"id": c} for c in self.category]
            },
            "Print Time": {
                "type": "number",
                "number": self.print_time if self.print_time is not None else 0.0
            }
        }
