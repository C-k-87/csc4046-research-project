import json
import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

data_path = Path("data/entries.jsonl")
# model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("transformer/model")
K_VALUE=3

chroma_client = chromadb.Client(
    Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
collection = chroma_client.create_collection(name='reflections')

def embed(text):
    return model.encode([text])[0].tolist()

def save_entry(data):
    data_path.parent.mkdir(exist_ok=True)
    with data_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data)+'\n')

def add_reflection(text, metadata={'data':'none'}):
    id = str(uuid.uuid4())

    entry = {
        "id": id,
        "text": text,
        "metadata": metadata
    }

    save_entry(entry)

    collection.add(
        ids=[id],
        documents=[text],
        embeddings=[embed(text)],
        metadatas=[metadata]
    )
    
    return id

def search(query, k=K_VALUE):
    res = collection.query(
        query_embeddings=[embed(query)],
        n_results=k
    )

    return res