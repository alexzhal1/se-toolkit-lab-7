#!/usr/bin/env python3
"""
Entry point for the Telegram bot. Supports --test mode for offline testing.
"""
import sys
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from handlers import start, help, health, labs, scores
from services.llm_router import route
from config import Config


# ----------------------------------------------------------------------
# Inline keyboard buttons
# ----------------------------------------------------------------------
START_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Available labs", callback_data="query:what labs are available?"),
        InlineKeyboardButton("Health check", callback_data="cmd:/health"),
    ],
    [
        InlineKeyboardButton("Scores lab-04", callback_data="cmd:/scores lab-04"),
        InlineKeyboardButton("Top students", callback_data="query:who are the top 5 students in lab 4?"),
    ],
    [
        InlineKeyboardButton("Help", callback_data="cmd:/help"),
    ],
])


# ----------------------------------------------------------------------
# Helper: route commands to the appropriate handler
# ----------------------------------------------------------------------
def handle_command(command: str, arg: str = None) -> str:
    """Call the correct handler function and return its string response."""
    if command == "/start":
        return start()
    elif command == "/help":
        return help()
    elif command == "/health":
        return health()
    elif command == "/labs":
        return labs()
    elif command == "/scores":
        return scores(arg)
    else:
        return None  # not a known command


# ----------------------------------------------------------------------
# Test mode: run a single command and print the result
# ----------------------------------------------------------------------
def test_mode(command_str: str):
    """
    Parse the command string and print the response.
    Slash commands go to handlers; plain text goes to LLM router.
    """
    parts = command_str.strip().split()
    if not parts:
        print("No command provided.")
        sys.exit(1)

    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else None

    # Slash commands go to handlers
    if cmd.startswith("/"):
        response = handle_command(cmd, arg)
        if response is not None:
            print(response)
            sys.exit(0)
        # Unknown slash command
        print(f"Unknown command: {cmd}. Use /help to see available commands.")
        sys.exit(0)

    # Plain text goes to LLM router
    response = route(command_str)

    print(response)
    sys.exit(0)


# ----------------------------------------------------------------------
# Telegram handlers
# ----------------------------------------------------------------------
async def tg_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start(), reply_markup=START_KEYBOARD)


async def tg_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(help())


async def tg_health(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(health())


async def tg_labs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(labs())


async def tg_scores(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lab_arg = ctx.args[0] if ctx.args else None
    await update.message.reply_text(scores(lab_arg))


async def tg_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle plain text messages via LLM router."""
    text = update.message.text
    response = route(text)
    await update.message.reply_text(response)


async def tg_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("cmd:"):
        cmd_str = data[4:]
        parts = cmd_str.strip().split()
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None
        response = handle_command(cmd, arg)
        if response:
            await query.message.reply_text(response)
    elif data.startswith("query:"):
        user_query = data[6:]
        response = route(user_query)
        await query.message.reply_text(response)


# ----------------------------------------------------------------------
# Telegram mode: start the bot
# ----------------------------------------------------------------------
def telegram_mode():
    """Start the Telegram bot using the provided token."""
    if not Config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Set it in .env.bot.secret")

    app = Application.builder().token(Config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", tg_start))
    app.add_handler(CommandHandler("help", tg_help))
    app.add_handler(CommandHandler("health", tg_health))
    app.add_handler(CommandHandler("labs", tg_labs))
    app.add_handler(CommandHandler("scores", tg_scores))
    app.add_handler(CallbackQueryHandler(tg_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tg_message))

    print("Bot is starting...")
    app.run_polling()


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if len(sys.argv) < 3:
            print("Usage: bot.py --test <command>")
            sys.exit(1)
        test_mode(sys.argv[2])
    else:
        Config.validate()
        telegram_mode()


if __name__ == "__main__":
    main()
