# ABES FastAPI Backend

This backend exposes the existing ABES RAG pipeline through FastAPI.

## Endpoints

- `GET /health`
- `POST /api/v1/retrieve`
- `POST /api/v1/chat`

The RAG components are initialized lazily on the first retrieval/chat request.

## Run

From the project root:

```powershell
uvicorn app.api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Environment

Required:

```env
GROQ_API_KEY=your_key
GROQ_MODEL=openai/gpt-oss-20b
```

Optional:

```env
ALLOWED_ORIGINS=http://localhost:3000
```

Never commit `.env` or API keys.
