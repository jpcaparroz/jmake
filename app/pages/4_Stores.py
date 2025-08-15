import streamlit as st
from services.notion import DB, create_page, list_pages, _title, _select

st.title('Stores')
with st.form('new_store'):
    name = st.text_input('Store name')
    type_ = st.selectbox('Type', options=['Marketplace','Online','Physical'])
    website = st.text_input('Website')
    go = st.form_submit_button('Create')
    if go and name:
        props = {
            'Store': _title(name),
            'Type': _select(type_),
            'Website': {"url": website or None},
        }
        create_page(DB['stores'], props)
        st.success('Store created!')

st.divider()
st.subheader('All stores')
for s in list_pages(DB['stores']):
    n = s['properties']['Store']['title'][0]['plain_text'] if s['properties'].get('Store',{}).get('title') else '—'
    st.write(n)