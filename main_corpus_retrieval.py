# main_corpus_retrieval.py
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from rag_config import CHROMA_DIR, EMBED_MODEL, TOP_K

_embeddings = OllamaEmbeddings(model=EMBED_MODEL)

_vectorstore = Chroma(
    collection_name="main_corpus",
    embedding_function=_embeddings,
    persist_directory=str(CHROMA_DIR),
)

_retriever = _vectorstore.as_retriever(
    search_kwargs={"k": TOP_K}
)


def retrieve_main_corpus(query: str):
    return _retriever.invoke(query)
