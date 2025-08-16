import pytz
from datetime import datetime

from notion_client import Client

from core.config import get_settings


settings = get_settings()


def get_database_data(notion: Client, database_id: str):
    results = []
    query = notion.databases.query(database_id=database_id)
    results.extend(query.get("results", []))
    return results

def extract_properties_to_easy_dict(page: dict) -> dict:
    """Extract properties from a Notion page object to an easy dict."""
    props = {}
    properties = page.get("properties", {})

    for key, val in properties.items():
        val_type = val.get("type")

        handlers = {
            "unique_id": lambda v: f"{v['unique_id']['prefix']}-{v['unique_id']['number']}" if v.get("unique_id") else None,
            "title": lambda v: v["title"][0]["plain_text"] if v.get("title") else "",
            "rich_text": lambda v: v["rich_text"][0]["plain_text"] if v.get("rich_text") else "",
            "number": lambda v: v.get("number"),
            "date": lambda v: v["date"]["start"] if v.get("date") else None,
            "select": lambda v: v["select"]["name"] if v.get("select") else None,
            "phone_number": lambda v: v.get("phone_number"),
            "url": lambda v: v.get("url"),
            "email": lambda v: v.get("email"),
            "formula": lambda v: v["formula"]["number"] if v.get("formula") else 0,
            "relation": lambda v: [r["id"] for r in v.get("relation", [])],
            "created_by": lambda v: v.get("created_by"),
            "last_edited_time": lambda v: format_datetime(v.get("last_edited_time")),
            "created_time": lambda v: format_datetime(v.get("created_time")),
        }

        if val_type == "rollup":
            props[key] = handle_rollup(val)
        elif val_type in handlers:
            props[key] = handlers[val_type](val)
        else:
            props[key] = None

    return props

def handle_rollup(val: dict):
    """Handle Notion rollup fields."""
    rollup_type = val.get("rollup", {}).get("type")
    rollup_data = val.get("rollup", {})

    if rollup_type == "array":
        array_data = rollup_data.get("array", [])
        if not array_data:
            return 0
        first = array_data[0]
        if first.get("type") == "formula":
            return first["formula"].get("number", 0)
        elif first.get("type") == "number":
            return first.get("number", 0)
    elif rollup_type == "number":
        return rollup_data.get("number", 0)

    return 0

def convert_time_zone(date: datetime) -> datetime:
    """Convert a datetime object to a different timezone."""
    if not date:
        return None
    return date.astimezone(pytz.timezone(settings.DEFAULT_TIMEZONE))

def format_datetime(iso_str):
    """Convert ISO datetime string to formatted string."""
    if not iso_str:
        return None
    return convert_time_zone(datetime.fromisoformat(iso_str)).strftime(settings.DEFAULT_DATE_FORMAT)
