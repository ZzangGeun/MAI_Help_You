# Copilot Instructions for MAI

Purpose
- Make AI coding agents productive in this Django + LangChain (RAG) project with an optional FastAPI microservice.

Big picture
- Django project `MAI` with apps: `chatbot`, `character_info`, `main_page`.
- Chat flow: HTTP → `chatbot/views.py` → `ChatbotService` (`chatbot/services.py`) → LangChain ConversationalRetrievalChain → FAISS (`MAI_db/indexex/faiss_index`) → LLM.
- RAG data lives in `MAI_db/json_data/**`; index is created on first run and persisted.
- Optional `fastapi_model/` provides a separate API using similar HF model logic.

Key files/dirs
- `MAI/settings.py`: loads `.env` via `dotenv`; SQLite default DB; uses `SECRET_KEY`, `NEXON_API_KEY`, `OPENAI_API_KEY`, `HUGGINGFACE_TOKEN`.
- `chatbot/services.py`: RAG + LLM core. Entrypoints: `ChatbotService.get_response()`, `get_chat_history()`, `clear_history()`.
- `chatbot/views.py` + `chatbot/urls.py`: endpoints `/chatbot/ask/`, `/chatbot/history/`, `/chatbot/clear-history/`, `/chatbot/health/`.
- `fastapi_model/{main.py,routes.py,model.py}`: separate API (`uvicorn main:app`).
- `MAI_db/json_data/` (sources) and `MAI_db/indexex/` (FAISS store).

LLM/RAG behavior
- `chatbot/services.py` instantiates `chatbot_service = ChatbotService()` at import time; model+memory are singleton-like.
- `CustomLLM` tries local fine-tuned model at `fine_tuned_model/fine_tuned_model` (absolute Windows path in code). If missing, falls back to `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`.
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (CPU). Retriever `k=3`.
- First run builds FAISS from `MAI_db/json_data/**` and saves to `MAI_db/indexex/faiss_index`.
- Requires `HUGGINGFACE_TOKEN` for hub login in both Django and FastAPI code paths.

Developer workflows (Windows cmd)
- Install: `pip install -r requirements.txt`
- Run Django: `python manage.py runserver`
- Optional FastAPI: `cd fastapi_model && uvicorn main:app --reload --port 8001`
- Env: create `.env` in repo root with `SECRET_KEY`, `HUGGINGFACE_TOKEN`, `NEXON_API_KEY`, `OPENAI_API_KEY`.
- Refresh RAG data: add JSON to `MAI_db/json_data/`; delete `MAI_db/indexex/faiss_index` to force rebuild next run.

Conventions & gotchas
- Avoid re-initializing models per request; reuse `chatbot_service`.
- Keep FAISS path consistent (`MAI_db/indexex/faiss_index`) across save/load.
- Windows-specific absolute path in `CustomLLM.model_path`; consider making it env-driven if you refactor.
- Tokenizer must have `pad_token = eos_token` (already set in code).
- CORS in FastAPI allows Django dev origins only (`http://localhost:8000`, `http://127.0.0.1:8000`).
- Default DB is SQLite; migrations are standard Django ones.

Typical extensions
- New chatbot endpoint: add view in `chatbot/views.py`, wire in `chatbot/urls.py`; call `chatbot_service.get_response()`.
- Swap embedding/model: edit model names in `chatbot/services.py` (and `fastapi_model/model.py` if used).
- Custom RAG data location: update the loader/save paths consistently in services code.

External integrations
- Nexon API via `NEXON_API_KEY` (see `main_page/get_nexon_api.py`).
- Hugging Face Hub login via `HUGGINGFACE_TOKEN`.

Do / Don’t
- Do configure secrets via `.env`, not hard-coded.
- Do maintain single model initialization; heavy loads belong at module init, not per request.
- Don’t rename or move `MAI_db/indexex/faiss_index` without updating both load and save.
- Don’t assume the local fine-tuned model path exists; handle fallback or make it configurable.

Smoke test
- Start Django, open `/chatbot/`, POST to `/chatbot/ask/` with `{ "question": "테스트" }` → expect JSON response and `has_rag` true if FAISS exists.
