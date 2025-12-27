# rag_app.py
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from head_query import gather_context
from rag_config import CHAT_MODEL

llm = OllamaLLM(model=CHAT_MODEL)

PROMPT = ChatPromptTemplate.from_template(
    """
You are a Linux system troubleshooting assistant.
Answer using the provided documentation context.
Be precise and practical.
If the answer is unknown, say so.

Context:
{context}

Question:
{question}
"""
)

def format_docs(docs):
    return "\n\n".join(
        f"[{d.metadata.get('domain')}/{d.metadata.get('topic')}]\n{d.page_content}"
        for d in docs
    )

def answer_query(query: str):
    contexts = gather_context(query)

    main_context = format_docs(contexts["main"])

    chain = PROMPT | llm | StrOutputParser()

    return chain.invoke(
        {
            "context": main_context,
            "question": query,
        }
    )
