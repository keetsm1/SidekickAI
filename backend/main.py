from fastapi import FastAPI
from pydantic import BaseModel
from embeddingsConversion import chunkText, to_embeddings
from vectorDB import save_to_chroma, collection, clear_collection
from llm import client

class AskRequest(BaseModel):
    question: str

class IngestRequest(BaseModel):
    text: str

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/ingest")
def ingest(req: IngestRequest):
    clear_collection()
    chunks = chunkText(req.text)
    embeddings = to_embeddings(chunks)
    save_to_chroma(embeddings, chunks)
    return {"chunks_ingested": len(chunks)}

@app.post("/ask")
def ask(ask: AskRequest):
    question_embedding = to_embeddings(ask.question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    # Build prompt from search results
    context = "\n\n".join(results["documents"][0])
    prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {ask.question}

Answer:"""

    # Get LLM response
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return {
        "question": ask.question,
        "answer": response.text
    }