from typing import Dict, Any, Optional

import streamlit as st

from models import Order
from core.config import get_notion_client


def create_order_on_notion(order: Order) -> Optional[Dict[str, Any]]:
    """Create a new order in Notion database."""
    try:
        notion_client = get_notion_client()
        response = notion_client.pages.create(
            parent={"database_id": order.database_id},
            properties=order.get_notion_json(),
            icon=order.get_icon()
        )

        st.toast(f"Pedido '{order.name}' criado com sucesso!", icon="✅")
        return response
    except Exception as e:
        st.toast(f"Erro ao criar pedido: {e}", icon="❌")
        return None
