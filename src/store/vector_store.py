import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils import embedding_functions

from functools import lru_cache

DEFAULT_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
RULES_COLLECTION_NAME = "rules"
OFFICIAL_QA_COLLECTION_NAME = "official_qa"
EMBED_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

@lru_cache(maxsize=None)
def _get_embedding_function(model_name: str = EMBED_MODEL_NAME):
    """Return a SentenceTransformer embedding function for Chroma."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)


def _chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split long text into overlapping chunks.

    Args:
        text: The text to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

@lru_cache(maxsize=None)
def get_client(persist_directory: str = DEFAULT_PERSIST_DIR) -> chromadb.PersistentClient:
    """Return (and create if missing) a Chroma client."""
    os.makedirs(persist_directory, exist_ok=True)
    return chromadb.PersistentClient(path=persist_directory)

class VectorStore:
    def __init__(
        self,
        persist_directory: str = DEFAULT_PERSIST_DIR,
        embedding_model_name: str = EMBED_MODEL_NAME,
    ):
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model_name

        self._client = get_client(persist_directory)
        self._embedding_function = _get_embedding_function(embedding_model_name)

    def get_collection(self, name: str):
        """Return (or create) a Chroma collection bound to this store."""
        return self._client.get_or_create_collection(
            name=name,
            embedding_function=self._embedding_function,
        )

    def populate_rules_collection(
        self,
        rules_dir: str = "data/ygoresources/processed/rules",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """Populate (or refresh) the `rules` collection with chunked texts."""
        collection = self.get_collection(RULES_COLLECTION_NAME)

        rules_path = Path(rules_dir)
        txt_files = list(rules_path.glob("*.txt"))

        existing_ids = set(collection.get(ids=None, limit=0)["ids"]) if collection.count() > 0 else set()

        for txt_file in txt_files:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = _chunk_text(content, chunk_size, chunk_overlap)
            documents, metadatas, ids = [], [], []
            for idx, chunk in enumerate(chunks):
                doc_id = f"{txt_file.name}-{idx}"
                if doc_id in existing_ids:
                    continue
                documents.append(chunk)
                metadatas.append({"filename": txt_file.name, "chunk_index": idx})
                ids.append(doc_id)

            if documents:
                collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def populate_official_qa_collection(
        self,
        qa_dir: str = "data/ygoresources/processed/official_qa",
    ):
        """Populate (or refresh) the `official_qa` collection."""
        collection = self.get_collection(OFFICIAL_QA_COLLECTION_NAME)

        qa_path = Path(qa_dir)
        json_files = list(qa_path.glob("*.json"))

        existing_ids = set(collection.get(ids=None, limit=0)["ids"]) if collection.count() > 0 else set()

        for json_file in json_files:
            doc_id = json_file.stem
            if doc_id in existing_ids:
                continue

            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            qa_en = data.get("qaData", {}).get("en")
            if not qa_en:
                continue

            question = qa_en.get("question", "").strip()
            answer = qa_en.get("answer", "").strip()
            if not question and not answer:
                continue

            document = f"Q: {question}\n\nA: {answer}"
            card_ids = data.get("cards", [])
            metadata = {
                "cardIds": ",".join(map(str, card_ids)),
                "qa_text": document,
            }
            collection.add(documents=[document], metadatas=[metadata], ids=[doc_id])

    def similarity_search(
        self,
        query_text: str,
        collection_name: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ):
        """Return top-k documents most similar to the query in *collection_name*."""
        collection = self.get_collection(collection_name)

        results = collection.query(query_texts=[query_text], n_results=k, where=where)
        ids = results["ids"][0]
        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        return [
            {"id": i, "document": d, "metadata": m, "distance": dist}
            for i, d, m, dist in zip(ids, docs, metadatas, distances)
        ]

    def get_qa_by_card_ids(self, card_ids: List[int]):
        """Return QA docs for the supplied card IDs using instance defaults."""
        collection = self.get_collection(OFFICIAL_QA_COLLECTION_NAME)

        all_docs = collection.get(include=["documents", "metadatas"])
        result = []
        target_set = set(map(str, card_ids))
        for doc_id, doc, meta in zip(all_docs["ids"], all_docs["documents"], all_docs["metadatas"]):
            card_str = meta.get("cardIds", "")
            doc_cards = set(card_str.split(",")) if card_str else set()
            if doc_cards & target_set:
                result.append({"id": doc_id, "document": doc, "metadata": meta})
        return result