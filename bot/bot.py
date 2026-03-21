#!/usr/bin/env python3
"""
Entry point for the Telegram bot. Supports --test mode for offline testing.
"""
import sys
from telegram.ext import Application, CommandHandler
from handlers import start, help, health, labs, scores
from config import Config


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
        return f"Unknown command: {command}. Use /help to see available commands."


# ----------------------------------------------------------------------
# Test mode: run a single command and print the result
# ----------------------------------------------------------------------
def test_mode(command_str: str):
    """
    Parse the command string (e.g., "/scores lab-04") and print the response.
    Exits with 0 on success, 1 on error.
    """
    parts = command_str.strip().split()
    if not parts:
        print("No command provided.")
        sys.exit(1)

    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else None

    response = handle_command(cmd, arg)
    print(response)
    sys.exit(0)


# ----------------------------------------------------------------------
# Telegram mode: start the bot (synchronous)
# ----------------------------------------------------------------------
def telegram_mode():
    """Start the Telegram bot using the provided token."""
    if not Config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN is missing. Set it in .env.bot.secret")

    app = Application.builder().token(Config.BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", lambda update, ctx: update.message.reply_text(start())))
    app.add_handler(CommandHandler("help", lambda update, ctx: update.message.reply_text(help())))
    app.add_handler(CommandHandler("health", lambda update, ctx: update.message.reply_text(health())))
    app.add_handler(CommandHandler("labs", lambda update, ctx: update.message.reply_text(labs())))
    app.add_handler(CommandHandler("scores", lambda update, ctx: update.message.reply_text(scores(ctx.args[0] if ctx.args else None))))

    print("Bot is starting...")
    app.run_polling()  # синхронный метод, не требует asyncio.run()


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
        Config.validate()      # проверяем LMS переменные (BOT_TOKEN проверится в telegram_mode)
        telegram_mode()


if __name__ == "__main__":
    main()
