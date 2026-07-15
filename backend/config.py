"""Backward-compatible config exports.

Prefer importing from `core.settings` in new code.
"""

try:
    from core.settings import settings
except ImportError:
    from backend.core.settings import settings


GEMINI_API_KEY = settings.gemini_api_key
