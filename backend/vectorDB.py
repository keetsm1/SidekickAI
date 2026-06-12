import chromadb
import uuid
import os

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_data")
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name="my_collection")

def save_to_chroma(embeddings, text):
    ids = [str(uuid.uuid4()) for _ in range(len(text))]

    collection.add(
        ids=ids,
        documents=text,
        embeddings=embeddings
    )

def clear_collection():
    all_ids = collection.get()["ids"]
    if all_ids:
        collection.delete(ids=all_ids)

