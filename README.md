# llm-gateway-engine

A high-throughput, asynchronous API Gateway for LLMs featuring failover routing, circuit breaking, and SSE streaming.

## High-Level Work

- **Asynchronous API Gateway** built with FastAPI for handling LLM chat completion requests.
- **Multi-provider failover routing** across Groq, OpenRouter, Gemini, and Deepseek endpoints with automatic fallback on failure.
- **Circuit breaking via cooldown timers** — providers that fail are temporarily skipped to avoid repeated requests to unhealthy endpoints.
- **Server-Sent Events (SSE) streaming** delivering OpenAI-style delta chunks to clients in real time.
- **Redis-backed response caching** to reduce latency and repeated provider calls for repeated prompts.
- **Health check endpoint** (`/health`) for monitoring gateway availability.
- **Streaming test client** (`test_client.py`) to verify end-to-end SSE responses.

## Project Structure

```
llm-gateway-engine/
├── gateway.py          # FastAPI streaming gateway with provider fallback, cooldown, and Redis cache
├── test_client.py      # SSE streaming client to test the gateway endpoint
├── learn_python.py     # Basic Python input/validation practice script
├── class.py            # Small Python class/function practice module
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── lab/                # Notebooks, assignment files, and datasets (ignored by git)
```

## Quick Start

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure provider keys

Set valid provider keys in `gateway.py` (the `PROVIDERS` list) before running real requests.

### 4. Run the gateway

```powershell
python gateway.py
```

The API starts on `http://localhost:8000`.

### 5. Test streaming response

In another terminal:

```powershell
python test_client.py
```

## API Endpoint

- `POST /v1/chat/completions`

Request body:

```json
{
  "message": "Your prompt text"
}
```

Response: Server-Sent Event (SSE) stream in OpenAI-style delta format.

### Health Check

- `GET /health` returns `{"status": "ok", "service": "llm-gateway"}`.

## Notes

- Update provider keys in `gateway.py` before production use.
- Redis is expected on `localhost:6379` for caching.
- The `lab/` folder contains learning assets and may include large files (ignored by git).

## Troubleshooting

- If `test_client.py` fails to connect, ensure `gateway.py` is running on port `8000`.
- If responses are empty, verify API keys and model names in `gateway.py`.
- If cache is not working, check that Redis is running and reachable.
