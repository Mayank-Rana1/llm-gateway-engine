import requests
import json

url="http://localhost:8000/v1/chat/completions"

payload={
    "message": "Make a small story about rain and snow"
}
print("Sending request to server..")
with requests.post(url,json=payload, stream=True) as response:
    response.raise_for_status()
    for chunk in response.iter_lines(decode_unicode=True):
        if not chunk:
            continue
        
        deco_line=chunk.strip()

        if deco_line.startswith("data: "):
            json_string= deco_line[6:]

            if json_string=="[DONE]":
                break

            try:
                chunk_data= json.loads(json_string)
                token= chunk_data['choices'][0]['delta'].get('content','')

                print(token, end="", flush=True)

            except (json.JSONDecodeError, KeyError, IndexError):
                pass

print("\n\n================================")
