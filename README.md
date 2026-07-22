# llm-gateway-engine

A high-throughput, asynchronous API Gateway for Large Language Models (LLMs) built with Python and FastAPI. The engine serves as an enterprise middleware layer that provides unified streaming interfaces, automated failover routing, and resilient error handling across multiple AI providers.

---

## Architecture Overview

Modern applications requiring LLM integration face challenges regarding API rate limits, provider downtime, and protocol variations. The `llm-gateway-engine` decouples client applications from direct provider APIs by managing routing, error handling, and protocol normalization at the network layer.

### Key Capabilities

* **Asynchronous Request Concurrency**: Built on Python's `asyncio` and `httpx` to handle hundreds of concurrent requests non-blockingly during streaming I/O operations.
* **Resilient Failover Routing**: Implements automated circuit breaking and cooldown logic. If a primary provider returns a 4xx or 5xx error, traffic instantly reroutes to secondary providers without interrupting client execution.
* **Server-Sent Events (SSE) Normalization**: Normalizes disparate vendor streaming formats (e.g., Google Gemini, OpenAI, Groq) into a standardized SSE stream.
* **Network-Level Exception Management**: Traps low-level HTTP status codes, socket timeouts, and connection drops to protect upstream clients from cascading failures.

---

## Tech Stack

* **Core Framework**: Python 3.10+, FastAPI, Uvicorn
* **Network Layer**: `httpx` (Asynchronous HTTP client)
* **Data Validation**: Pydantic v2
* **Protocols**: HTTP/1.1, Server-Sent Events (SSE), JSON

---

## Architectural Roadmap

This repository reflects Phase 1 (Core Gateway Engine). Future architectural phases include:

1. **Phase 1: Asynchronous Proxy & Circuit Breaking** *(Current)*
   * Multi-provider routing (Gemini, Groq, OpenRouter).
   * Automatic failover and provider cooldown tracking.
   * Universal SSE chunk formatting.

2. **Phase 2: Semantic Caching Layer** *(Planned)*
   * Integration with Redis for exact-match query caching.
   * Integration with Qdrant Vector Database for cosine similarity matching.
   * Reduction of duplicate LLM API costs and query latencies (<15ms cache hits).

3. **Phase 3: Containerization & Cloud Infrastructure** *(Planned)*
   * Multi-container deployment using Docker and Docker Compose.
   * PII detection and redaction middleware (Microsoft Presidio integration).

---

## Getting Started

### Prerequisites

* Python 3.10 or higher
* Valid API keys for supported providers (Google Gemini, Groq, OpenRouter)

### Installation

1. Clone the repository:

```bash
git clone [https://github.com/YOUR_USERNAME/llm-gateway-engine.git](https://github.com/YOUR_USERNAME/llm-gateway-engine.git)
cd llm-gateway-engine

```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

```

3. Install required dependencies:

```bash
pip install -r requirements.txt

```

4. Configure environment variables:
Copy `.env.example` to `.env` and fill in your API credentials:

```bash
cp .env.example .env

```

5. Launch the gateway server:

```bash
uvicorn gateway:app --reload --port 8000

```

---

## System Metrics & Benchmark Goals

| Component | Target Metric | Engineering Objective |
| --- | --- | --- |
| **Failover Overhead** | < 50ms | Instant transition on provider failure |
| **Streaming Latency** | Near Zero Overhead | Direct pass-through of SSE chunks |
| **I/O Concurrency** | High Throughput | Non-blocking socket handling via `asyncio` |

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
```

```
