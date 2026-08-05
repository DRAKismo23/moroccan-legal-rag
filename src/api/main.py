import sys
sys.path.insert(0, "src/ingestion")
sys.path.insert(0, "src/retrieval")
sys.path.insert(0, "src/graph")

from fastapi import FastAPI
from pydantic import BaseModel

from legal_rag_graph import build_graph, GraphState, CONFIDENCE_THRESHOLD

app = FastAPI(title="Moroccan Legal RAG API")

print("Building LangGraph workflow (loads BM25 index + reranker once at startup)...")
GRAPH = build_graph()
print("API ready to serve requests.\n")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    answer: str
    language: str
    confidence: float
    articles_used: list[str]


@app.get("/")
def root():
    return {"status": "ok", "message": "Moroccan Legal RAG API is running"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    initial_state: GraphState = {
        "query": request.question,
        "language": "",
        "retrieved_articles": [],
        "confidence": 0.0,
        "answer": "",
    }

    final_state = GRAPH.invoke(initial_state)

    # Only report articles as "used" if we actually generated an answer
    # from them — not when we declined due to low confidence
    articles_used = (
        [a["article_number"] for a in final_state["retrieved_articles"]]
        if final_state["confidence"] >= CONFIDENCE_THRESHOLD
        else []
    )

    return AskResponse(
        question=request.question,
        answer=final_state["answer"],
        language=final_state["language"],
        confidence=final_state["confidence"],
        articles_used=articles_used,
    )