import sys
sys.path.insert(0, "src/ingestion")
sys.path.insert(0, "src/retrieval")
sys.path.insert(0, "src/graph")

from typing import TypedDict
import requests
from reranked_search import full_search
from langgraph.graph import StateGraph, END


class GraphState(TypedDict):
    query: str
    language: str
    retrieved_articles: list
    confidence: float
    answer: str


def detect_language(state: GraphState) -> GraphState:
    """Simple heuristic: check for Arabic script characters."""
    query = state["query"]
    has_arabic = any('\u0600' <= ch <= '\u06FF' for ch in query)
    language = "ar" if has_arabic else "fr"
    print(f"[detect_language] Detected: {language}")
    return {**state, "language": language}


def retrieve(state: GraphState) -> GraphState:
    """Run our Milestone 5 hybrid search + reranking pipeline."""
    print(f"[retrieve] Searching for: '{state['query']}'")
    results = full_search(state["query"], hybrid_candidates=15, final_top_k=3)
    articles = [article for article, score in results]
    top_score = results[0][1] if results else 0.0
    print(f"[retrieve] Found {len(articles)} articles, top score: {top_score:.4f}")
    return {**state, "retrieved_articles": articles, "confidence": float(top_score)}


CONFIDENCE_THRESHOLD = 0.05  # Below this, we don't trust the results enough to answer


def check_confidence(state: GraphState) -> str:
    """
    Conditional edge function: returns which node to go to next, based on
    whether our retrieval confidence is high enough to attempt an answer.
    """
    if state["confidence"] < CONFIDENCE_THRESHOLD:
        print(f"[check_confidence] Low confidence ({state['confidence']:.4f}) — declining to answer")
        return "low_confidence"
    print(f"[check_confidence] Confidence OK ({state['confidence']:.4f}) — proceeding to generate")
    return "generate"


def generate_answer(state: GraphState) -> GraphState:
    """
    Feed the query + retrieved articles to Qwen 3, instructing it to answer
    in the query's detected language. This is where our Arabic-primary +
    live-translation strategy actually happens: articles may be in Arabic,
    but Qwen 3 translates/synthesizes the answer in whatever language the
    user asked in.
    """
    articles_text = "\n\n".join(
        f"Article {a['article_number']} ({a['law_name']}, {a['language']}):\n{a['text'][:800]}"
        for a in state["retrieved_articles"]
    )

    language_instruction = {
        "fr": "Réponds en français, même si les articles sources sont en arabe. Traduis le contenu pertinent.",
        "ar": "أجب باللغة العربية.",
    }[state["language"]]

    prompt = f"""Tu es un assistant juridique spécialisé dans le droit marocain. 
{language_instruction}
Base ta réponse UNIQUEMENT sur les articles fournis ci-dessous. Cite le numéro de l'article dans ta réponse.

Articles pertinents:
{articles_text}

Question de l'utilisateur: {state['query']}

Réponse:"""

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen3:4b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
    )
    response.raise_for_status()
    answer = response.json()["message"]["content"]

    print(f"[generate_answer] Generated {len(answer)} characters")
    return {**state, "answer": answer}


def low_confidence_response(state: GraphState) -> GraphState:
    """Honest fallback when we don't have a confident match in our corpus."""
    message = (
        "Je n'ai pas trouvé d'article pertinent dans les codes disponibles "
        "(Code Pénal, Code de Procédure Pénale, Code de la Route) pour répondre "
        "précisément à cette question."
    )
    print("[low_confidence_response] Returning honest 'no answer' response")
    return {**state, "answer": message}


def build_graph():
    """Assembles our 4 nodes into an actual LangGraph workflow with
    conditional branching based on retrieval confidence."""
    workflow = StateGraph(GraphState)

    # Register each node
    workflow.add_node("detect_language", detect_language)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("low_confidence", low_confidence_response)

    # Define the flow
    workflow.set_entry_point("detect_language")
    workflow.add_edge("detect_language", "retrieve")

    # Conditional branch: after retrieve, check_confidence decides
    # whether to go to "generate" or "low_confidence"
    workflow.add_conditional_edges(
        "retrieve",
        check_confidence,
        {
            "generate": "generate",
            "low_confidence": "low_confidence",
        }
    )

    # Both paths end the graph after producing their answer
    workflow.add_edge("generate", END)
    workflow.add_edge("low_confidence", END)

    return workflow.compile()


if __name__ == "__main__":
    graph = build_graph()

    queries = [
        "Quelle est la sanction pour un excès de vitesse important ?",
        "Quelle est la vitesse maximale autorisée en ville ?",  # our known "no good answer" case
    ]

    for query in queries:
        print("=" * 60)
        print(f"QUERY: {query}")
        print("=" * 60)

        initial_state: GraphState = {
            "query": query,
            "language": "",
            "retrieved_articles": [],
            "confidence": 0.0,
            "answer": "",
        }

        final_state = graph.invoke(initial_state)

        print(f"\n--- FINAL ANSWER ---")
        print(final_state["answer"])
        print()