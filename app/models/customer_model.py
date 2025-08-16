import json
from datetime import datetime
from typing import Optional, Dict, List

from utils.notion_utils import extract_properties_to_easy_dict
from core.config import get_settings


settings = get_settings()


class Customer:
    """Customer class representation"""

    def __init__(self,
                 customer_id: str,
                 name: str,
                 order: List[str],
                 phone: Optional[str],
                 address: Optional[float],
                 country: Optional[str],
                 email: Optional[str],
                 description: Optional[str],
                 gender: Optional[str],
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = settings.DB_CUSTOMER_ID
        self.customer_id = customer_id
        self.name = name
        self.order = order
        self.phone = phone
        self.address = address
        self.country = country
        self.email = email
        self.description = description
        self.gender = gender
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.customer_id,
            "Name": self.name,
            "Order": self.order,
            "Phone": self.phone,
            "Address": self.address,
            "Country": self.country,
            "Email": self.email,
            "Description": self.description,
            "Gender": self.gender,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, customer_as_json: str) -> 'Customer':
        customer_as_dict = json.loads(customer_as_json)
        return cls.from_dict(customer_as_dict)

    @classmethod
    def from_dict(cls, customer_as_dict: Dict) -> 'Customer':
        props = extract_properties_to_easy_dict(customer_as_dict)

        return cls(
            notion_id=customer_as_dict.get('id'),
            customer_id=props.get('ID'),
            name=props.get('Name'),
            order=props.get('Order', []),
            phone=props.get('Phone'),
            address=props.get('Address'),
            country=props.get('Country'),
            email=props.get('Email'),
            description=props.get('Description'),
            gender=props.get('Gender'),
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
                "url": "https://www.notion.so/icons/person_gray.svg"
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
            "Order": {
                "type": "relation",
                "relation": [{"id": o} for o in self.order]
            },
            "Phone": {
                "type": "phone_number",
                "phone_number": self.phone
            },
            "Address": {
                "type": "number",
                "number": self.address
            },
            "Country": {
                "type": "select",
                "select": {"name": self.country} if self.country else None
            },
            "Email": {
                "type": "email",
                "email": self.email
            },
            "Description": {
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": self.description}
                }] if self.description else []
            },
            "Gender": {
                "type": "select",
                "select": {"name": self.gender} if self.gender else None
            }
        }
