# rag_config.py
from pathlib import Path

# Paths
DATA_DIR = Path("data")
SYSTEM_CORPUS_DIR = DATA_DIR / "system_knowledge"
LINUX_DIR = SYSTEM_CORPUS_DIR / "linux"
ARCH_WIKI_DIR = LINUX_DIR / "arch_wiki" 
UBUNTU_WIKI_DIR = LINUX_DIR / "ubuntu_wiki"
CHROMA_DIR = Path("chroma_db/main_corpus")
WINDOWS_DOCS_DIR = SYSTEM_CORPUS_DIR / "windows"

# Models
import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Load Secrets
# Ensure you have GROQ_API_KEY in your .streamlit/secrets.toml or Docker ENV
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

# 2. Setup Embeddings (Runs locally on CPU, no API needed)
# This replaces OllamaEmbeddings
EMBED_MODEL_NAME = "all-MiniLM-L6-v2" 
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)

# 3. Setup LLM (Groq)
# This replaces OllamaLLM
SUMMARY_MODEL = "llama-3.1-8b-instant"
CHAT_MODEL_NAME = "llama-3.3-70b-versatile" 
llm = ChatGroq(
    model=CHAT_MODEL_NAME,
    api_key=GROQ_API_KEY,
    temperature=0.5
)

# Chunking
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 6
