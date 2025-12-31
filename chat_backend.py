import streamlit as st
import json
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from supabase import create_client
from supabase import Client
from supabase_config import url, key
from langchain_ollama import ChatOllama
from rag_app import answer_query
from config import OllamaConfig

def _get_supabase_client() -> Client:
    if not url or not key:
        raise RuntimeError("Supabase credentials missing in supabase_config.py")
    return create_client(url, key)

def load_past_chats(email:str):
    st.session_state.setdefault("chat_id",{})
    if email is None:
        return {"error" : "No email given"}
    sb = _get_supabase_client()
    resp = (
        sb.table("user_chat_nums").select("chat_id").eq("email",email).execute()
    )
    st.session_state.setdefault("chat_id",{})
    try:
        chat_ids = [entry["chat_id"] for entry in resp.data]
    except Exception as e:
        chat_ids = []
    for chat_id in chat_ids:
        chat_resp = (sb.table("all_chats").select("*").eq("email",email).eq("chat_id",chat_id).execute())
        data = chat_resp.data
        # print(data)
        # print(type(data[0]))
        st.session_state.chat_id.update({
            chat_id : {"user_messages":data[0]["user_messages"] , "llm_responses" : data[0]["llm_responses"], "title":data[0]["title"],"summary":data[0]["summary"]}
        })
    new_id = max(chat_ids)+1 if len(chat_ids) > 0 else 1
    st.session_state.chat_id.update({
        new_id : {"user_messages":[],"llm_responses":[],"title":"","summary":""}
    })
    st.session_state.setdefault("current_chat_id",new_id)


def update_chat() -> dict:
    if "current_chat_id" not in st.session_state:
        return { "error": "No valid chat id found"}
    try:
        messages = st.session_state.chat_id[st.session_state.current_chat_id]["user_messages"]
        responses = st.session_state.chat_id[st.session_state.current_chat_id]["llm_responses"]
        email = st.user.get("email", "")
        chat_id = st.session_state.current_chat_id
        if len(messages) == 0 or len(responses) == 0 or len(messages) != len(responses):
            return {"warning" : "No messages/responses or unequal number of messages/responses"}
        sb = _get_supabase_client()
        title,summary,metadata = summarize_and_meta(messages,responses)
        if title is None or summary is None or  not metadata:
            return {"error" : "unable to get summary and metadata"}
        st.session_state.chat_id[st.session_state.current_chat_id]["title"] = title
        st.session_state.chat_id[st.session_state.current_chat_id]["summary"] = summary
        payload = {
            "chat_id" : chat_id,
            "email" : email,
            "title" : title,
            "user_messages" : messages,
            "llm_responses" : responses,
            "summary" : summary,
            "metadata" : metadata
        }
        resp1 = ( sb.table("all_chats").upsert(payload).execute() )
        resp2 = ( sb.table("user_chat_nums").upsert({"email":email,"chat_id":chat_id}).execute() )
        if "error" in resp1:
            return {"error" : resp1.error}
        if "error" in resp2:
            return {"error" : resp2.error}
        return {"message" :  "Success!"}
    except Exception as e:
        return {"error" : e}


def summarize_and_meta(messages: List[str], responses:List[str], model_name: Optional[str] = None) -> Tuple[Optional[str],Optional[str], Dict[str, Any]]:
    """
    Produce a short summary and lightweight metadata for the conversation.
    Uses an Ollama chat model (you can pass a mistral model name).
    Returns (summary_text, metadata_dict).
    """
    if not messages or not responses:
        return None,None, {}
    if len(messages) != len(responses):
        return None, None, {}
    model_name = model_name or "mistral"  # override if needed
    fallback_title = (
        messages[0][:120]
        if messages[0]
        else f"chat-{datetime.utcnow().isoformat()}"
    )
    convo = "\n\n" + "\n\n".join(
        f"User : {m}\nLLM: {r}"
        for m, r in zip(messages, responses)
    ) + "\n\n"
    try:
        model = ChatOllama(
            model=model_name,
            base_url=OllamaConfig.BASE_URL,
            temperature=0.0
        )
        prompt = (
            "You are a concise summarizer that can explain the basic flow, points and aims of a user to llm conversation.\n"
            " Given the conversation, produce a JSON object with keys:\n"
            "  title -> short description of chat\n"
            "  summary -> summary whose length is the minimum between half of approximate length of chat and 300 words\n"
            "  tags -> list of short topic tags. Produce between 2 to 30 tags according to relevancy. \n\n"
            f"Conversation:\n{convo}\n\nRespond ONLY with valid JSON."
        )
        resp = model.invoke(prompt)
        content = getattr(resp, "content", resp)
        # try parse as JSON
        parsed = {}
        try:
            parsed = json.loads(content)

            summary = parsed.get("summary") if isinstance(parsed, dict) else content

            if isinstance(parsed, dict):
                title = parsed.get("title", fallback_title)
            else:
                title = fallback_title
            
            tags = parsed.get("tags") if isinstance(parsed, dict) else []

            metadata = {"tags": tags, "generated_by": model_name}
            return title, summary, metadata
        except Exception:
            # fallback: use raw model output as summary
            return fallback_title,content.strip(), {"generated_by": model_name}
    except Exception:
        # last-resort lightweight summary
        return fallback_title, convo[:400], {"generated_by": "fallback", "length": len(messages)}


def on_input_change():
    """Handles updating the chat to supabase when new messages are sent"""
    user_input = st.session_state.user_input.strip()
    if not user_input:
        # print("No message")
        return

    # store user message
    st.session_state.chat_id[st.session_state.current_chat_id]["user_messages"].append(user_input)
    # print(user_input)
    # RAG call
    try:
        answer = answer_query(user_input)
    except Exception as e:
        answer = f"RAG error: {e}"
    
    st.session_state.chat_id[st.session_state.current_chat_id]["llm_responses"].append(answer)
    response = update_chat()
    # if "error" in response:
    #     print(f"error : {response["error"]}")
    # elif "warning" in response:
    #     print(f"warning : {response["warning"]}")
    # else:
    #     print(f"Success !")
    # Clear the input box after sending
    st.session_state.user_input = ""

def on_btn_click():
    """Handles clearing the chat to get an empty chat"""
    try:
        email = getattr(st, "user", None)
        if hasattr(email, "email"):
            email_val = email.email
        else:
            email_val = st.session_state.get("email") or "unknown@example.com"

        user_messages = list(st.session_state.chat_id[st.session_state.current_chat_id].get("user_messages", []))
        llm_responses = list(st.session_state.chat_id[st.session_state.current_chat_id].get("llm_responses", []))

    except Exception as e:
        st.warning(f"Failed to save chat before clearing: {e}")

    last_id = max(st.session_state.chat_id)
    if len(st.session_state.chat_id[last_id]["user_messages"]) == 0:
        st.session_state.current_chat_id = last_id
    else:
        st.session_state.current_chat_id = last_id + 1
        st.session_state.chat_id.update({
            st.session_state.current_chat_id : {"user_messages":[],"llm_responses":[],"title":"","summary":""}
        })

    
    