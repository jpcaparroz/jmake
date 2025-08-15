import json
from datetime import datetime
from typing import Optional, Dict, List

from app.utils.notion_utils import extract_properties_to_easy_dict
from app.core.config import DB


class OrderItem:
    """Order Item class representation"""

    def __init__(self,
                 order_item_id: str,
                 name: str,
                 sale_ids: List[str],
                 product_ids: List[str],
                 quantity: Optional[float],
                 price: Optional[float],
                 suggested_price: Optional[float],
                 total_value: Optional[float],
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = DB['order_item']
        self.order_item_id = order_item_id
        self.name = name
        self.sale_ids = sale_ids
        self.product_ids = product_ids
        self.quantity = quantity
        self.price = price
        self.suggested_price = suggested_price
        self.total_value = total_value
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.order_item_id,
            "Name": self.name,
            "Sale": self.sale_ids,
            "Product": self.product_ids,
            "Quantity": self.quantity,
            "Price": self.price,
            "Suggested Price": self.suggested_price,
            "Total Value": self.total_value,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, order_item_as_json: str) -> 'OrderItem':
        order_item_as_dict = json.loads(order_item_as_json)
        return cls.from_dict(order_item_as_dict)

    @classmethod
    def from_dict(cls, order_item_as_dict: Dict) -> 'OrderItem':
        props = extract_properties_to_easy_dict(order_item_as_dict)

        suggested_price = None
        sp_rollup = order_item_as_dict.get('properties', {}).get('Suggested Price', {})
        if sp_rollup.get('type') == 'rollup' and sp_rollup.get('rollup', {}).get('array'):
            suggested_price = sp_rollup['rollup']['array'][0].get('number')

        return cls(
            notion_id=order_item_as_dict.get('id'),
            order_item_id=props.get('ID'),
            name=props.get('Name'),
            sale_ids=props.get('Sale', []),
            product_ids=props.get('Product', []),
            quantity=props.get('Quantity'),
            price=props.get('Price'),
            suggested_price=suggested_price,
            total_value=props.get('Total Value'),
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
                "url": "https://www.notion.so/icons/tag_gray.svg"
            }
        }

    async def get_notion_json(self) -> dict:
        return {
            "Name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": self.name}}]
            },
            "Sale": {
                "type": "relation",
                "relation": [{"id": sid} for sid in self.sale_ids]
            },
            "Product": {
                "type": "relation",
                "relation": [{"id": pid} for pid in self.product_ids]
            },
            "Quantity": {"type": "number", "number": self.quantity},
            "Price": {"type": "number", "number": self.price},
            "Suggested Price": {"type": "number", "number": self.suggested_price},
            "Total Value": {"type": "formula", "formula": {"type": "number", "number": self.total_value}}
        }
