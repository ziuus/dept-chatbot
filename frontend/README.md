# Frontend (Next.js Voice UI)

Simple voice-first UI for the department chatbot backend.

## 1) Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

If your backend requires `SERVICE_API_KEY`, set `BACKEND_API_KEY` in `.env.local`.

## 2) Run

```bash
npm run dev
```

Open: `http://127.0.0.1:3000`

## 3) Flow

- Click **Start Voice Question**
- Speak your query
- Frontend transcribes speech in browser (Web Speech API)
- Sends question to `/api/ask` (Next server route)
- Route forwards to FastAPI `/query`
- Answer text is displayed and spoken back via browser TTS
