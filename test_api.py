import os
import sys
import asyncio
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

async def test_telegram_token(token):
    print("Testing Telegram Bot Token...")
    if not token:
        print("[FAIL] Telegram Bot Token is not set in .env")
        return False
    
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    print("[OK] Telegram Token is VALID!")
                    print(f"   Bot Name: {bot_info.get('first_name')}")
                    print(f"   Username: @{bot_info.get('username')}")
                    return True
            print(f"[FAIL] Telegram Token test failed: {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Error testing Telegram Token: {e}")
        return False

async def test_gemini_api(api_key):
    print("\nTesting Google Gemini API Key...")
    if not api_key:
        print("[INFO] GEMINI_API_KEY is not set in .env")
        return False

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # Using a simple sync call for quick test
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Hello! Respond with 'Gemini OK' if you hear me.")
        if response.text:
            print("[OK] Gemini API is VALID!")
            print(f"   Response: {response.text.strip()}")
            return True
        print("[FAIL] Gemini API returned empty response")
        return False
    except Exception as e:
        print(f"[FAIL] Gemini API test failed: {e}")
        return False

async def test_groq_api(api_key):
    print("\nTesting Groq API Key...")
    if not api_key:
        print("[INFO] Groq_KEY is not set in .env")
        return False

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": "Hello! Respond with 'Groq OK' if you hear me."}
        ],
        "max_tokens": 50
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    print("[OK] Groq API is VALID!")
                    print(f"   Response: {content.strip()}")
                    return True
            elif response.status_code == 404 or response.status_code == 400:
                # Try fallback model if llama-3.3-70b-versatile is not available
                payload["model"] = "llama3-8b-8192"
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        print("[OK] Groq API is VALID! (Fallback model)")
                        print(f"   Response: {content.strip()}")
                        return True
            print(f"[FAIL] Groq API test failed (Status {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Error testing Groq API: {e}")
        return False

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("Groq_KEY") or os.getenv("GROQ_API_KEY")

    telegram_ok = await test_telegram_token(bot_token)
    
    # Check if either API key works
    gemini_ok = await test_gemini_api(gemini_key)
    groq_ok = await test_groq_api(groq_key)
    
    print("\n" + "="*40)
    print("SUMMARY OF TESTS:")
    print(f"Telegram Bot Token: {'WORKING' if telegram_ok else 'FAILED'}")
    if gemini_key:
        print(f"Gemini API Key:     {'WORKING' if gemini_ok else 'FAILED'}")
    if groq_key:
        print(f"Groq API Key:       {'WORKING' if groq_ok else 'FAILED'}")
    
    if not gemini_key and not groq_key:
        print("[FAIL] No AI Engine API keys configured in .env.")
    elif groq_ok and not gemini_ok:
        print("\nNOTE: You have configured a Groq API Key, but the bot is currently set up to use Google Gemini.")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())
