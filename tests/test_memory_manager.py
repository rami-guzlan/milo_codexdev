from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from milo_core.memory import Message
from milo_core.memory_manager import MemoryManager


def setup_manager() -> tuple[MemoryManager, MagicMock, MagicMock]:
    mock_llm = MagicMock()
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    with patch(
        "milo_core.memory_manager.chromadb.PersistentClient", return_value=mock_client
    ):
        with patch("sentence_transformers.SentenceTransformer") as mock_model:
            mock_model.return_value.encode.return_value = [0.1, 0.2]
            manager = MemoryManager(mock_llm, db_path="./milo_memory_db")
    return manager, mock_collection, mock_llm


def test_summarize_and_store_session_stores_when_useful() -> None:
    manager, collection, llm = setup_manager()
    llm.generate_response.side_effect = ["a summary", "YES"]
    manager.summarize_and_store_session([Message(role="user", content="hi")])
    collection.add.assert_called_once()


def test_summarize_and_store_session_skips_when_not_useful() -> None:
    manager, collection, llm = setup_manager()
    llm.generate_response.side_effect = ["a summary", "NO"]
    manager.summarize_and_store_session([Message(role="user", content="hi")])
    collection.add.assert_not_called()


def test_retrieve_relevant_memories_queries_collection() -> None:
    manager, collection, _ = setup_manager()
    collection.query.return_value = {"documents": [["doc"]]}
    result = manager.retrieve_relevant_memories("query")
    assert result == ["doc"]
    collection.query.assert_called_once()


def test_consolidate_memories() -> None:
    manager, collection, llm = setup_manager()
    old_ts = (datetime.now(timezone.utc) - timedelta(weeks=2)).isoformat()
    collection.get.return_value = {
        "documents": ["d1", "d2"],
        "metadatas": [{"timestamp": old_ts}, {"timestamp": old_ts}],
        "ids": ["id1", "id2"],
    }
    llm.generate_response.return_value = "digest"
    manager.consolidate_memories()
    assert "weekly digest" in llm.generate_response.call_args[0][0]
    collection.add.assert_called_once()
    collection.delete.assert_called_once_with(ids=["id1", "id2"])
