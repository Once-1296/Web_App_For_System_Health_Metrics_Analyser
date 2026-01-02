# main_corpus_ingestion.py
import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from rag_config import (
    ARCH_WIKI_DIR,
    CHROMA_DIR,
    UBUNTU_WIKI_DIR,
    WINDOWS_DOCS_DIR,
    embeddings,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


def load_windows_docs():
    documents = []
    for domain_dir in WINDOWS_DOCS_DIR.iterdir():
        if not domain_dir.is_dir():
            continue

        domain = domain_dir.name

        for file in domain_dir.glob("*.json"):
            topic = file.stem

            with open(file, "r", encoding="utf-8") as f:
                content = json.load(f)

            text = json.dumps(content, indent=2, ensure_ascii=False)

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": "windows_docs",
                        "domain": domain,
                        "topic": topic,
                        "os": "windows",
                        "distro": "10/11",
                        "path": str(file),
                    },
                )
            )

    return documents

def load_arch_wiki_docs():
    documents = []

    for domain_dir in ARCH_WIKI_DIR.iterdir():
        if not domain_dir.is_dir():
            continue

        domain = domain_dir.name

        for file in domain_dir.glob("*.json"):
            topic = file.stem

            with open(file, "r", encoding="utf-8") as f:
                content = json.load(f)

            text = json.dumps(content, indent=2, ensure_ascii=False)

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": "arch_wiki",
                        "domain": domain,
                        "topic": topic,
                        "os": "linux",
                        "distro": "arch",
                        "path": str(file),
                    },
                )
            )

    return documents


def load_ubuntu_wiki_docs():
    documents = []

    for domain_dir in UBUNTU_WIKI_DIR.iterdir():
        if not domain_dir.is_dir():
            continue

        domain = domain_dir.name

        for file in domain_dir.glob("*.json"):
            topic = file.stem

            with open(file, "r", encoding="utf-8") as f:
                content = json.load(f)

            text = json.dumps(content, indent=2, ensure_ascii=False)

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": "ubuntu_docs",
                        "domain": domain,
                        "topic": topic,
                        "os": "linux",
                        "distro": "ubuntu",
                        "path": str(file),
                    },
                )
            )

    return documents


def ingest():
    print("📥 Loading Arch Wiki docs...")
    docs = load_arch_wiki_docs()

    print("📥 Loading Ubuntu docs...")
    docs.extend(load_ubuntu_wiki_docs())

    print("📥 Loading Windows docs...")
    docs.extend(load_windows_docs())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )

    splits = splitter.split_documents(docs)

    print(f"✂️ Total chunks: {len(splits)}")

    vectorstore = Chroma(
        collection_name="main_corpus",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    vectorstore.reset_collection()
    vectorstore.add_documents(splits)

    print("✅ Main corpus ingestion complete.")


if __name__ == "__main__":
    ingest()
