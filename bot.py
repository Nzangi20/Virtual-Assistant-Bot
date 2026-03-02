"""
bot.py - Telegram Customer Support Bot
========================================
Main entry point for the bot.
Handles commands, button callbacks, and keyword-based auto-replies.

Usage:
    python bot.py
"""

import asyncio
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

import config
import database
import ai_engine

# ──────────────────────────────────────────────
# 🪵  Logging Setup
# ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)


# ╔══════════════════════════════════════════════╗
# ║           HELPER FUNCTIONS                   ║
# ╚══════════════════════════════════════════════╝

def build_main_menu() -> InlineKeyboardMarkup:
    """Build the main menu inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📌 Services", callback_data="services"),
            InlineKeyboardButton("💰 Pricing", callback_data="pricing"),
        ],
        [
            InlineKeyboardButton("📞 Contact", callback_data="contact"),
            InlineKeyboardButton("📍 Location", callback_data="location"),
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def log_user_and_message(update: Update, text: str | None = None) -> None:
    """Save user info and the message to the database."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    if user:
        database.save_user(
            chat_id=chat_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    if text:
        database.save_message(chat_id=chat_id, message_text=text)


# ╔══════════════════════════════════════════════╗
# ║           COMMAND HANDLERS                   ║
# ╚══════════════════════════════════════════════╝

async def start_command(update: Update, context) -> None:
    """Handle /start — send a welcome message with the main menu."""
    log_user_and_message(update, "/start")

    await update.message.reply_text(
        config.WELCOME_MESSAGE,
        parse_mode="Markdown",
        reply_markup=build_main_menu(),
    )
    logger.info(f"/start from {update.effective_user.first_name}")


async def menu_command(update: Update, context) -> None:
    """Handle /menu — re-display the main menu."""
    log_user_and_message(update, "/menu")

    await update.message.reply_text(
        "📋 *Main Menu*\nChoose an option below:",
        parse_mode="Markdown",
        reply_markup=build_main_menu(),
    )


async def help_command(update: Update, context) -> None:
    """Handle /help — display help information."""
    log_user_and_message(update, "/help")

    await update.message.reply_text(
        config.HELP_TEXT,
        parse_mode="Markdown",
    )


# ╔══════════════════════════════════════════════╗
# ║           BUTTON CALLBACK HANDLER            ║
# ╚══════════════════════════════════════════════╝

# Map callback_data values to their response text
MENU_RESPONSES: dict[str, str] = {
    "services": config.SERVICES_TEXT,
    "pricing":  config.PRICING_TEXT,
    "contact":  config.CONTACT_TEXT,
    "location": config.LOCATION_TEXT,
    "help":     config.HELP_TEXT,
}


async def button_callback(update: Update, context) -> None:
    """Handle inline button presses from the main menu."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    choice = query.data
    response_text = MENU_RESPONSES.get(choice, "❓ Unknown option.")

    log_user_and_message(update, f"[Button] {choice}")

    await query.message.reply_text(
        response_text,
        parse_mode="Markdown",
        reply_markup=build_main_menu(),  # Re-attach menu
    )
    logger.info(f"Button '{choice}' pressed by {update.effective_user.first_name}")


# ╔══════════════════════════════════════════════╗
# ║        KEYWORD AUTO-REPLY HANDLER            ║
# ╚══════════════════════════════════════════════╝

# Define keyword → response mappings
# Each tuple: (list of trigger keywords, response text)
KEYWORD_MAP: list[tuple[list[str], str]] = [
    (
        ["hello", "hi", "hey", "good morning", "good evening"],
        f"👋 Hello! Welcome to *{config.BUSINESS_NAME}*.\n"
        "How can I help you today?\n\n"
        "Use the menu below to explore our services!",
    ),
    (
        ["price", "cost", "pricing", "how much", "rate", "fee"],
        config.PRICING_TEXT,
    ),
    (
        ["service", "services", "what do you do", "offer", "product"],
        config.SERVICES_TEXT,
    ),
    (
        ["location", "address", "where", "find you", "directions", "map"],
        config.LOCATION_TEXT,
    ),
    (
        ["contact", "phone", "email", "call", "reach"],
        config.CONTACT_TEXT,
    ),
    (
        ["help", "support", "assist"],
        config.HELP_TEXT,
    ),
    (
        ["thank", "thanks", "thx"],
        "😊 You're welcome! Is there anything else I can help with?",
    ),
]


async def handle_message(update: Update, context) -> None:
    """
    Handle regular text messages.
    Checks for keyword matches and replies accordingly.
    If no keyword matches, sends a default fallback response.
    """
    text = update.message.text
    log_user_and_message(update, text)

    # Normalize the message for keyword matching
    lower_text = text.lower().strip()

    # Check each keyword group for a match
    for keywords, response in KEYWORD_MAP:
        if any(kw in lower_text for kw in keywords):
            await update.message.reply_text(
                response,
                parse_mode="Markdown",
                reply_markup=build_main_menu(),
            )
            logger.info(
                f"Keyword match for '{lower_text}' "
                f"from {update.effective_user.first_name}"
            )
            return

    # No keyword matched — try AI response
    ai_response = await ai_engine.get_ai_response(text)

    if ai_response:
        await update.message.reply_text(
            ai_response,
            reply_markup=build_main_menu(),
        )
        logger.info(
            f"AI response for '{lower_text[:40]}' "
            f"from {update.effective_user.first_name}"
        )
    else:
        # AI unavailable — send a friendly fallback
        fallback = (
            "🤔 I'm not sure I understand that.\n\n"
            "Try one of these:\n"
            "• Tap a button in the menu below\n"
            "• Type *help* for a list of commands\n"
            "• Type *services* or *pricing*\n\n"
            "Your message has been noted, and our team will follow up if needed!"
        )
        await update.message.reply_text(
            fallback,
            parse_mode="Markdown",
            reply_markup=build_main_menu(),
        )
        logger.info(
            f"No keyword match for '{lower_text}' "
            f"from {update.effective_user.first_name}"
        )


# ╔══════════════════════════════════════════════╗
# ║           ERROR HANDLER                      ║
# ╚══════════════════════════════════════════════╝

async def error_handler(update: Update, context) -> None:
    """Log errors and notify the user gracefully."""
    logger.error(f"Update {update} caused error: {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ Something went wrong. Please try again later.\n"
            "If the issue persists, contact our support team.",
        )


# ╔══════════════════════════════════════════════╗
# ║              MAIN                            ║
# ╚══════════════════════════════════════════════╝

def main() -> None:
    """Initialize the database, build the application, and start polling."""
    # 1. Initialize the database
    database.init_db()
    logger.info("📦 Database ready.")

    # 2. Initialize AI engine
    ai_engine.init_ai()

    # 2. Build the Telegram bot application
    app = Application.builder().token(config.BOT_TOKEN).build()

    # 3. Register handlers (order matters!)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 4. Register the error handler
    app.add_error_handler(error_handler)

    # 5. Start the bot (Python 3.14+ requires an explicit event loop)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.info(f"🤖 {config.BUSINESS_NAME} Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
