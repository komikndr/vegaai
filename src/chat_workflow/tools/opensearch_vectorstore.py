import os
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.tools import tool

import chainlit as cl
EMBEDDING_MODEL = "text-embedding-3-small"

OPENSEARCH_URL = os.getenv("OPENSEARCH_URL")
OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD")
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER")
OPENSEARCH_VECTOR_INDEX = os.getenv("OPENSEARCH_VECTOR_INDEX")

OPENSEARCH_AUTH=(OPENSEARCH_USER, OPENSEARCH_PASSWORD)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = OpenSearchVectorSearch(
    opensearch_url=OPENSEARCH_URL,
    embedding_function=embeddings,
    http_auth=OPENSEARCH_AUTH,
    index_name=OPENSEARCH_VECTOR_INDEX,
    use_ssl=False,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)


@tool(response_format="content_and_artifact")
def vector_retriever(query: str, top_k=3):
    """
    Retrieve relevant documents from a vector store based on the given query.

    This function performs a similarity search in a vector database and returns
    the top-k most relevant documents. It provides both a serialized textual
    summary of the retrieved documents and their raw structured data.

    Args:
        query (str): The input query to search for relevant documents.
        top_k (int, optional): The number of top matching documents to retrieve.
                               Defaults to 3.
    """
    retrieved_docs = vector_store.similarity_search(query, k=1)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs
