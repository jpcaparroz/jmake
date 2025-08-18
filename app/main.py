import streamlit as st

# Main page configs
st.logo('./app/image/jmake-logo.svg', size='medium')

# Navigation pages
pages = {
    "Home": [st.Page("pages/home.py", title="🏡 Home", default=True)],
    "Configurations": [st.Page("pages/settings_page.py", title="⚙️ Settings")],
}

nav = st.navigation(pages, position="top")
nav.run()
