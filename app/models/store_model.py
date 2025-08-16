import json
from datetime import datetime
from typing import Optional, Dict

from utils.notion_utils import extract_properties_to_easy_dict
from core.config import get_settings


settings = get_settings()


class Store:
    """Store class representation"""

    def __init__(self,
                 store_id: str,
                 name: str,
                 store_type: Optional[str],
                 website: Optional[str],
                 description: Optional[str],
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = settings.DB_STORE_ID
        self.store_id = store_id
        self.name = name
        self.store_type = store_type
        self.website = website
        self.description = description
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.store_id,
            "Name": self.name,
            "Type": self.store_type,
            "Website": self.website,
            "Description": self.description,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, store_as_json: str) -> 'Store':
        store_as_dict = json.loads(store_as_json)
        return cls.from_dict(store_as_dict)

    @classmethod
    def from_dict(cls, store_as_dict: Dict) -> 'Store':
        props = extract_properties_to_easy_dict(store_as_dict)

        return cls(
            notion_id=store_as_dict.get('id'),
            store_id=props.get('ID'),
            name=props.get('Name'),
            store_type=props.get('Type'),
            website=props.get('Website'),
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
                "url": "https://www.notion.so/icons/store_gray.svg"
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
            "Type": {
                "type": "select",
                "select": {"name": self.store_type} if self.store_type else None
            },
            "Website": {
                "type": "url",
                "url": self.website
            },
            "Description": {
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": self.description}
                }] if self.description else []
            }
        }
