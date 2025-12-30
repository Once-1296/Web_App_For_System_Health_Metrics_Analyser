import streamlit as st
from streamlit_option_menu import option_menu
import auth
import dashboard
import chat2

# auth checkup
if not st.user.is_logged_in:
    auth.render()
    st.stop()

# Here will be a new navigation sidebar 
#     1. Dashboard, 
#     2. Chat, 
#     3. History
#     4. Logout
# 
with st.sidebar:
    selected = option_menu(
        None,
        ["Dashboard", "Chat", "History", "Logout"],
        icons=["speedometer2", "chat-dots", "clock-history", "box-arrow-right"],
        orientation="vertical",
        default_index=0,
        styles={
            "container": {
                "padding": "0!important",
                "margin": "10px"
            },
            "icon": {
                "font-size": "20px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "4px 0",
                "--hover-color": "#e66c38"
            },
            "nav-link-selected": {
                "color": "white"
            },
        }
    )

# page routing
if selected == "Dashboard":
    dashboard.render()

elif selected == "Chat":
    chat2.render()

elif selected == "Logout":
    st.warning("Are you sure you want to logout?")
    if st.button("Yes, Logout"):
        st.logout()
            