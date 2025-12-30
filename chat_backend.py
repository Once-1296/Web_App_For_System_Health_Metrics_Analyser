import streamlit as st
from supabase import create_client
from supabase import Client
from supabase_config import url, key

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
            chat_id : {"user_messages":data[0]["user_messages"] , "llm_responses" : data[0]["llm_responses"], "title":data[0]["title"]}
        })
    st.session_state.chat_id.update({
        max(chat_ids)+1:{"user_messages":[],"llm_responses":[],"title":""}
    })
    st.session_state.setdefault("current_chat_id",max(chat_ids)+1)
    
    