"""
config.py - Configuration Module
=================================
Loads environment variables and stores all bot settings.
Easy to customize for different business clients.
"""

import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# ──────────────────────────────────────────────
# 🔑  Bot Token (REQUIRED)
# ──────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN not found! "
        "Create a .env file with: BOT_TOKEN=your_token_here"
    )

# ──────────────────────────────────────────────
# 📂  Database
# ──────────────────────────────────────────────
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")

# ──────────────────────────────────────────────
# 🧠  AI Engine (Google Gemini)
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ──────────────────────────────────────────────
# 🏢  Business Information (customize per client)
# ──────────────────────────────────────────────
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Our Business")

WELCOME_MESSAGE = (
    f"👋 Welcome to *{BUSINESS_NAME}*!\n\n"
    "I'm your virtual assistant. I can help you with:\n"
    "• Our services & pricing\n"
    "• Contact information\n"
    "• Location details\n\n"
    "Use the menu below or just type your question!"
)

SERVICES_TEXT = os.getenv(
    "SERVICES_TEXT",
    (
        "📌 *Our Services*\n\n"
        "1️⃣  Web Development\n"
        "2️⃣  Mobile App Development\n"
        "3️⃣  UI/UX Design\n"
        "4️⃣  Digital Marketing\n"
        "5️⃣  IT Consulting\n\n"
        "💬 Reply with a service number for more details, "
        "or tap *Pricing* to see our rates."
    ),
)

PRICING_TEXT = os.getenv(
    "PRICING_TEXT",
    (
        "💰 *Pricing Plans*\n\n"
        "🟢 *Starter* — $199/mo\n"
        "   Basic website + hosting\n\n"
        "🔵 *Professional* — $499/mo\n"
        "   Custom site + SEO + support\n\n"
        "🟣 *Enterprise* — Custom quote\n"
        "   Full-stack solution + priority support\n\n"
        "📩 Contact us for a tailored quote!"
    ),
)

CONTACT_TEXT = os.getenv(
    "CONTACT_TEXT",
    (
        "📞 *Contact Us*\n\n"
        "📧 Email: info@business.com\n"
        "📱 Phone: +1 (555) 123-4567\n"
        "🌐 Website: www.business.com\n"
        "🕐 Hours: Mon-Fri 9 AM – 6 PM\n\n"
        "We typically respond within 1 hour!"
    ),
)

LOCATION_TEXT = os.getenv(
    "LOCATION_TEXT",
    (
        "📍 *Our Location*\n\n"
        "🏢 123 Business Avenue, Suite 100\n"
        "     New York, NY 10001\n\n"
        "🗺️ [Open in Google Maps]"
        "(https://maps.google.com)\n\n"
        "Free parking available for visitors!"
    ),
)

HELP_TEXT = (
    "❓ *Help & Support*\n\n"
    "Here's what I can do:\n\n"
    "• /start — Restart the bot & show the menu\n"
    "• /menu  — Show the main menu\n"
    "• /help  — Show this help message\n\n"
    "You can also type naturally:\n"
    '  → "hi" or "hello" to say hi\n'
    '  → "services" to see what we offer\n'
    '  → "price" to view pricing\n'
    '  → "location" to find us\n\n'
    "🤖 Can't find what you need? Type your question "
    "and our team will follow up!"
)

# ──────────────────────────────────────────────
# 📝  Logging
# ──────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
