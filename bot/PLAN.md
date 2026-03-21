# Development Plan for Lab 7 Bot

## Overview
This project aims to build a Telegram bot that integrates with an LMS backend and an LLM service. The bot will support both command‑based interactions (`/start`, `/help`, `/health`, `/labs`, `/scores`) and free‑text queries that are routed to an LLM for answer generation.

## Architecture
The core design principle is **testable handlers**: all business logic is implemented in pure Python functions (in the `handlers/` directory) that receive input and return text. These functions do not depend on Telegram, allowing them to be invoked both by the Telegram bot and by a local `--test` mode. The entry point (`bot.py`) parses the command line: if `--test` is passed, it calls the appropriate handler directly and prints the result; otherwise, it starts a Telegram `Application` that uses the same handlers for each command.

## Task Breakdown
- **Task 1 (Scaffold)**: Set up the directory structure, `pyproject.toml`, configuration loader, and placeholder handlers. Implement `--test` mode to verify the skeleton works. Deploy the bot to Telegram and confirm `/start` responds.
- **Task 2 (Backend Integration)**: Replace placeholder handlers with real logic that calls the LMS API (`LMS_API_URL`, `LMS_API_KEY`). Implement `/labs` to fetch the list of labs, `/scores <lab>` to fetch the score for a specific lab, and `/health` to check backend availability.
- **Task 3 (Intent Routing)**: Add support for free‑text queries. When a user sends a message that is not a command, route it through an LLM (using `LLM_API_KEY`) to decide whether to answer directly or delegate to backend commands.
- **Task 4 (Deployment)**: Finalize the bot, ensure it runs as a systemd service on the VM, and write integration tests.

## Technology Stack
- **Python 3.10+** with `uv` as the package manager.
- `python-telegram-bot` for Telegram integration.
- `python-dotenv` for environment configuration.
- `requests` for HTTP calls to the LMS backend.
- `openai` (or similar) for LLM integration (Task 3).

## Testing Strategy
- **Unit tests** for each handler function, mocking external HTTP calls.
- **Test mode** (`--test`) allows manual verification without Telegram.
- After each task, the bot is deployed and tested in Telegram to ensure real‑world functionality.

## Deployment
The bot runs on the lab VM inside a virtual environment managed by `uv`. Environment secrets are stored in `.env.bot.secret` (ignored by Git). A systemd service or a simple `nohup` process keeps the bot alive. Logs are written to `bot.log` for debugging.
