from typing import Dict, Any, List, Optional

# from app.models import Category, Product, Customer, Supplier, Store, Order, OrderItem, Stock, StockMovement
from utils.notion_utils import extract_properties_to_easy_dict
from core.config import get_notion_client, get_db_map

notion = get_notion_client()
db = get_db_map()

# ---- Low-level helpers ----
def create_page(db_id: str, properties: Dict[str, Any]) -> dict:
    return notion.pages.create(parent={"database_id": db_id}, properties=properties)


def update_page(page_id: str, properties: Dict[str, Any]) -> dict:
    return notion.pages.update(page_id=page_id, properties=properties)


def find_by_title(db_id: str, title_prop: str, title: str) -> Optional[dict]:
    res = notion.databases.query(database_id=db_id, filter={
        "property": title_prop,
        "title": {"equals": title}
    })
    results = res.get('results', [])
    return results[0] if results else None


def list_pages(db_name: str, page_size: int = 50) -> List[dict]:
    db_id = db.get(db_name)
    if not db_id:
        raise ValueError(f"Database '{db_name}' not found in configuration.")
    res = notion.databases.query(database_id=db_id, page_size=page_size)
    return res.get('results', [])


def get_database_count(db_name: str) -> int:
    return len(list_pages(db_name))


def get_page_name_by_id(page_id: str) -> str | None:
    """Fetch a page by its ID and return its name."""
    try:
        page = notion.pages.retrieve(page_id=page_id)
        props = extract_properties_to_easy_dict(page)
        return props.get("title")
    except Exception as e:
        print(f"Error fetching page {page_id}:{e}")
        return None
