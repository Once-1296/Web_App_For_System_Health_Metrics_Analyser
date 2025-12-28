from supabase import create_client
from supabase.lib.client_options import ClientOptions  # type: ignore
from supabase import Client
import json
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

from supabase_config import url, key  # uses your existing file
from langchain_ollama import ChatOllama
from config import OllamaConfig

def _get_supabase_client() -> Client:
    if not url or not key:
        raise RuntimeError("Supabase credentials missing in supabase_config.py")
    return create_client(url, key, options=ClientOptions())

def _latest_saved_for(email: str) -> Optional[Dict[str, Any]]:
    sb = _get_supabase_client()
    resp = sb.table("all_chats").select("*").eq("email", email).order("chat_id", desc=True).limit(1).execute()
    if resp.error:
        return None
    data = resp.data or []
    return data[0] if data else None

def save_chat(
    email: str,
    user_messages: List[str],
    llm_responses: List[str],
    title: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    summary: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Save chat to Supabase table `all_chats`.
    - Skips save if user_messages is empty.
    - If latest saved chat for this email is identical (by messages + responses) the insert is skipped.
    Returns inserted row dict or None if skipped/failed.
    """
    if not user_messages or len(user_messages) == 0:
        return None

    sb = _get_supabase_client()

    # Check latest saved and skip duplicates
    latest = _latest_saved_for(email)
    if latest:
        try:
            latest_user = latest.get("user_messages") or []
            latest_llm = latest.get("llm_responses") or []
            if list(latest_user) == list(user_messages) and list(latest_llm) == list(llm_responses):
                # no changes
                return None
        except Exception:
            pass

    title = title or (user_messages[0][:120] if user_messages else f"chat-{datetime.utcnow().isoformat()}")

    payload = {
        "email": email,
        "title": title,
        "user_messages": user_messages,
        "llm_responses": llm_responses,
        "summary": summary,
        "metadata": metadata or {},
    }

    resp = sb.table("all_chats").insert(payload).select("*").execute()
    if resp.error:
        # caller may log; return None
        return None
    inserted = resp.data[0] if resp.data else None

    # optional mapping into user_chat_nums if you need it
    try:
        if inserted and inserted.get("chat_id"):
            sb.table("user_chat_nums").insert({"chat_id": inserted["chat_id"], "email": email}).execute()
    except Exception:
        pass

    return inserted

def summarize_and_meta(messages: List[str], model_name: Optional[str] = None) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Produce a short summary and lightweight metadata for the conversation.
    Uses an Ollama chat model (you can pass a mistral model name).
    Returns (summary_text, metadata_dict).
    """
    if not messages:
        return None, {}

    model_name = model_name or "mistral"  # override if needed
    try:
        model = ChatOllama(
            model=model_name,
            base_url=OllamaConfig.BASE_URL,
            temperature=0.0
        )
        convo = "\n\n".join(messages)
        prompt = (
            "You are a concise summarizer. Given the conversation, produce a JSON object with keys:\n"
            "  summary -> 1-2 sentence summary\n"
            "  tags -> list of short topic tags\n\n"
            f"Conversation:\n{convo}\n\nRespond ONLY with valid JSON."
        )
        resp = model.invoke(prompt)
        content = getattr(resp, "content", resp)
        # try parse as JSON
        parsed = {}
        try:
            parsed = json.loads(content)
            summary = parsed.get("summary") if isinstance(parsed, dict) else content
            tags = parsed.get("tags") if isinstance(parsed, dict) else []
            metadata = {"tags": tags, "generated_by": model_name}
            return summary, metadata
        except Exception:
            # fallback: use raw model output as summary
            return content.strip(), {"generated_by": model_name}
    except Exception:
        # last-resort lightweight summary
        joined = " ".join(messages)
        return joined[:400] + ("…" if len(joined) > 400 else ""), {"generated_by": "fallback", "length": len(messages)}