from functools import lru_cache
import time
import faiss
import threading
import numpy as np
from typing import Optional, List, Dict

from factories.embedding_factory import get_embedding_model
from logger import get_logger

logger = get_logger("SemanticCache")

class VolatileSemanticCache:
    def __init__(self, ttl_seconds: int = 3600, cleanup_interval: int = 1800):
        self.embeddings = get_embedding_model()

        logger.info("Probing embedding model for dimension size...")
        probe_vector = self.embeddings.embed_query("probe")
        self.dimension = len(probe_vector)
        logger.info(f"Detected embedding dimension: {self.dimension}")

        self.ttl = ttl_seconds
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        
        self.lock = threading.Lock()

        self.index = faiss.IndexFlatL2(self.dimension)
        self.entries: List[Dict] = []

    def check_cache(self, query: str, threshold: float = 0.35) -> Optional[str]:
        with self.lock:
            if not self.index or self.index.ntotal == 0:
                return None
            current_index = self.index
            current_entries = self.entries

        try:
            clean_query = query.strip().lower()
            vector = np.array([self.embeddings.embed_query(clean_query)]).astype('float32')
            
            distances, indices = current_index.search(vector, 1)
            distance = distances[0][0]
            idx = indices[0][0]

            if idx == -1 or distance > threshold:
                return None

            entry = current_entries[idx]
            if time.time() > entry["expiry"]:
                return None

            logger.info(f"✅ FAISS Cache HIT | Dist: {distance:.4f}")
            return entry["answer"]
        except Exception as e:
            logger.error(f"Cache check error: {e}")
            return None

    def update_cache(self, query: str, answer: str):
        try:
            clean_query = query.strip().lower()
            vector = np.array([self.embeddings.embed_query(clean_query)]).astype('float32')
            
            if vector.shape != (1, self.dimension):
                vector = vector.reshape(1, self.dimension)

            with self.lock:
                self.index.add(vector)
                self.entries.append({
                    "query": clean_query,
                    "answer": answer,
                    "expiry": time.time() + self.ttl,
                    "vector": vector 
                })
                logger.info(f"💾 Cache updated. Active: {self.index.ntotal}")

                if time.time() - self.last_cleanup > self.cleanup_interval:
                    snapshot = list(self.entries)
                    threading.Thread(
                        target=self._bg_rebuild, 
                        args=(snapshot,), 
                        daemon=True
                    ).start()
                
        except Exception as e:
            logger.error(f"Failed to update cache: {e}", exc_info=True)

    def _bg_rebuild(self, snapshot: List[Dict]):
        try:
            now = time.time()
            valid = [e for e in snapshot if e["expiry"] > now]
            
            new_index = faiss.IndexFlatL2(self.dimension)
            if valid:
                vectors = np.vstack([e["vector"] for e in valid]).astype('float32')
                new_index.add(vectors)
            
            with self.lock:
                self.index = new_index
                self.entries = valid
                self.last_cleanup = now
                logger.info(f"✨ BG Cleanup Complete: {len(self.entries)} entries retained.")
        except Exception as e:
            logger.error(f"Background rebuild failed: {e}", exc_info=True)

@lru_cache
def get_cache():
    return VolatileSemanticCache(ttl_seconds=3600, cleanup_interval=1800)