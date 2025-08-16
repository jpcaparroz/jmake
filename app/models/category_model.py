import json
from datetime import datetime
from typing import Optional, Dict

from utils.notion_utils import extract_properties_to_easy_dict
from core.config import get_settings

settings = get_settings()

class Category:
    """Category class representation"""

    def __init__(self,
                 category_id: str,
                 name: str,
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = settings.DB_CATEGORY_ID
        self.category_id = category_id
        self.name = name
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.category_id,
            "Name": self.name,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, category_as_json: str) -> 'Category':
        category_as_dict = json.loads(category_as_json)
        return cls.from_dict(category_as_dict)

    @classmethod
    def from_dict(cls, category_as_dict: Dict) -> 'Category':
        props = extract_properties_to_easy_dict(category_as_dict)

        return cls(
            notion_id=category_as_dict.get('id'),
            category_id=props.get('ID'),
            name=props.get('Name'),
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
                "title": [{
                    "type": "text",
                    "text": {"content": self.name}
                }]
            }
        }
