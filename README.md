# Python for AI

A learning workspace for Python and AI experiments, including:
- Basic Python practice scripts
- A FastAPI-based LLM gateway with multi-provider fallback
- Lab notebooks and assignment files for model training practice

## Prerequisites

- Python 3.10+
- Redis running locally on `localhost:6379`
- Internet access for provider API calls

## Project Structure

- `gateway.py`: FastAPI streaming gateway with provider fallback and Redis cache
- `test_client.py`: Simple streaming client to test the gateway endpoint
- `learn_python.py`: Basic Python input/validation practice script
- `class.py`: Small Python class/function practice module
- `lab/`: Notebooks, assignment files, and datasets
- `requirements.txt`: Python dependencies

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

### 2.1 Configure provider keys

Set valid provider keys in `gateway.py` before running real requests.

### 3. Run the gateway

```powershell
python gateway.py
```

The API starts on `http://localhost:8000`.

### 4. Test streaming response

In another terminal:

```powershell
python test_client.py
```

## API Endpoint

- `POST /v1/chat/completions`
- Request body:

```json
{
  "message": "Your prompt text"
}
```

- Response: Server-Sent Event (SSE) stream in OpenAI-style delta format.

## Notes

- Update provider keys in `gateway.py` before production use.
- Redis is expected on `localhost:6379` for caching.
- The `lab/` folder contains learning assets and may include large files.

## Troubleshooting

- If `test_client.py` fails to connect, ensure `gateway.py` is running on port `8000`.
- If responses are empty, verify API keys and model names in `gateway.py`.
- If cache is not working, check that Redis is running and reachable.
