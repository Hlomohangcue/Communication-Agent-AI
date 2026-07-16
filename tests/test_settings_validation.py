import importlib
import sys

import pytest


SETTINGS_MODULES = ["backend.core.settings", "core.settings"]


def _unload_settings_modules() -> None:
    for module_name in SETTINGS_MODULES:
        sys.modules.pop(module_name, None)


def _import_settings_module():
    _unload_settings_modules()
    return importlib.import_module("backend.core.settings")


def test_development_allows_default_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("JWT_SECRET_KEY", "")

    module = _import_settings_module()

    assert module.settings.jwt_secret_key == "development-only-jwt-secret"


def test_testing_allows_default_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("JWT_SECRET_KEY", "")

    module = _import_settings_module()

    assert module.settings.jwt_secret_key == "development-only-jwt-secret"


def test_staging_requires_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("JWT_SECRET_KEY", "")

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY is required"):
        _import_settings_module()


def test_production_requires_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "")

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY is required"):
        _import_settings_module()
