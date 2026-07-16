import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


def _load_dotenv_file() -> None:
    """Load key=value pairs from the repository root .env if present."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _split_csv(value: str, default: List[str]) -> List[str]:
    if not value:
        return default
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or default


_load_dotenv_file()


@dataclass(frozen=True)
class AppSettings:
    app_env: str = os.getenv("APP_ENV", "development").strip().lower()

    app_name: str = os.getenv("APP_NAME", "Communication Bridge AI")
    app_version: str = os.getenv("APP_VERSION", "1.1.0")

    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", str(60 * 24 * 7)))

    cors_origins: List[str] = field(
        default_factory=lambda: _split_csv(
            os.getenv("CORS_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080,http://localhost:8000"),
            ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:8000"],
        )
    )
    cors_allow_credentials: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

    default_confidence_threshold: float = float(os.getenv("DEFAULT_CONFIDENCE_THRESHOLD", "0.7"))

    def __post_init__(self) -> None:
        if self.jwt_secret_key.strip():
            return

        if self.app_env in {"development", "testing"}:
            object.__setattr__(self, "jwt_secret_key", "development-only-jwt-secret")
            return

        raise RuntimeError(
            "JWT_SECRET_KEY is required when APP_ENV is 'staging' or 'production'. "
            "Use APP_ENV=development or APP_ENV=testing only for non-production environments."
        )


settings = AppSettings()
