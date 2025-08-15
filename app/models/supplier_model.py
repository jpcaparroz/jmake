import json
from datetime import datetime
from typing import Optional, Dict

from app.utils.notion_utils import extract_properties_to_easy_dict
from app.core.config import DB


class Supplier:
    """Supplier class representation"""

    def __init__(self,
                 supplier_id: str,
                 name: str,
                 phone: Optional[str],
                 address: Optional[str],
                 email: Optional[str],
                 cnpj: Optional[str],
                 description: Optional[str],
                 created_time: datetime,
                 last_edited_time: datetime,
                 notion_id: Optional[str] = None) -> None:

        self.database_id = DB['supplier']
        self.supplier_id = supplier_id
        self.name = name
        self.phone = phone
        self.address = address
        self.email = email
        self.cnpj = cnpj
        self.description = description
        self.created_time = created_time
        self.last_edited_time = last_edited_time
        self.notion_id = notion_id

    def to_dict(self) -> dict:
        return {
            "DatabaseId": self.database_id,
            "NotionID": self.notion_id,
            "ID": self.supplier_id,
            "Name": self.name,
            "Phone": self.phone,
            "Address": self.address,
            "Email": self.email,
            "CNPJ": self.cnpj,
            "Description": self.description,
            "Created Time": self.created_time,
            "Last Edited Time": self.last_edited_time
        }

    @classmethod
    def from_json(cls, supplier_as_json: str) -> 'Supplier':
        supplier_as_dict = json.loads(supplier_as_json)
        return cls.from_dict(supplier_as_dict)

    @classmethod
    def from_dict(cls, supplier_as_dict: Dict) -> 'Supplier':
        props = extract_properties_to_easy_dict(supplier_as_dict)

        return cls(
            notion_id=supplier_as_dict.get('id'),
            supplier_id=props.get('ID'),
            name=props.get('Name'),
            phone=props.get('Phone'),
            address=props.get('Address'),
            email=props.get('Email'),
            cnpj=props.get('CNPJ'),
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
                "url": "https://www.notion.so/icons/building_gray.svg"
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
            "Phone": {
                "type": "phone_number",
                "phone_number": self.phone
            },
            "Address": {
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": self.address}
                }] if self.address else []
            },
            "Email": {
                "type": "email",
                "email": self.email
            },
            "CNPJ": {
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": self.cnpj}
                }] if self.cnpj else []
            },
            "Description": {
                "type": "rich_text",
                "rich_text": [{
                    "type": "text",
                    "text": {"content": self.description}
                }] if self.description else []
            }
        }
