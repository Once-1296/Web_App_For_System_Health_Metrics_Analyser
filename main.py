import streamlit as st
import auth
import dashboard
import chat

if not st.user.is_logged_in:
    auth.render()
else:
    # Navigation
    page = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Chat"]
    )

    if page == "Dashboard":
        dashboard.render()
    elif page == "Chat":
        chat.render()
