import streamlit as st
from streamlit_chat import *
from langchain_ollama import ChatOllama
from config import OllamaConfig

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

        st.session_state.past.append(user_input)

        response = model.invoke(user_input)

        st.session_state.generated.append({
            "type": "normal",
            "data": response.content
        })

        st.session_state.user_input = ""

    def on_btn_click():
        # If chat is getting cleared. Making sure that it gets saved somewhere in JSON.
        
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
    st.text_input(
        "User Input:",
        key="user_input",
        on_change=on_input_change
    )

if __name__ == "__main__":
    render()