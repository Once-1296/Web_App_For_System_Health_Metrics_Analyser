# To revoke the history part.
import streamlit as st
from streamlit_chat import *
from supabase import create_client
from supabase import Client
from supabase_config import url, key

def render():
    