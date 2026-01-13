# rag_app.py
import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.Utils.head_query import gather_context
from src.Utils.rag_config import llm


PROMPT = ChatPromptTemplate.from_template(
    """
You are a Linux and Windows system troubleshooting assistant.
Answer using the provided documentation context as well as previous messages of user (may be empty for a new chat).
Be precise and practical.
If the answer is unknown, say so.

Context:
{context}

Previous Messages:\n
Summary:\n
{summary}
Recent Messages:\n
{recent_messages}

Question:
{question}
"""
)

def format_docs(docs):
    return "\n\n".join(
        f"[{d.metadata.get('domain')}/{d.metadata.get('topic')}]\n{d.page_content}"
        for d in docs
    )

def answer_query(query: str):
    contexts = gather_context(query)

    main_context = format_docs(contexts["main"])

    chain = PROMPT | llm | StrOutputParser()

    try:   
        summary = st.session_state.chat_id[st.session_state.current_chat_id]["summary"]
        messages = st.session_state.chat_id[st.session_state.current_chat_id]["user_messages"][-5:]
        responses = st.session_state.chat_id[st.session_state.current_chat_id]["llm_responses"][-5:]
        if len(messages) == 0:
            summary = ""
            recent_messages = ""
        else:
            recent_messages = "\n\n" + "\n\n".join(
                f"User : {m}\nLLM: {r}"
                for m, r in zip(messages, responses)
            ) + "\n\n"
    except Exception as e:
        summary = ""
        recent_messages =""

    return chain.invoke(
        {
            "context": main_context,
            "question": query,
            "summary": summary,
            "recent_messages": recent_messages,
        }
    )
