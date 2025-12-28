import streamlit as st
from streamlit_chat import *
from langchain_ollama import ChatOllama
from config import OllamaConfig
from chat3 import save_chat, summarize_and_meta

img1="https://imgs.search.brave.com/pWwhW0HerlZ2C1HHMnEiRrVIU76w2o8CLiXILkxMedc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pLnBp/bmltZy5jb20vb3Jp/Z2luYWxzL2ZjLzgy/LzViL2ZjODI1YmE4/ODE3NjA5NzMxY2Mz/MzE2NjliZmUzNTc3/LmpwZw"
img2="https://imgs.search.brave.com/wVPMe1LUk2ORYXfAcvjE54bV_c-SgqORRIxtX9tF2GU/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9wbGF5/LWxoLmdvb2dsZXVz/ZXJjb250ZW50LmNv/bS9wcm94eS8wNl94/R0ZmR2xRSGt3YzNN/MXpiVGhyZ1ZfelVL/QzRxWkpfNEtuQmt6/M240elY0eGNtcG5k/RjdxUzQ5TmdLYUJM/a3lMRnpPQkwxZi1K/a3Fvc0d6VG8weUwx/VktuVFhQXzZuNUQ5/bWVPRUh2Ml9YcE9L/X1h3a1o5OD1zMTky/MC13MTkyMC1oMTA4/MA"

def render():
    model = ChatOllama(
        model=OllamaConfig.MODEL_NAME,
        base_url=OllamaConfig.BASE_URL,
        temperature=OllamaConfig.TEMPERATURE
    )

    # A dictionary type which saves the chat for user and the bot.
    st.session_state.setdefault("past", [])
    st.session_state.setdefault("generated", [])

    def on_input_change():
        user_input = st.session_state.user_input.strip()
        if not user_input:
            return

        # store user message
        st.session_state.past.append(user_input)
        
        from rag_app import answer_query

        # 🔥 RAG call instead of model.invoke
        try:
            answer = answer_query(user_input)
        except Exception as e:
            answer = f"RAG error: {e}"

        st.session_state.generated.append({
            "type": "rag",
            "data": answer
        })

        st.session_state.user_input = ""

    def on_btn_click():
        # If chat is getting cleared. Making sure that it gets saved somewhere in JSON.
        try:
            email = getattr(st, "user", None)
            # attempt to read email from st.user or session_state
            if hasattr(email, "email"):
                email_val = email.email
            else:
                email_val = st.session_state.get("email") or "unknown@example.com"

            user_messages = list(st.session_state.get("past", []))
            llm_responses = [g.get("data") if isinstance(g, dict) else g for g in st.session_state.get("generated", [])]

            # skip saving empty chats (handled in save_chat)
            # produce summary + metadata using a different model (e.g. mistral)
            summary, metadata = summarize_and_meta(user_messages, model_name="mistral-7b")

            save_chat(email_val, user_messages, llm_responses, title=None, metadata=metadata, summary=summary)
        except Exception as e:
            st.warning(f"Failed to save chat before clearing: {e}")

        st.session_state.past.clear()
        st.session_state.generated.clear()

    #ui
    st.title("Chat")

    chat_placeholder = st.empty()

    with chat_placeholder.container():

        # Welcome message if chat is empty
        if len(st.session_state.past) == 0:
            st.title("Hi! How can I help you today?")

        # Display chat history
        for i in range(len(st.session_state.generated)):
            message(
                st.session_state.past[i],
                is_user=True,
                avatar_style=None,
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

        st.button("Clear chat", on_click=on_btn_click)

    # input.
    st.text_area(
        "User Input (Shift+Enter for newline; click Send to submit):",
        key="user_input",
        height=140
    )
    st.button("Send", on_click=on_input_change)

if __name__ == "__main__":
    render()