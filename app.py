import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Configure the Streamlit page layout
st.set_page_config(
    page_title="Asset Sync – Warehouse Device Monitoring",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS to hide Streamlit boilerplate and make iframe full-viewport
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            width: 100% !important;
            border: none !important;
            min-height: 100vh;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load the interactive HTML dashboard
html_file = Path(__file__).parent / "index.html"

if html_file.exists():
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    components.html(html_content, height=1000, scrolling=True)
else:
    st.error("index.html not found! Ensure index.html is in the same directory as app.py.")
