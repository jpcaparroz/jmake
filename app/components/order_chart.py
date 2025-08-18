import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from services.notion_service import list_pages
from models import Order


@st.cache_data
def load_orders() -> pd.DataFrame:
    """Load notion orders into a DataFrame"""
    raw_orders = list_pages("order", page_size=100)
    orders = [Order.from_dict(o).to_dict() for o in raw_orders]

    df = pd.DataFrame(orders)

    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df["Total Value"] = pd.to_numeric(df["Total Value"], errors="coerce").fillna(0)

    return df


def group_orders(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Group orders by selected period"""
    if period == "Weekly":
        df_grouped = df.groupby(df["Date"].dt.to_period("W"))["Total Value"].sum().reset_index()
        df_grouped["Date"] = df_grouped["Date"].dt.start_time
    elif period == "Monthly":
        df_grouped = df.groupby(df["Date"].dt.to_period("M"))["Total Value"].sum().reset_index()
        df_grouped["Date"] = df_grouped["Date"].dt.to_timestamp()
    else:
        df_grouped = df.groupby(df["Date"].dt.to_period("Y"))["Total Value"].sum().reset_index()
        df_grouped["Date"] = df_grouped["Date"].dt.to_timestamp()

    return df_grouped


def show_orders_chart(streamlit: st):
    streamlit.subheader("Orders by Period")

    period = streamlit.segmented_control(
        label="Filter", 
        options=["Weekly", "Monthly", "Yearly"], 
        selection_mode='single',
        default="Weekly"
    )

    df = load_orders()
    if df.empty:
        st.warning("No orders found in Notion.")
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

    streamlit.altair_chart(chart, use_container_width=True)
