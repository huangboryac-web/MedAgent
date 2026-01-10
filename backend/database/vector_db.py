import os
import logging
from typing import List
from langchain_chroma import Chroma
from langchain_core.documents import Document

from constants import VECTOR_DB_PERSIST_DIR, VECTOR_DB_COLLECTION_NAME
from factories.embedding_factory import get_embedding_model
from logger import get_logger

logger = get_logger("VectorDB")

embeddings = get_embedding_model()

def get_vectorstore() -> Chroma:
    if not os.path.exists(VECTOR_DB_PERSIST_DIR):
        os.makedirs(VECTOR_DB_PERSIST_DIR)
        
    return Chroma(
        collection_name=VECTOR_DB_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_PERSIST_DIR
    )

def index_documents(documents: List[Document]):
    if not documents:
        return
    try:
        vectorstore = get_vectorstore()
        vectorstore.add_documents(documents)
        logger.info(f"💾 Indexed {len(documents)} new documents.")
    except Exception as e:
        logger.error(f"❌ Indexing Failed: {e}", exc_info=True)

def retrieve_documents(query: str, k: int = 5) -> List[Document]:
    try:
        vectorstore = get_vectorstore()
        docs = vectorstore.similarity_search(query, k=k)
        if docs:
            logger.info(f"✅ Retrieved {len(docs)} documents.")
        else:
            logger.warning(f"⚠️ Cache Miss: No docs for '{query}'")
        return docs
    except Exception as e:
        logger.error(f"❌ Retrieval Failed: {e}", exc_info=True)
        return []