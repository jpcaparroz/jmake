import time
import streamlit as st

from services.notion_service import list_pages
from services.category_service import create_category_on_notion
from services.product_service import create_product_on_notion
from models import Product, Category


def create_product_dialog_state(state: bool = True):
    st.session_state["create_product_dialog_open"] = state

def edit_product_dialog_state(state: bool = True):
    st.session_state["edit_product_dialog_open"] = state


# --- Helpers ---
def fetch_categories():
    try:
        categories = [Category.from_dict(c) for c in list_pages("category", page_size=100)]
        options = [c.name for c in categories]
    except Exception as e:
        st.error(f"Error fetching categories: {e}")
        categories, options = [], []
    return categories, options


def fetch_products():
    try:
        products = [Product.from_dict(p) for p in list_pages("product", page_size=100)]
        options = [f"{p.name} (ID: {p.product_id})" for p in products]
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        products, options = [], []
    return products, options


# --- Dialogs ---
@st.dialog(title="Create New Product", width="large", on_dismiss=lambda: create_product_dialog_state(False))
def create_product_dialog() -> None:
    categories, category_options = fetch_categories()

    st.subheader("Required Inputs")
    name = st.text_input("Name")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    category = st.selectbox(
        label="Category",
        options=category_options,
        accept_new_options=True,
        placeholder="Select a category"
    )

    st.subheader("Optional Inputs")
    print_time = st.number_input("Print Time", min_value=0.0, format="%.2f")

    if st.button("Create Product", type="primary", use_container_width=True):
        # Create category if not exists
        if category not in category_options:
            category_id = create_category_on_notion(Category(name=category)).get("id")
        else:
            category_id = next(c.notion_id for c in categories if c.name == category)

        new_product = Product(
            name=name,
            price=price,
            print_time=print_time or 0,
            category=[category_id]
        )

        with st.spinner("Creating product..."):
            create_product_on_notion(new_product)
            time.sleep(1)

        create_product_dialog_state(False)
        st.rerun()


@st.dialog(title="Edit Product", width="large", on_dismiss=lambda: edit_product_dialog_state(False))
def edit_product_dialog() -> None:
    categories, category_options = fetch_categories()
    products, product_options = fetch_products()

    st.subheader("Required Inputs")

    # --- Select the product to edit ---
    selected_index = st.selectbox(
        label="Product",
        options=list(range(len(product_options))),
        format_func=lambda i: product_options[i],
        placeholder="Select a product to edit",
        accept_new_options=False,
    )

    # Get the actual Product object
    selected_product_obj = products[selected_index]

    # --- Pre-fill inputs with product data ---
    price = st.number_input(
        "Price",
        min_value=0.0,
        format="%.2f",
        value=float(selected_product_obj.price)
    )

    # Pre-fill category (selectbox requires index of the option)
    try:
        category_index = category_options.index(selected_product_obj.category)  # Assuming category_name exists
    except ValueError:
        # If category no longer exists
        category_options.append(selected_product_obj.category)
        category_index = len(category_options) - 1

    category = st.selectbox(
        label="Category",
        options=category_options,
        index=category_index,
        accept_new_options=True,
        placeholder="Select a category"
    )

    # Optional fields
    print_time = st.number_input(
        "Print Time",
        min_value=0.0,
        format="%.2f",
        value=float(selected_product_obj.print_time)
    )

    # --- Edit button ---
    if st.button("Edit Product", type="primary", use_container_width=True):
        # Create category if it does not exist
        if category not in category_options:
            category_id = create_category_on_notion(Category(name=category)).get("id")
        else:
            category_id = next(c.notion_id for c in categories if c.name == category)

        updated_product = Product(
            name=selected_product_obj.name,
            price=price,
            print_time=print_time,
            category=[category_id]
        )

        with st.spinner("Editing product..."):
            create_product_on_notion(updated_product)
            time.sleep(1)

        edit_product_dialog_state(False)
        st.rerun()