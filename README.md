# Python for AI

A learning workspace for Python and AI experiments, including:
- Basic Python practice scripts
- A FastAPI-based LLM gateway with multi-provider fallback
- Lab notebooks and assignment files for model training practice

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
