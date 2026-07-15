from __future__ import annotations

import logging
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from core.settings import settings
except ImportError:
    from backend.core.settings import settings


logger = logging.getLogger(__name__)


class GeminiClient:
    """Shared Gemini client with lazy model initialization."""

    _shared_model = None
    _shared_model_name = None

    def __init__(self, model_name: Optional[str] = None) -> None:
        self.api_key = settings.gemini_api_key
        self.model_name = model_name or settings.gemini_model
        self.model = None

        if not self.api_key:
            logger.warning("Gemini API key is not configured; falling back to rule/template logic")
            return

        if genai is None:
            logger.warning("google-generativeai is not installed; falling back to rule/template logic")
            return

        try:
            genai.configure(api_key=self.api_key)
            if (
                GeminiClient._shared_model is not None
                and GeminiClient._shared_model_name == self.model_name
            ):
                self.model = GeminiClient._shared_model
                return

            self.model = self._build_model(self.model_name)
            GeminiClient._shared_model = self.model
            GeminiClient._shared_model_name = self.model_name
        except Exception as exc:
            logger.exception("Failed to initialize Gemini model: %s", exc)
            self.model = None

    @staticmethod
    def _build_model(model_name: str):
        candidates = [model_name, f"models/{model_name}", "models/gemini-pro"]
        last_error = None

        for candidate in candidates:
            try:
                return genai.GenerativeModel(candidate)
            except Exception as exc:
                last_error = exc

        if last_error:
            raise last_error
        raise RuntimeError("Unable to initialize Gemini model")

    def is_available(self) -> bool:
        return self.model is not None
