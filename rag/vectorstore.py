import chromadb
from chromadb.utils import embedding_functions
import os

from config import GOOGLE_API_KEY

client = chromadb.Client(chromadb.config.Settings(
    persist_directory="./chroma_db"
))

embedding_fn = embedding_functions.google_embedding_function.GoogleGenerativeAiEmbeddingFunction(model_name="models/text-embedding-004")

collection = client.create_collection(
    name="damage_policy",
    embedding_function=embedding_fn
)


project_root = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(project_root, "policies")

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    collection.add(
        ids=[filename],                # unique id for each document
        documents=[text],              # the document contents
        metadatas=[{"source": filename}],
    )