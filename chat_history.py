# To revoke the history part.
import streamlit as st
from streamlit_chat import *
from streamlit_option_menu import option_menu

def render():
    details = [ (chat_id,chat["title"]) for chat_id,chat in st.session_state.chat_id.items()]
    details = details[::-1]
    default_index = next(
        i for i, (cid, _) in enumerate(details)
        if cid == st.session_state.current_chat_id
    )

    titles = [title for _, title in details]
    labels = [
        f"{title} ⟨{i}⟩"
        for i, (_, title) in enumerate(details)
    ]
    selected_label = option_menu(
        None,
        labels,
        icons = len(titles)*["chat-dots"],
        orientation="vertical",
        default_index=default_index,
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
    selected_index = labels.index(selected_label)
    selected_chat_id = details[selected_index][0]
    # print(selected_chat_id)
    st.session_state.current_chat_id = selected_chat_id
    pass