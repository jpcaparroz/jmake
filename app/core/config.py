from functools import lru_cache
from notion_client import Client
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration, loaded from environment or .env"""
    NOTION_API_KEY: str

    DB_PRODUCT_ID: str | None = None
    DB_CATEGORY_ID: str | None = None
    DB_CUSTOMER_ID: str | None = None
    DB_SUPPLIER_ID: str | None = None
    DB_STORE_ID: str | None = None
    DB_ORDER_ID: str | None = None
    DB_ORDER_ITEM_ID: str | None = None
    DB_COST_ID: str | None = None
    DB_STOCK_ID: str | None = None
    DB_STOCK_MOVEMENT_ID: str | None = None

    DEFAULT_TIMEZONE: str = "America/Sao_Paulo"
    DEFAULT_DATE_FORMAT: str = "%d/%m/%Y %H:%M:%S"

    ST_DATE_FORMAT: str = "DD/MM/YYYY"
    ST_ORDER_NUMBER_FORMAT: str = "R$ %.2f"

    ST_PRODUCT_PRICE_NUMBER_FORMAT: str = "R$ %.2f"
    ST_PRODUCT_CREATED_TIME_FORMAT: str = "dddd, MMMM Do YYYY, kk:mm:ss"
    ST_PRODUCT_LAST_EDITED_TIME_FORMAT: str = "dddd, MMMM Do YYYY, kk:mm:ss"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Load settings once and cache them"""
    return Settings()


@lru_cache
def get_notion_client() -> Client:
    """Singleton Notion client"""
    settings = get_settings()
    return Client(auth=settings.NOTION_API_KEY)


def get_db_map() -> dict[str, str | None]:
    """Helper to access DB IDs as dict"""
    s = get_settings()
    return {
        "product": s.DB_PRODUCT_ID,
        "category": s.DB_CATEGORY_ID,
        "customer": s.DB_CUSTOMER_ID,
        "supplier": s.DB_SUPPLIER_ID,
        "store": s.DB_STORE_ID,
        "order": s.DB_ORDER_ID,
        "order_item": s.DB_ORDER_ITEM_ID,
        "cost": s.DB_COST_ID,
        "stock": s.DB_STOCK_ID,
        "stock_movement": s.DB_STOCK_MOVEMENT_ID,
    }
