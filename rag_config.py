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
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.1:8b"

# Chunking
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 6
