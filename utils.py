import html

def sanitize_message(message: str) -> str:
    return html.escape(message)
