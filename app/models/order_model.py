import json
from datetime import datetime, date
from typing import Optional, Dict, List

from app.utils.notion_utils import extract_properties_to_easy_dict
from app.core.config import DB


class Order:
    """Order class representation"""

    def __init__(self,
                 order_id: str,
                 name: str,
                 order_date: date,
                 store_ids: List[str],
                 customer_ids: List[str],
                 sale_item_ids: List[str],
                 total_value: Optional[float],
                 description: Optional[str],
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = DB['order']
        self.order_id = order_id
        self.name = name
        self.order_date = order_date
        self.store_ids = store_ids
        self.customer_ids = customer_ids
        self.sale_item_ids = sale_item_ids
        self.total_value = total_value
        self.description = description
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.order_id,
            "Name": self.name,
            "Date": self.order_date,
            "Store": self.store_ids,
            "Customer": self.customer_ids,
            "Sale Item": self.sale_item_ids,
            "Total Value": self.total_value,
            "Description": self.description,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, order_as_json: str) -> 'Order':
        order_as_dict = json.loads(order_as_json)
        return cls.from_dict(order_as_dict)

    @classmethod
    def from_dict(cls, order_as_dict: Dict) -> 'Order':
        props = extract_properties_to_easy_dict(order_as_dict)

        return cls(
            notion_id=order_as_dict.get('id'),
            order_id=props.get('ID'),
            name=props.get('Name'),
            order_date=props.get('Date'),
            store_ids=props.get('Store', []),
            customer_ids=props.get('Customer', []),
            sale_item_ids=props.get('Sale Item', []),
            total_value=props.get('Total Value'),
            description=props.get('Description'),
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
                "url": "https://www.notion.so/icons/shopping-cart_gray.svg"
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
            "Date": {
                "type": "date",
                "date": {"start": self.order_date.isoformat()} if self.order_date else None
            },
            "Store": {
                "type": "relation",
                "relation": [{"id": store_id} for store_id in self.store_ids]
            },
            "Customer": {
                "type": "relation",
                "relation": [{"id": cust_id} for cust_id in self.customer_ids]
            },
            "Sale Item": {
                "type": "relation",
                "relation": [{"id": item_id} for item_id in self.sale_item_ids]
            },
            "Description": {
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": self.description}
                }] if self.description else []
            }
        }
