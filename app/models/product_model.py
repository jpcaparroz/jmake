import json
from datetime import datetime
from typing import Optional, Dict, List

from app.utils.notion_utils import extract_properties_to_easy_dict
from app.core.config import DB


class Product:
    """Product class representation"""

    def __init__(self,
                 product_id: str,
                 name: str,
                 price: float,
                 stock: List[str],
                 category: List[str],
                 stock_qty: Optional[int],
                 print_time: Optional[float],
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = DB['product']
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

    async def get_parent(self) -> dict:
        return {
            "type": "database_id",
            "database_id": self.database_id
        }

    async def get_icon(self) -> dict:
        return {
            "type": "external",
            "external": {
                "url": "https://www.notion.so/icons/barcode_gray.svg"
            }
        }

    async def get_notion_json(self) -> dict:
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
                "number": self.price
            },
            "Stock": {
                "type": "relation",
                "relation": [{"id": s} for s in self.stock]
            },
            "Category": {
                "type": "relation",
                "relation": [{"id": c} for c in self.category]
            },
            "Print Time": {
                "type": "number",
                "number": self.print_time
            }
        }
