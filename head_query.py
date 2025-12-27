# head_query.py
from main_corpus_retrieval import retrieve_main_corpus

def gather_context(query: str):
    main_docs = retrieve_main_corpus(query)

    # Later:
    # user_docs = retrieve_user_docs(user_id)
    # system_docs = retrieve_system_data(user_id)

    return {
        "main": main_docs,
        # "user": user_docs,
        # "system": system_docs,
    }
