import streamlit as st
import src.Pages.auth as auth
from src.Utils.chat_backend import load_past_chats
import requests
from io import BytesIO

st.set_page_config(
    page_title="SysPy",
    layout="centered",
    initial_sidebar_state="auto",
)

# auth checkup
if not st.user.is_logged_in:
    auth.render()
    st.stop()

# Load past chats if new session
if not "current_chat_id" in st.session_state:
    load_past_chats(st.user.get("email", ""))
    
if "switch_page_from_history" not in st.session_state:
    st.session_state.setdefault("switch_page_from_history",False)

# Here will be a new navigation sidebar 
#     1. Dashboard, 
#     2. Chat, 
#     3. History
#     4. Logout

picture = st.user.get("picture")

if picture:
    try:
        r = requests.get(picture, timeout=5)
        if r.ok:
            st.logo(BytesIO(r.content), size="large")
    except Exception:
        pass

dashboard_page = st.Page(
    page="src/Pages/dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=True
)

chat_page = st.Page(
    page="src/Pages/chat_frontend.py",
    title="Chat",
    icon=":material/chat:"
)

history_page = st.Page(
    page="src/Pages/chat_history.py",
    title="History",
    icon=":material/history:"
)

loc_app_doc_page = st.Page(
    page="src/Pages/loc_app_doc.py",
    title="Local App Guide",
    icon=":material/download:"
)

reports_page = st.Page(
    page="src/Pages/reports.py",
    title="Reports",
    icon=":material/insert_chart:"
)

pg = st.navigation([dashboard_page, chat_page, history_page, reports_page, loc_app_doc_page])
pg.run()