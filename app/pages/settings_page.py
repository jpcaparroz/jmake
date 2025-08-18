import streamlit as st
from core.config import get_notion_client, get_db_map


st.set_page_config(page_title='Settings', page_icon='⚙️', layout='centered')
st.title('Settings')

st.write('Loaded Database IDs:')
st.dataframe(get_db_map(), column_config={"": "Database Name", "value": "Database ID"})

if st.button('Test Notion connection'):
    try:
        notion_client = get_notion_client()
        notion_client.search(query='')
        st.success('Notion API reachable!')
        st.balloons()
    except Exception as e:
        st.error(f'Error: {e}')
