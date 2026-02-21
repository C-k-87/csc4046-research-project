import json
import uuid
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

data_path = Path("data/entries.jsonl")
# model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("transformer/bge-code-v1")
K_VALUE=3

persist_dir='data/persist'
chroma_client = chromadb.PersistentClient(path=persist_dir)
collection = chroma_client.get_or_create_collection(name='reflections')

def embed(text):
    return model.encode([text], normalize_embeddings=True)[0].tolist()

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

if __name__=="__main__":
    from collections import Counter

    add_reflection("I did not include a strong base case for a loop")
    add_reflection("I should add some unit tests")
    add_reflection("I check the data types")
    res = search("loop")["documents"][0]

    def classify_bug(reflection):
        t = reflection.lower()

        if "return" in t or "output" in t:
            return "RETURN_CONTRACT_VIOLATION"
        if "empty" in t or "none" in t or "minimal" in t:
            return "EDGE_CASE_MISSING"
        if "input" in t and ("valid" in t or "format" in t):
            return "INPUT_VALIDATION_ERROR"
        if "loop" in t or "iterate" in t:
            return "ITERATION_LOGIC_ERROR"
        if "index" in t or "out of range" in t or "pop" in t:
            return "INDEX_BOUND_ERROR"
        if "data structure" in t or "stack" in t or "list" in t:
            return "DATA_STRUCTURE_MISUSE"
        if "recursion" in t or "base case" in t:
            return "RECURSION_STRUCTURE_ERROR"

        return "PROBLEM_INTERPRETATION_ERROR"

    def get_top_k_bugs(reflections, k):
        bug_types = []
        for reflection in reflections:
            bug_type = classify_bug(reflection)
            bug_types.append(bug_type)

        counts = Counter(bug_types)
        
        sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1],reverse=True))
        return dict(list(sorted_counts.items())[:k])

    bug_types = get_top_k_bugs(res, 3)
    print(list(bug_types.keys()))