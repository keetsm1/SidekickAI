import chromadb
import uuid

chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="my_collection")

def save_to_chroma(embeddings, text):
    ids = [str(uuid.uuid4()) for _ in range(len(text))]

    collection.add(
        ids=ids,
        documents=text,
        embeddings=embeddings
    )

def clear_collection():
    collection.delete(where={})

