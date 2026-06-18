import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from contextlib import asynccontextmanager

import uvicorn
import hashlib
import time
import json


COOLDOWN_TIME = 60

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
    {
        "name": "Deepseek",
        "type": "openai",
        "url": "https://q5dh1rfszfym23hj.us-east-2.aws.endpoints.huggingface.cloud/v1/chat/completions",
        "key": "not-needed",
        "model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "cooldown": 0,
    },
]

#------------------------------------------#

class UserPayload(BaseModel):
    message:str


redis_client: redis.Redis =None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client= redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=False,
        socket_connect_timeout=0.005,
        socket_timeout=0.005)
    yield
    await redis_client.aclose()

app=FastAPI(lifespan=lifespan)

# Tell the server to accept requests from web browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you lock this down to your real website URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def make_cach_key(prompt:str)-> str:
    nor_prompt=prompt.strip()
    hashed=hashlib.sha256(nor_prompt.encode("utf-8")).hexdigest()
    return f"cache:{hashed}"

async def re_stream_bytes(catch_byt: bytes):
    print("[CACHE HIT] Re-streaming response from redis..")
    yield catch_byt
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

@app.post("/v1/chat/completions")
async def handel_chat_request(data: UserPayload):
    print("Received a message:",data.message)

    cache_key=make_cach_key(data.message)

    cached_payload = None
    try:
        cached_payload= await redis_client.get(cache_key)
    except Exception as exc:
        print(f"Redis Error (No cache): {exc}")
    if(cached_payload):
        return StreamingResponse(re_stream_bytes(cached_payload), media_type="text/event-stream")

    print("Cache Miss Sending request to api")
    async def stream_as_get():
        accumulated_chunks=[]

        async with httpx.AsyncClient() as client:
            now=time.time()
            for provider in PROVIDERS:
                if provider["cooldown"]>now:
                    print(f"Skipping {provider['name']} (cooldown active)")
                    continue

                print(f"Trying provider: {provider['name']}...")
                try:
                    if provider['type']=="openai":
                        async for chunk in send_openai(client,provider,data.message):
                            accumulated_chunks.append(chunk)
                            yield chunk
                    else :
                        async for chunk in send_gemini(client,provider,data.message):
                            accumulated_chunks.append(chunk)
                            yield chunk
                    if accumulated_chunks:
                        try:
                            full_payload=b"".join(accumulated_chunks)
                            await redis_client.set(cache_key,full_payload,ex=600)
                            print("Response saved to Redis!")
                        except:
                            print(f"Redis Save Error: {Exception}")
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


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "llm-gateway"}


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)