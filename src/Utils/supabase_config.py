import streamlit as st
from supabase import create_client
import json

try:
    url = st.secrets.supabase["PROJECT_URL"]
    key = st.secrets.supabase["service_role_key"]
except Exception as e:
    print(f"Error accessing secrets: {e}")
    url,key="",""
