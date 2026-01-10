import os
import logging
from typing import List
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever

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

        m = k * 4  
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": m})
        candidate_docs = vector_retriever.invoke(query)
        
        if not candidate_docs:
            logger.warning(f"⚠️ No vector docs for '{query}'")
            return []
        
        bm25_retriever = BM25Retriever.from_documents(candidate_docs)
        bm25_retriever.k = len(candidate_docs) 
        bm25_docs = bm25_retriever.invoke(query)
        
        vector_ranks = {doc.page_content: rank for rank, doc in enumerate(candidate_docs, 1)}
        bm25_ranks = {doc.page_content: rank for rank, doc in enumerate(bm25_docs, 1)}

        hybrid_scores = {}
        for doc in candidate_docs:
            content = doc.page_content
            ## When using the RRF reranking strategy, we need to configure the parameter k. 
            ## It is a smoothing parameter that can effectively alter the relative weights of full-text search versus vector search.  
            ## 60 is commonly chosen for RRF (https://milvus.io/docs/rrf-ranker.md)
            rrf_score = (1 / (60 + vector_ranks.get(content, m+1))) + (1 / (60 + bm25_ranks.get(content, m+1))) 
            hybrid_scores[content] = rrf_score

        sorted_contents = sorted(hybrid_scores, key=hybrid_scores.get, reverse=True)[:k]
        hybrid_docs = [next(d for d in candidate_docs if d.page_content == content) for content in sorted_contents]
        
        if hybrid_docs:
            logger.info(f"✅ Retrieved {len(hybrid_docs)} hybrid documents (vector + BM25 rerank).")
        else:
            logger.warning(f"⚠️ Cache Miss: No docs for '{query}'")
        return hybrid_docs
    except Exception as e:
        logger.error(f"❌ Retrieval Failed: {e}", exc_info=True)
        return []