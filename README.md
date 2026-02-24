# Department AI Brain (Backend Only)

Production-oriented AI service for department queries:
- Structured lookup for strict facts (teacher cabin, subjects taught).
- RAG for natural language Q&A using faculty knowledge chunks.
- Guardrailed LLM prompt to reduce hallucinations.
- Domain guardrail for non-department questions.
- Abusive language filter.
- Optional API key auth (`X-API-Key`) and request rate limiting.
- Readiness endpoint and request-id based logging.

## 1) Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set provider values in `.env`.

OpenAI example:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
LLM_MODEL=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-small
```

Gemini example:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key
LLM_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=text-embedding-004
```

## 2) Run API

```bash
uvicorn app.main:app --reload
```

API base: `http://127.0.0.1:8000`

Production run (example):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

## 3) Endpoints

- `GET /health`
- `GET /ready`
- `POST /ingest`  
  Builds embeddings and loads faculty chunks into Chroma.
- `POST /query`  
  Body:
  ```json
  {
    "question": "Where can I find AI sir?"
  }
  ```

Response:
```json
{
  "answer": "Dr. Anil Mehta is in cabin 402. Availability: 10:00-13:00.",
  "route": "structured",
  "sources": [
    {
      "id": "fac-001",
      "text": "...",
      "metadata": {"source": "structured"},
      "score": null
    }
  ]
}
```

If `SERVICE_API_KEY` is set, include:

```http
X-API-Key: <your-key>
```

## 4) Data

Edit `data/faculty.json` with real faculty details. Re-run `POST /ingest` after changes.

## 5) Notes

- If no strict match is found, service falls back to RAG.
- If info is missing in retrieved context, assistant should return:  
  `I don't have that information right now.`
- Public-agent controls:
  - Off-topic questions can be blocked (`ALLOW_OFF_TOPIC=false`).
  - Low-confidence retrieval is rejected using `MAX_RAG_DISTANCE`.
- Runtime note:
  - On Python `3.14+`, Chroma is disabled by the service for compatibility, so RAG endpoints return unavailable.
  - Use Python `3.12` or `3.13` for full RAG (`/ingest` + vector retrieval).

## 6) Production Environment Variables

- `AI_PROVIDER`: `openai` or `gemini`.
- `OPENAI_API_KEY`: required when `AI_PROVIDER=openai`.
- `GEMINI_API_KEY`: required when `AI_PROVIDER=gemini`.
- `SERVICE_API_KEY`: optional API key for `/query` and `/ingest`.
- `RATE_LIMIT_REQUESTS`: max requests in the rate window per client IP.
- `RATE_LIMIT_WINDOW_SECONDS`: rate window size.
- `MAX_QUESTION_CHARS`: hard max input length.
- `TOP_K`: RAG retrieval depth.
- `MAX_RAG_DISTANCE`: relevance threshold for accepted retrieval results.

## 7) Run Tests

```bash
pytest -q
```

## 8) Docker

```bash
docker build -t dept-ai-brain .
docker run --rm -p 8000:8000 --env-file .env dept-ai-brain
```

## 9) Voice Frontend (Next.js)

A simple voice UI is available in `frontend/`.

Run backend first (example port):

```bash
uvicorn app.main:app --reload --port 8001
```

Then run frontend:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://127.0.0.1:3000` and ask questions by voice.
