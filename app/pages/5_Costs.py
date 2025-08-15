import streamlit as st
from datetime import datetime
from services.notion import DB, list_pages, create_page, _date_iso, _relation, _number, _select, _rich

st.title('Costs')
products = list_pages(DB['products']) if DB['products'] else []
product_map = { p['properties']['Product']['title'][0]['plain_text']: p['id'] for p in products if p['properties'].get('Product',{}).get('title') }

with st.form('new_cost'):
    date_str = st.date_input('Date', value=datetime.today()).isoformat()
    ctype = st.selectbox('Cost Type', options=['Material','Energy','Packaging','Maintenance','Other'])
    value = st.number_input('Value', min_value=0.0, value=0.0)
    prod_name = st.selectbox('Product (optional)', options=['— None —'] + list(product_map.keys()))
    notes = st.text_area('Notes', '')
    go = st.form_submit_button('Create cost')
    if go:
        props = {
            'Date': _date_iso(date_str),
            'Cost Type': _select(ctype),
            'Value': _number(value),
            'Notes': _rich(notes),
        }
        if prod_name != '— None —':
            props['Product'] = _relation(product_map[prod_name])
        create_page(DB['costs'], props)
        st.success('Cost created!')

st.divider()
st.subheader('Recent costs')
for c in list_pages(DB['costs']):
    ctype = c['properties'].get('Cost Type',{}).get('select',{}).get('name','—')
    val = c['properties'].get('Value',{}).get('number') or 0
    st.write(f"{ctype}: R$ {val:.2f}")
