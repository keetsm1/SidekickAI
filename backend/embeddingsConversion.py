from sentence_transformers import SentenceTransformer
from vectorDB import save_to_chroma
model = SentenceTransformer("all-MiniLM-L6-v2")

def chunkText(text: str, chunk_size: int =400):
    words = text.split()

    chunks=[]

    for i in range (0, len(words), chunk_size):
        chunk = words[i:i+chunk_size]
        chunks.append(" ".join(chunk))

    return chunks

def to_embeddings(text):
    return model.encode(text)

