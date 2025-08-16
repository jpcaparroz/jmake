import streamlit
import pandas as pd
import altair as alt
from datetime import datetime

from services.notion_service import list_pages
from models import Order


@streamlit.cache_data
def load_orders(st: streamlit) -> pd.DataFrame:
    """Load notion orders into a DataFrame"""
    raw_orders = list_pages("order", page_size=100)  # pode ajustar
    orders = [Order.from_dict(o).to_dict() for o in raw_orders]

    df = pd.DataFrame(orders)

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df["Total Value"] = pd.to_numeric(df["Total Value"], errors="coerce").fillna(0)

    return df


def group_orders(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Group orders by selected period"""
    if period == "Semana":
        df_grouped = df.groupby(df["Date"].dt.to_period("W"))["Total Value"].sum().reset_index()
        df_grouped["Date"] = df_grouped["Date"].dt.start_time
    elif period == "Mês":
        df_grouped = df.groupby(df["Date"].dt.to_period("M"))["Total Value"].sum().reset_index()
        df_grouped["Date"] = df_grouped["Date"].dt.to_timestamp()
    else:  # Ano
        df_grouped = df.groupby(df["Date"].dt.to_period("Y"))["Total Value"].sum().reset_index()
        df_grouped["Date"] = df_grouped["Date"].dt.to_timestamp()

    return df_grouped


def show_orders_chart(st: streamlit):
    st.subheader("📊 Pedidos ao longo do tempo")

    period = st.selectbox("Agrupar por:", ["Semana", "Mês", "Ano"], index=1)

    df = load_orders(st)

    if df.empty:
        st.warning("Nenhum pedido encontrado no Notion.")
        return

    df_grouped = group_orders(df, period)

    chart = (
        alt.Chart(df_grouped)
        .mark_line(point=True)
        .encode(
            x="Date:T",
            y="Total Value:Q",
            tooltip=["Date:T", "Total Value:Q"]
        )
        .properties(width="container", height=400)
    )

    st.altair_chart(chart, use_container_width=True)
