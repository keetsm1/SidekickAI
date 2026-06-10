import chromadb

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(name="my_collection")

def save_to_chroma(embeddings, text):
    ids = [f"doc_{i}" for i in range(len(text))]

    collection.add(
        ids=ids,
        documents=text,
        embeddings=embeddings
    )

