import streamlit as st
import json
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from supabase import create_client
from supabase import Client
from supabase_config import url, key
from langchain_groq import ChatGroq
from rag_app import answer_query
from rag_config import SUMMARY_MODEL, GROQ_API_KEY

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
    # system report count
    st.session_state.setdefault("report_times",[])
    report_timings = (
        sb.table("user_system_reports").select("created_at").eq("user_email",email).execute()
    )
    try:
        st.session_state.report_times = [entry["created_at"] for entry in report_timings.data]
    except Exception as e:
        st.session_state.report_times = []


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


def summarize_and_meta(
    messages: List[str], 
    responses: List[str], 
    model_name: Optional[str] = None
) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
    """
    Produce a short summary and lightweight metadata for the conversation using Groq.
    """
    if not messages or not responses:
        return None, None, {}
    
    if len(messages) != len(responses):
        return None, None, {}

    # Default to the lightweight config model if none provided
    target_model = model_name or SUMMARY_MODEL
    
    fallback_title = (
        messages[0][:50] + "..." if len(messages[0]) > 50 
        else f"chat-{datetime.utcnow().isoformat()}"
    )

    # Format conversation history
    convo = "\n\n".join(
        f"User: {m}\nAI: {r}"
        for m, r in zip(messages, responses)
    )

    try:
        # Initialize Groq Chat Model
        llm = ChatGroq(
            model=target_model,
            api_key=GROQ_API_KEY,
            temperature=0.0  # Keep 0 for consistent JSON
        )

        # Updated Prompt: Optimized for Llama 3 to enforce JSON
        prompt = (
            "System: You are a JSON-only API. You must strictly output valid JSON. No preambles. No markdown blocks.\n"
            "Task: Analyze the following conversation and return a JSON object.\n"
            "Requirements:\n"
            "1. 'title': A short, descriptive title (max 10 words).\n"
            "2. 'summary': A concise summary of the key points.(max 500 words)\n"
            "3. 'tags': A list of 2-10 topic tags.\n\n"
            f"Conversation:\n{convo}\n\n"
            "Output JSON:"
        )

        # Invoke model
        resp = llm.invoke(prompt)
        content = getattr(resp, "content", str(resp))

        # --- Cleaning Llama 3 Output ---
        # Sometimes models wrap JSON in ```json ... ```. We clean that.
        cleaned_content = content.replace("```json", "").replace("```", "").strip()

        # Parse JSON
        parsed = json.loads(cleaned_content)
        
        # Extract fields safely
        title = parsed.get("title", fallback_title)
        summary = parsed.get("summary", "Summary unavailable")
        tags = parsed.get("tags", [])

        metadata = {"tags": tags, "generated_by": target_model}
        return title, summary, metadata

    except json.JSONDecodeError:
        # Fallback: If JSON parsing fails, treat the whole content as the summary
        return fallback_title, content[:500], {"error": "json_parse_fail", "generated_by": target_model}
        
    except Exception as e:
        # Final fallback: If Groq API fails entirely
        print(f"Summarization failed: {e}")
        return fallback_title, convo[:200] + "...", {"error": str(e), "generated_by": "fallback"}


def on_input_change():
    """Handles updating the chat to supabase when new messages are sent"""
    user_input = st.session_state.user_input.strip()
    if not user_input:
        # print("No message")
        return

    # store user message
    # print(user_input)
    # RAG call
    try:
        answer = answer_query(user_input)
    except Exception as e:
        answer = f"RAG error: {e}"
    st.session_state.chat_id[st.session_state.current_chat_id]["user_messages"].append(user_input)
    st.session_state.chat_id[st.session_state.current_chat_id]["llm_responses"].append(answer)
    response = update_chat()
    if "error" in response:
        print(f"error : {response['error']}")
    elif "warning" in response:
        print(f"warning : {response['warning']}")
    else:
        pass
        print(f"Success !")
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

    
    