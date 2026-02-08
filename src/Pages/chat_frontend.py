import streamlit as st
from streamlit_chat import message
from src.Utils.chat_backend import update_chat, on_input_change, on_btn_click

img1="https://imgs.search.brave.com/pWwhW0HerlZ2C1HHMnEiRrVIU76w2o8CLiXILkxMedc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pLnBp/bmltZy5jb20vb3Jp/Z2luYWxzL2ZjLzgy/LzViL2ZjODI1YmE4/ODE3NjA5NzMxY2Mz/MzE2NjliZmUzNTc3/LmpwZw"
img2="https://imgs.search.brave.com/wVPMe1LUk2ORYXfAcvjE54bV_c-SgqORRIxtX9tF2GU/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9wbGF5/LWxoLmdvb2dsZXVz/ZXJjb250ZW50LmNv/bS9wcm94eS8wNl94/R0ZmR2xRSGt3YzNN/MXpiVGhyZ1ZfelVL/QzRxWkpfNEtuQmt6/M240elY0eGNtcG5k/RjdxUzQ5TmdLYUJM/a3lMRnpPQkwxZi1K/a3Fvc0d6VG8weUwx/VktuVFhQXzZuNUQ5/bWVPRUh2Ml9YcE9L/X1h3a1o5OD1zMTky/MC13MTkyMC1oMTA4/MA"

st.set_page_config(
    layout="centered",
    initial_sidebar_state="auto",
)

def render():
    # Initialize session state
    if "current_chat_id" not in st.session_state:
        st.session_state.setdefault("current_chat_id",1)
        if not "chat_id" in st.session_state:
            st.session_state.setdefault("chat_id",{})
        st.session_state.chat_id.update({
            1 :{"user_messages":[],"llm_responses":[],"title":"","summary":""}
        })

    # 1. Chat Display Area
    chat_placeholder = st.container()
    with chat_placeholder:
        if len(st.session_state.chat_id[st.session_state.current_chat_id]["user_messages"]) == 0:
            st.title("Hi! How can I help you today?", text_alignment='center')

        for i in range(len(st.session_state.chat_id[st.session_state.current_chat_id]["user_messages"])):
            message(
                st.session_state.chat_id[st.session_state.current_chat_id]["user_messages"][i],
                is_user=True,
                logo=img1,
                key=f"{i}_user"
            )
            message(
                st.session_state.chat_id[st.session_state.current_chat_id]["llm_responses"][i],
                key=f"{i}_bot",
                allow_html=True,
                logo=img2,
            )

    # 2. Chat Input Area at Bottom
    with st.container():
        st.text_area(
            "User Input:",
            key="user_input",
            height=100,
            placeholder='Ask anything (Shift+Enter for newline)',
            label_visibility="collapsed"
        )

        col1, _, col2 = st.columns([1, 4, 1])

        with col1:
            st.button("Send", on_click=on_input_change)

        with col2:
            if len(st.session_state.chat_id[st.session_state.current_chat_id]["user_messages"]) > 0:
                st.button("Clear chat", on_click=on_btn_click)


if __name__ == "__main__":
    render()
