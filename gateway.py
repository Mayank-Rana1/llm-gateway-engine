import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import time
import json


COOLDOWN_TIME = 60

app=FastAPI()


# Tell the server to accept requests from web browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you lock this down to your real website URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CONFIG ---------------- #

PROVIDERS = [
    {
        "name": "Groq-1",
        "type": "openai",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": "api-key",
        "model": "llama-3.1-8b-instant",
        "cooldown": 0,
    },
    {
        "name": "Groq-2",
        "type": "openai",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": "GROQ_API_KEY_2",
        "model": "llama-3.1-8b-instant",
        "cooldown": 0,
    },
    {
        "name": "OpenRouter",
        "type": "openai",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key": "api-key",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "cooldown": 0,
    },
    {
        "name": "Gemini",
        "type": "gemini",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse&key={key}",
        "key": "api-key",
        "model": "gemini-3.1-flash-lite",
        "cooldown": 0,
    },
]

#------------------------------------------#

async def send_openai(client,provider,message):
    async with client.stream(
        "POST",
        provider["url"],
        headers={
            "Authorization": f"Bearer {provider['key']}",
            "content-type": "application/json"
        },
        json={
            "model": provider["model"],
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "stream": True
        }
    ) as response:
        response.raise_for_status()

        async for line in response.aiter_bytes():
            yield line

#----------------------#

async def send_gemini(client,provider,message):

    request_url = provider['url'].format(model=provider['model'], key=provider['key'])

    async with client.stream(
        "POST",
        request_url,
        headers={
            "content-type": "application/json"
        },
        json={
            "contents": [
                {
                    "parts": [{"text": message}]
                }
            ]
        }
    ) as response:
        response.raise_for_status()

        async for line in response.aiter_lines():
            if not line.startswith("data: "):
                continue
            raw_json=line[6:]

            try:
                gemini_data = json.loads(raw_json)
                text_chunk = gemini_data["candidates"][0]["content"]["parts"][0]["text"]
                fake_openai_payload = {
                    "choices": [{"delta":{"content": text_chunk}}]
                }

                yield f"data: {json.dumps(fake_openai_payload)}\n\n".encode('utf-8')
            except httpx.HTTPStatusError as e:
                # This will print the EXACT reason Google rejected the request!
                print(f"❌ {provider['name']} failed! Status: {e.response.status_code}")
                print(f"Google's secret error message: {e.response.text}")
                provider["cooldown"] = time.time() + COOLDOWN_TIME
            except Exception as e:
                # This catches non-HTTP errors (like your internet being down)
                print(f"❌ {provider['name']} failed! Error: {e}")
                provider["cooldown"] = time.time() + COOLDOWN_TIME
        yield b'data: [DONE]\n\n'


#------------------------------------------#

class UserPayload(BaseModel):
    message:str

@app.post("/v1/chat/completions")
async def handel_chat_request(data: UserPayload):
    print("Received a message:",data.message,"\nSending request to api")

    async def stream_as_get():
        async with httpx.AsyncClient() as client:
            now=time.time()
            for provider in PROVIDERS:
                if provider["cooldown"]>now:
                    continue

                print(f"Trying provider: {provider['name']}...")
                try:
                    if provider['type']=="openai":
                        async for chunk in send_openai(client,provider,data.message):
                            yield chunk
                    else :
                        async for chunk in send_gemini(client,provider,data.message):
                            yield chunk
                    return
                except httpx.HTTPStatusError as e:
                    # We just print the status code, no .text!
                    print(f"❌ {provider['name']} failed! Status: {e.response.status_code}")
                    provider["cooldown"] = time.time() + COOLDOWN_TIME
                    
                except Exception as e:
                    print(f"❌ {provider['name']} failed! Error: {e}")
                    provider["cooldown"] = time.time() + COOLDOWN_TIME
        yield b'data: {"choices":[{"delta":{"content":"No provider available"}}]}\n\n'
        yield b"data: [DONE]\n\n"        

    return StreamingResponse(stream_as_get(),media_type="text/event-stream")


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)