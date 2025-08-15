import json
from datetime import datetime
from typing import Optional, Dict, List

from app.utils.notion_utils import extract_properties_to_easy_dict
from app.core.config import DB


class StockMovement:
    """Stock Movement class representation"""

    def __init__(self,
                 stock_movement_id: str,
                 name: str,
                 product: List[str],
                 type: Optional[str],
                 description: Optional[str],
                 quantity: Optional[float],
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = DB['stock_movement']
        self.stock_movement_id = stock_movement_id
        self.name = name
        self.product = product
        self.type = type
        self.description = description
        self.quantity = quantity
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.stock_movement_id,
            "Name": self.name,
            "Product": self.product,
            "Type": self.type,
            "Description": self.description,
            "Quantity": self.quantity,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, stock_movement_as_json: str) -> 'StockMovement':
        stock_movement_as_dict = json.loads(stock_movement_as_json)
        return cls.from_dict(stock_movement_as_dict)

    @classmethod
    def from_dict(cls, stock_movement_as_dict: Dict) -> 'StockMovement':
        props = extract_properties_to_easy_dict(stock_movement_as_dict)

        return cls(
            notion_id=stock_movement_as_dict.get('id'),
            stock_movement_id=props.get('ID'),
            name=props.get('Name'),
            product=props.get('Product', []),
            type=props.get('Type'),
            description=props.get('Description'),
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
            "Type": {
                "type": "select",
                "select": {"name": self.type} if self.type else None
            },
            "Description": {
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": self.description}
                }] if self.description else []
            },
            "Quantity": {
                "type": "number",
                "number": self.quantity
            }
        }
