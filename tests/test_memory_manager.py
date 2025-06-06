from __future__ import annotations

from unittest.mock import MagicMock, patch

from milo_core.memory import Message
from milo_core.memory_manager import MemoryManager


def setup_manager() -> tuple[MemoryManager, MagicMock]:
    mock_llm = MagicMock()
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    with patch(
        "milo_core.memory_manager.chromadb.PersistentClient", return_value=mock_client
    ):
        with patch("sentence_transformers.SentenceTransformer") as mock_model:
            mock_model.return_value.encode.return_value = [0.1, 0.2]
            manager = MemoryManager(mock_llm)
    return manager, mock_collection


def test_summarize_and_store_session_stores_when_useful() -> None:
    manager, collection = setup_manager()
    manager.llm.generate_response.side_effect = ["a summary", "YES"]
    manager.summarize_and_store_session([Message(role="user", content="hi")])
    collection.add.assert_called_once()


def test_retrieve_relevant_memories_queries_collection() -> None:
    manager, collection = setup_manager()
    collection.query.return_value = {"documents": [["doc"]]}
    result = manager.retrieve_relevant_memories("query")
    assert result == ["doc"]
    collection.query.assert_called_once()
