# BAAI/bge-code-v1.5
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-code-v1")
path = "../transformer/model"

model.save()