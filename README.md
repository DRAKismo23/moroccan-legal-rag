# Moroccan Legal RAG Chatbot

A production-grade, locally-hosted Retrieval-Augmented Generation (RAG) chatbot for answering questions about Moroccan law, supporting French and Arabic legal documents.

## Status
🚧 Under active development — Milestone 2 (PDF Parsing)

## Scope

This chatbot covers three Moroccan legal codes:
- **Code Pénal** (Criminal Code)
- **Code de Procédure Pénale** (Criminal Procedure Code)
- **Code de la Route** (Road Traffic Code)

## Tech Stack
- **LLM:** Qwen 3 Instruct (via Ollama, local)
- **Embeddings:** BGE-M3 (multilingual)
- **Vector DB:** Qdrant (local persistent)
- **Retrieval:** Hybrid Search (Dense + BM25)
- **Reranker:** BGE-Reranker-v2
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **PDF Parsing:** PyMuPDF
- **Workflow:** LangGraph
- **Containerization:** Docker & Docker Compose

## Data Sourcing Notes

This project uses **Arabic as the authoritative source language** for all three legal codes, since Moroccan law is officially published in Arabic, and current French translations are often outdated, incomplete, or unavailable for certain codes (notably the Code de Procédure Pénale, whose current version — Law 22.01 — was published only in Arabic).

French output is generated **at query time** via LLM translation of the retrieved Arabic source text, rather than relying on static French documents — ensuring answers stay grounded in the legally current text regardless of translation availability.

**Sources used:**
- Code Pénal — Arabic (Aug 2024) & French (Apr 2023), both official, via adala.justice.gov.ma
- Code de la Route — Arabic (July 2024), official, via sgg.gov.ma
- Code de Procédure Pénale — Arabic (Dec 2025, reflects Law 03.23 amendment), official, via adala.justice.gov.ma

## Setup
Instructions coming soon as the project develops.