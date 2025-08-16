import streamlit as st
from app.services.notion_service import DB, create_page, list_pages, _title

st.title('Customers')
with st.form('new_cust'):
    name = st.text_input('Customer name')
    phone = st.text_input('Phone')
    email = st.text_input('Email')
    address = st.text_area('Address')
    go = st.form_submit_button('Create')
    if go and name:
        props = {
            'Customer': _title(name),
            'Phone': {"phone_number": phone or None},
            'Email': {"email": email or None},
            'Address': {"rich_text": [{"text": {"content": address or ''}}]},
        }
        create_page(DB['customers'], props)
        st.success('Customer created!')

st.divider()
st.subheader('All customers')
for c in list_pages(DB['customers']):
    n = c['properties']['Customer']['title'][0]['plain_text'] if c['properties'].get('Customer',{}).get('title') else '—'
    st.write(n)
