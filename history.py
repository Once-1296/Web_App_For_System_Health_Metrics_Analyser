# To revoke the history part.
import streamlit as st
from streamlit_chat import *
from streamlit_option_menu import option_menu

def render():
    titles = [chat["title"] for chat in st.session_state.chat_id.values()]
    titles = titles[::-1]
    selected = option_menu(
        None,
        titles,
        icons = len(titles)*["chat-dots"],
        orientation="vertical",
        default_index=0,
        styles={
            "container": {
                "padding": "0!important", 
                "background-color": "transparent"
            },
            "icon": {
                "font-size": "16px" # Slightly smaller to match compact look
            }, 
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "5px", # Small margin between items
                "--hover-color": "#e66c38"
            },
            "nav-link-selected": {
                "background-color": "#e66c38", # Added background color for clearer selection
                "color": "white"
            },
        }
    )
    pass