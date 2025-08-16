import json
from datetime import datetime
from typing import Optional, Dict, List

from utils.notion_utils import extract_properties_to_easy_dict
from core.config import get_settings


settings = get_settings()


class Stock:
    """Stock class representation"""

    def __init__(self,
                 stock_id: str,
                 name: str,
                 product: List[str],
                 entries: Optional[float],
                 sales: Optional[float],
                 quantity: Optional[float],
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = settings.DB_STOCK_ID
        self.stock_id = stock_id
        self.name = name
        self.product = product
        self.entries = entries
        self.sales = sales
        self.quantity = quantity
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.stock_id,
            "Name": self.name,
            "Product": self.product,
            "Entries": self.entries,
            "Sales": self.sales,
            "Quantity": self.quantity,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, stock_as_json: str) -> 'Stock':
        stock_as_dict = json.loads(stock_as_json)
        return cls.from_dict(stock_as_dict)

    @classmethod
    def from_dict(cls, stock_as_dict: Dict) -> 'Stock':
        props = extract_properties_to_easy_dict(stock_as_dict)

        return cls(
            notion_id=stock_as_dict.get('id'),
            stock_id=props.get('ID'),
            name=props.get('Name'),
            product=props.get('Product', []),
            entries=props.get('Entries'),
            sales=props.get('Sales'),
            quantity=props.get('Quantity'),
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
            "Product": {
                "type": "relation",
                "relation": [{"id": p} for p in self.product]
            },
            "Entries": {
                "type": "number",
                "number": self.entries
            },
            "Sales": {
                "type": "number",
                "number": self.sales
            },
            "Quantity": {
                "type": "formula",
                "formula": {"type": "number", "number": self.quantity}
            }
        }
