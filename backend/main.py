from fastapi import FastAPI
from pydantic import BaseModel
from embeddingsConversion import chunkText, to_embeddings
from vectorDB import save_to_chroma

class AskRequest(BaseModel):
    question: str
    page_text: str

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/ask")
def ask(ask: AskRequest):
    chunks = chunkText(ask.page_text)
    chunk_embeddings = to_embeddings(chunks)
    save_to_chroma(chunk_embeddings, chunks)

    question_embedding = to_embeddings(ask.question)
    save_to_chroma([question_embedding], [ask.question])

    return {
        "question": ask.question,
        "answer": "answer down the line"
    }