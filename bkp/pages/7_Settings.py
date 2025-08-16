import streamlit as st
from app.services.notion_service import DB, client

st.title('Settings')

st.write('Loaded Database IDs:')
for k, v in DB.items():
    st.write(f"- {k}: {v}")

if st.button('Test Notion connection'):
    try:
        client.search(query='')
        st.success('Notion API reachable!')
    except Exception as e:
        st.error(f'Error: {e}')