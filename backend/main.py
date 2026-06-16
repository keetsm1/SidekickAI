from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from embeddingsConversion import chunkText, to_embeddings
from vectorDB import save_to_chroma, collection, clear_collection
from llm import get_client
from pypdf import PdfReader
import io

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
    chunks = chunkText(req.text)
    embeddings = to_embeddings(chunks)
    save_to_chroma(embeddings, chunks)
    return {"chunks_ingested": len(chunks)}

@app.post("/ingest-pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    reader = PdfReader(io.BytesIO(content))

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

    chunks = chunkText(text)
    embeddings = to_embeddings(chunks)
    save_to_chroma(embeddings, chunks)
    return {"filename": file.filename, "chunks_ingested": len(chunks)}

@app.get("/count")
def count():
    return {"documents": collection.count()}

@app.delete("/clear")
def clear():
    clear_collection()
    return {"status": "cleared"}

@app.post("/ask")
def ask(ask: AskRequest, x_api_key: Optional[str] = Header(None)):
    client = get_client(api_key=x_api_key)

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "question": ask.question,
        "answer": response.text
    }
