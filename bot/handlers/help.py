def help() -> str:
    """Return list of commands."""
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - This help\n"
        "/health - Check backend status\n"
        "/labs - List all labs\n"
        "/scores <lab> - Get score for a lab (e.g., /scores lab-04)"
    )
