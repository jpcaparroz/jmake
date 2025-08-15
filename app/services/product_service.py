from typing import Dict, Any, List, Optional

from app.models import Product
from app.core.config import notion_client, DB


def get_product_count() -> int:
    pages = notion_client.databases.query(database_id=DB['product'], page_size=100)

    

    return Product.objects.count()
