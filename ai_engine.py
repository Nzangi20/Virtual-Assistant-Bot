"""
ai_engine.py - AI Response Engine
===================================
Integrates Google Gemini AI for natural, human-like conversation.
Falls back to a polite default if the AI service is unavailable.
"""

import logging
import google.generativeai as genai  # type: ignore[import-untyped]
from config import GEMINI_API_KEY, BUSINESS_NAME  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# 🤖  Gemini Configuration
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

# Track if AI is available
_ai_available = False
_model = None


def init_ai() -> bool:
    """
    Initialize the Gemini AI model.
    Returns True if successful, False otherwise.
    """
    global _ai_available, _model

    if not GEMINI_API_KEY:
        logger.warning(
            "⚠️  GEMINI_API_KEY not set — AI responses disabled. "
            "Bot will use keyword matching only."
        )
        return False

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        _ai_available = True
        logger.info("✅ Gemini AI initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini AI: {e}")
        _ai_available = False
        return False


async def get_ai_response(user_message: str) -> str | None:
    """
    Generate an AI response to the user's message.

    Args:
        user_message: The text the user sent.

    Returns:
        The AI-generated response string, or None if AI is unavailable.
    """
    if not _ai_available or _model is None:
        return None

    model = _model  # local ref for type narrowing

    try:
        response = model.generate_content(user_message)  # type: ignore[union-attr]

        # Safety check — Gemini may block some content
        if response.parts:
            return response.text.strip()
        else:
            preview = str(user_message)[:50]  # type: ignore[index]
            logger.warning(f"AI response blocked for: {preview}")
            return None

    except Exception as e:
        logger.error(f"AI response error: {e}")
        return None
