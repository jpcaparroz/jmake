from typing import Dict, Any, Optional

import streamlit as st

from models import Product
from core.config import get_notion_client


def create_product_on_notion(product: Product) -> Optional[Dict[str, Any]]:
    """Create a new product in Notion database."""
    try:
        notion_client = get_notion_client()
        response = notion_client.pages.create(
            parent={"database_id": product.database_id},
            properties=product.get_notion_json(),
            icon=product.get_icon()
        )

        st.toast(f"Produto '{product.name}' criado com sucesso!", icon="✅")
        return response
    except Exception as e:
        st.toast(f"Erro ao criar produto: {e}", icon="❌")
        return None
