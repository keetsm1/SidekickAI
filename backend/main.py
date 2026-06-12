from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from embeddingsConversion import chunkText, to_embeddings
from vectorDB import save_to_chroma, collection, clear_collection
from llm import client

class AskRequest(BaseModel):
    question: str

class IngestRequest(BaseModel):
    text: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/count")
def count():
    return {"documents": collection.count()}

@app.post("/ask")
def ask(ask: AskRequest):
    question_embedding = to_embeddings(ask.question)

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    documents = results.get("documents", [[]])[0]
    if not documents:
        prompt = f"""You are a helpful assistant. Answer the following question based on your own knowledge.

Question: {ask.question}

Answer:"""
    else:
        context = "\n\n".join(documents)
        prompt = f"""You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {ask.question}

Answer:"""

    # Get LLM response
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "question": ask.question,
        "answer": response.text
    }