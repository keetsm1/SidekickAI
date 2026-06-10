from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunkText(text: str, chunk_size: int =400):
    words = text.split()

    chunks=[]

    for i in range (0, len(words), chunk_size):
        chunk = words[i:i+chunk_size]
        chunks.append("".join(chunk))

    return chunks

def convert_chunks_to_embeddings(chunks):
    embeddings = model.encode(chunks)

def convert_question_to_embeddings(question):
    embeddings = model.encode(question)

def save_to_vector_db(embeddings):
