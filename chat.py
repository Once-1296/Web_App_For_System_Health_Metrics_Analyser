import streamlit as st
from config import OllamaConfig
from langchain_ollama import ChatOllama

model = ChatOllama(
    model=OllamaConfig.MODEL_NAME,
    base_url=OllamaConfig.BASE_URL,
    temperature=OllamaConfig.TEMPERATURE
)

def render():
    st.title("Chat")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show welcome message ONLY if no chat started
    if len(st.session_state.messages) == 0:
        st.info("Hi! How can I help you today?")

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Store user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate assistant response
        with st.chat_message("assistant"):
            response = model.invoke(user_input)
            assistant_reply = response.content
            st.markdown(assistant_reply)

        # Store assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
