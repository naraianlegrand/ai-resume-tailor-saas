import os
import json
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_call():
    # 1. Check Key
    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"[1] Checking API key presence... {'FOUND' if api_key else 'MISSING'}")
    
    # 2. Build direct anonymous REST payload
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": "Say hello from the cloud!"}]}]
    }
    
    print("[2] Dispatching clean REST client over the wire...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            print(f"[3] Network response received. Status: {response.status_code}")
            if response.status_code == 200:
                print("[SUCCESS] Gemini says:", response.json()['candidates'][0]['content']['parts'][0]['text'].strip())
            else:
                print("[ERROR] Payload details:", response.text)
    except Exception as e:
        print(f"[CRASH] System error intercepted: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_call())