from fastapi import FastAPI
from pydantic import BaseModel
from embeddingsConversion import chunkText

class AskRequest(BaseModel):
    question: str
    page_text: str

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

@app.post("/ask")
def root(ask: AskRequestL):

    chunkText(ask.page_text)
    return {
        "question": ask.question,
        "answer": "answer down the line"
    }