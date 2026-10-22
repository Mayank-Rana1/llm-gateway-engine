import base64, json, time, hmac, hashlib, struct, requests

email = "mrana171mr@gmail.com"
gist_url = "https://gist.github.com/Mayank-Rana1/2e538f8463738f71161304f311911233"

def gen_totp(email, counter):
    secret = (email + "HENNGECHALLENGE004").encode()
    msg = struct.pack(">Q", counter)
    hs = hmac.new(secret, msg, hashlib.sha512).digest()
    offset = hs[-1] & 0x0F
    binary = ((hs[offset] & 0x7f) << 24) | ((hs[offset+1] & 0xff) << 16) | ((hs[offset+2] & 0xff) << 8) | (hs[offset+3] & 0xff)
    return str(binary % 10**10).zfill(10)

body = {
  "github_url": gist_url,
  "contact_email": email,
  "solution_language": "python"
}

url = "https://api.challenge.hennge.com/challenges/backend-recursion/004"

for delta in [0, -1, 1]:
    counter = int(time.time() // 30) + delta
    otp = gen_totp(email, counter)
    token = base64.b64encode(f"{email}:{otp}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers, data=json.dumps(body))
    print(f"Trying counter {counter} otp {otp} -> {r.status_code} {r.text}")
    if r.status_code == 200:
        break