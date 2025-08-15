import pytz
from datetime import datetime

from notion_client import Client

from app.core.config import DEFAULT_DATE_FORMAT, DEFAULT_TIMEZONE


def get_database_data(notion: Client, database_id: str):
    results = []
    query = notion.databases.query(database_id=database_id)
    results.extend(query.get("results", []))
    return results

def extract_properties_to_easy_dict(page: dict) -> dict:
    """Extract properties from a Notion page object to a easy dict."""
    props = {}
    for key, val in page["properties"].items():
        if val["type"] == "unique_id":
            props[key] = f"{val['unique_id']['prefix']}-{str(val['unique_id']['number'])}" if val["unique_id"] else None
        elif val["type"] == "title":
            props[key] = val["title"][0]["plain_text"] if val["title"] else ""
        elif val["type"] == "rich_text":
            props[key] = val["rich_text"][0]["plain_text"] if val["rich_text"] else ""
        elif val["type"] == "number":
            props[key] = val["number"]
        elif val["type"] == "date":
            props[key] = val["date"]["start"] if val["date"] else None
        elif val["type"] == "select":
            props[key] = val["select"]["name"] if val["select"] else None
        elif val["type"] == "phone_number":
            props[key] = val["phone_number"] if val["phone_number"] else None
        elif val["type"] == "url":
            props[key] = val["url"] if val["url"] else None
        elif val["type"] == "email":
            props[key] = val["email"] if val["email"] else None
        elif val["type"] == "relation":
            props[key] = [r["id"] for r in val["relation"]]
        elif val["type"] == "rollup":
            props[key] = val["rollup"]["array"][0]['formula']['number'] if val["rollup"] else None
        elif val["type"] == "created_by":
            props[key] = val["created_by"] if val["created_by"] else None
        elif val["type"] == "last_edited_time":
            props[key] = convert_time_zone(datetime.fromisoformat(val["last_edited_time"])).strftime(DEFAULT_DATE_FORMAT) if val["last_edited_time"] else None
        elif val["type"] == "created_time":
            props[key] = convert_time_zone(datetime.fromisoformat(val["created_time"])).strftime(DEFAULT_DATE_FORMAT) if val["created_time"] else None
        else:
            props[key] = None

    return props

def convert_time_zone(date: datetime) -> datetime:
    """Convert a datetime object to a different timezone."""
    if not date:
        return None
    return date.astimezone(pytz.timezone(DEFAULT_TIMEZONE))
