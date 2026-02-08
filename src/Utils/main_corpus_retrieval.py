# main_corpus_retrieval.py
from langchain_chroma import Chroma
from src.Utils.rag_config import CHROMA_DIR, embeddings as _embeddings, TOP_K

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
