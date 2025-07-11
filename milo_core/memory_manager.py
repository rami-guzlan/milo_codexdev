import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import List

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import chromadb

from .memory import Message


class MemoryManager:
    """Manage long-term memories using a local vector store."""

    def __init__(self, llm_instance, db_path: str = "./milo_memory_db") -> None:
        self.llm = llm_instance
        self.db_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.db_client.get_or_create_collection(
            name="long_term_memory"
        )
        from sentence_transformers import SentenceTransformer

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def summarize_and_store_session(self, session_history: List[Message]) -> None:
        """Summarize a conversation session and store it if useful."""
        history_text = "\n".join(f"{m.role}: {m.content}" for m in session_history)
        summary_prompt = (
            "Summarize the key entities, topics, user preferences in 2-3 sentences:"
            f" {history_text}"
        )
        summary_blurb = self.llm.generate_response(summary_prompt)
        verification_prompt = (
            "Does the following text contain specific, useful information that should"
            f" be remembered? Answer only YES or NO. Text: '{summary_blurb}'"
        )
        verification = self.llm.generate_response(verification_prompt)
        if verification.strip().upper() == "YES":
            self._store_memory(summary_blurb)

    def _store_memory(self, text: str) -> None:
        embedding = self.embedding_model.encode(text)
        timestamp = datetime.now(timezone.utc).isoformat()
        doc_id = str(uuid.uuid4())
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"timestamp": timestamp}],
            ids=[doc_id],
        )

    def retrieve_relevant_memories(self, text: str, limit: int = 3) -> List[str]:
        embedding = self.embedding_model.encode(text)
        results = self.collection.query(query_embeddings=[embedding], n_results=limit)
        documents = results.get("documents", [[]])
        return documents[0] if documents else []

    def consolidate_memories(self) -> None:
        """Consolidate older memories into weekly digests."""
        now = datetime.now(timezone.utc)
        records = self.collection.get(include=["documents", "metadatas"])
        if not records:
            return

        docs_by_week = {}
        for doc, meta, doc_id in zip(
            records.get("documents", []),
            records.get("metadatas", []),
            records.get("ids", []),
        ):
            if not meta:
                continue
            ts = datetime.fromisoformat(meta.get("timestamp"))
            if now - ts < timedelta(weeks=1):
                continue
            week_key = ts.strftime("%Y-%W")
            docs_by_week.setdefault(week_key, []).append((doc_id, doc))

        for week, docs in docs_by_week.items():
            texts = [d for _, d in docs]
            consolidation_prompt = (
                "Summarize the following memories into a weekly digest:"
                + " \n".join(texts)
            )
            digest = self.llm.generate_response(consolidation_prompt)
            self._store_memory(f"Week {week}: {digest}")
            ids_to_delete = [doc_id for doc_id, _ in docs]
            self.collection.delete(ids=ids_to_delete)
