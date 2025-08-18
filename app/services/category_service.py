import streamlit as st

from typing import Dict, Any, Optional

from models import Category
from core.config import get_notion_client


def create_category_on_notion(category: Category) -> Optional[Dict[str, Any]]:
    """Create a new category in Notion database."""
    try:
        notion_client = get_notion_client()
        response = notion_client.pages.create(
            parent={"database_id": category.database_id},
            properties=category.get_notion_json(),
            icon=category.get_icon()
        )
        st.toast(f"Category '{category.name}' created successfully!", icon="✅")
        return response
    
    except Exception as e:
        st.toast(f"Error creating category in Notion: {e}", icon="❌")
        return None
