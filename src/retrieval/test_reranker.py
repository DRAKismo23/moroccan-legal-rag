from sentence_transformers import CrossEncoder

print("Loading BGE-Reranker-v2 (this will download the model on first run)...")
model = CrossEncoder("BAAI/bge-reranker-v2-m3")
print("Model loaded successfully.\n")

query = "peine de mort"

candidates = [
    "Le meurtre commis avec préméditation ou guet-apens est qualifié assassinat et puni de la peine de mort.",
    "Nul ne peut conduire un véhicule sans permis de conduire.",
    "Est puni de la peine de mort, quiconque pour l'exécution d'un fait qualifié crime emploie des tortures.",
]

pairs = [[query, candidate] for candidate in candidates]
scores = model.predict(pairs)

print(f"Query: '{query}'\n")
for candidate, score in zip(candidates, scores):
    print(f"Score: {score:.4f}")
    print(f"Text: {candidate}")
    print()