"""
ai_engine.py - AI Response Engine
===================================
Integrates Google Gemini AI for natural, human-like conversation.
Falls back to a polite default if the AI service is unavailable.
"""

import logging
import google.generativeai as genai  # type: ignore[import-untyped]
from config import GEMINI_API_KEY, GROQ_API_KEY, BUSINESS_NAME  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 🤖  AI Engine Configuration
# ──────────────────────────────────────────────

# System instruction that shapes the AI's personality
SYSTEM_PROMPT = f"""You are a friendly, professional customer support assistant for {BUSINESS_NAME}.

Rules:
- Be warm, helpful, and concise (keep replies under 150 words).
- Answer questions about the business naturally.
- If you don't know something specific about the business, say so politely and suggest the user contact support directly.
- Never make up facts about the business (prices, addresses, phone numbers).
- Use occasional emojis to keep the tone friendly but professional.
- Do NOT use markdown formatting like asterisks or underscores — use plain text only.
- If the user is just greeting you, greet them back warmly.
- If asked about something unrelated to business, you can still chat naturally but gently steer back to how you can help.
"""

# Track if AI is available and which provider is active
_ai_available = False
_ai_provider = None  # "gemini" or "groq"
_model = None        # Used for Gemini
_groq_api_key = None # Used for Groq


def init_ai() -> bool:
    """
    Initialize the AI model (Gemini or Groq).
    Returns True if successful, False otherwise.
    """
    global _ai_available, _model, _ai_provider, _groq_api_key

    # Check for Groq first
    if GROQ_API_KEY:
        _groq_api_key = GROQ_API_KEY
        _ai_provider = "groq"
        _ai_available = True
        logger.info("✅ Groq AI initialized successfully.")
        return True

    # Fallback to Gemini
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            _model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=SYSTEM_PROMPT,
            )
            _ai_provider = "gemini"
            _ai_available = True
            logger.info("✅ Gemini AI initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            _ai_available = False
            return False

    logger.warning(
        "⚠️  Neither GEMINI_API_KEY nor Groq_KEY/GROQ_API_KEY set — AI responses disabled. "
        "Bot will use keyword matching only."
    )
    _ai_available = False
    return False


async def get_ai_response(user_message: str) -> str | None:
    """
    Generate an AI response to the user's message using the active provider.

    Args:
        user_message: The text the user sent.

    Returns:
        The AI-generated response string, or None if AI is unavailable.
    """
    if not _ai_available:
        return None

    if _ai_provider == "gemini":
        if _model is None:
            return None
        model = _model
        try:
            response = model.generate_content(user_message)  # type: ignore[union-attr]
            if response.parts:
                return response.text.strip()
            else:
                preview = str(user_message)[:50]
                logger.warning(f"Gemini response blocked for: {preview}")
                return None
        except Exception as e:
            logger.error(f"Gemini AI response error: {e}")
            return None

    elif _ai_provider == "groq":
        import httpx
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {_groq_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 150
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        return content.strip()
                elif response.status_code in (400, 404):
                    # Fallback to llama3-8b-8192 if llama-3.3-70b-versatile is not available
                    payload["model"] = "llama3-8b-8192"
                    response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                    if response.status_code == 200:
                        data = response.json()
                        choices = data.get("choices", [])
                        if choices:
                            content = choices[0].get("message", {}).get("content", "")
                            return content.strip()
                logger.error(f"Groq API error (status {response.status_code}): {response.text}")
                return None
        except Exception as e:
            logger.error(f"Groq AI response error: {e}")
            return None

    return None
