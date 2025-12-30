import streamlit as st
from streamlit_chat import *
from chat3 import save_chat, summarize_and_meta
from rag_app import answer_query

img1="https://imgs.search.brave.com/pWwhW0HerlZ2C1HHMnEiRrVIU76w2o8CLiXILkxMedc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pLnBp/bmltZy5jb20vb3Jp/Z2luYWxzL2ZjLzgy/LzViL2ZjODI1YmE4/ODE3NjA5NzMxY2Mz/MzE2NjliZmUzNTc3/LmpwZw"
img2="https://imgs.search.brave.com/wVPMe1LUk2ORYXfAcvjE54bV_c-SgqORRIxtX9tF2GU/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9wbGF5/LWxoLmdvb2dsZXVz/ZXJjb250ZW50LmNv/bS9wcm94eS8wNl94/R0ZmR2xRSGt3YzNN/MXpiVGhyZ1ZfelVL/QzRxWkpfNEtuQmt6/M240elY0eGNtcG5k/RjdxUzQ5TmdLYUJM/a3lMRnpPQkwxZi1K/a3Fvc0d6VG8weUwx/VktuVFhQXzZuNUQ5/bWVPRUh2Ml9YcE9L/X1h3a1o5OD1zMTky/MC13MTkyMC1oMTA4/MA"

def on_input_change():
    user_input = st.session_state.user_input.strip()
    if not user_input:
        return

    # store user message
    st.session_state.past.append(user_input)

    # RAG call
    try:
        answer = answer_query(user_input)
    except Exception as e:
        answer = f"RAG error: {e}"

    st.session_state.generated.append({
        "type": "rag",
        "data": answer
    })

    # Clear the input box after sending
    st.session_state.user_input = ""

def on_btn_click():
    """Handles clearing and saving the chat history"""
    try:
        email = getattr(st, "user", None)
        if hasattr(email, "email"):
            email_val = email.email
        else:
            email_val = st.session_state.get("email") or "unknown@example.com"

        user_messages = list(st.session_state.get("past", []))
        llm_responses = [g.get("data") if isinstance(g, dict) else g for g in st.session_state.get("generated", [])]

        # skip saving empty chats (handled in save_chat)
        # produce summary + metadata using a different model (e.g. mistral)
        summary, metadata = summarize_and_meta(user_messages, model_name="mistral")

        save_chat(email_val, user_messages, llm_responses, title=None, metadata=metadata, summary=summary)
        st.toast("Chat Saved Successfully!")
    except Exception as e:
        st.warning(f"Failed to save chat before clearing: {e}")

    st.session_state.past.clear()
    st.session_state.generated.clear()

def render():
    # Initialize session state
    st.session_state.setdefault("past", [])
    st.session_state.setdefault("generated", [])

    # 1. Chat Display Area
    chat_placeholder = st.container()

    with chat_placeholder:
        if len(st.session_state.past) == 0:
            st.title("Hi! How can I help you today?", text_alignment='center')

        for i in range(len(st.session_state.generated)):
            message(
                st.session_state.past[i],
                is_user=True,
                logo=img1,
                key=f"{i}_user"
            )
            message(
                st.session_state.generated[i]["data"],
                key=f"{i}_bot",
                allow_html=True,
                logo=img2,
                is_table=True if st.session_state.generated[i]["type"] == "table" else False
            )

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
            if len(st.session_state.past) > 0:
                st.button("Clear chat", on_click=on_btn_click)
