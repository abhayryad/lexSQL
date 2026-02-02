from langchain_community.vectorstores import FAISS

def build_schema_index(schema_texts: list[str], embedding_model):
    """
    Build a FAISS vector store from schema documents.
    """
    vectorstore = FAISS.from_texts(
        texts=schema_texts,
        embedding=embedding_model
    )
    return vectorstore

def retrieve_relevant_schema(vectorstore, query: str, k: int = 4) -> str:
    """
    Retrieve top-k relevant schema chunks for a query.
    """
    docs = vectorstore.similarity_search(query, k=k)
    return "\n".join(doc.page_content for doc in docs)
