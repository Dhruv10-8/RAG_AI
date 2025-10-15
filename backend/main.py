from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import rag_pipeline

app = FastAPI(title="IPL RAG Chatbot API")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "IPL RAG API is running"}

@app.post("/ask")
def ask_question(request: QueryRequest):
    answer = rag_pipeline(request.question)
    return {"answer": answer}
