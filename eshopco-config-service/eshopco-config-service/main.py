import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent

DEFAULTS: dict[str, Any] = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

app = FastAPI(title="eShopCo Effective Config API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


def normalize_key(key: str) -> str:
    key = key.strip()
    if key.upper() == "NUM_WORKERS":
        return "workers"
    if key.startswith("APP_"):
        key = key[4:]
    return key.lower()


def coerce(key: str, value: Any) -> Any:
    text = str(value).strip()
    if key in ("port", "workers"):
        return int(text)
    if key == "debug":
        return text.lower() in {"true", "1", "yes", "on"}
    return text


def apply_layer(config: dict[str, Any], layer: dict[str, Any]) -> None:
    for raw_key, value in layer.items():
        if value is None:
            continue
        key = normalize_key(str(raw_key))
        if key in DEFAULTS:
            config[key] = coerce(key, value)


def load_config() -> dict[str, Any]:
    config = DEFAULTS.copy()

    env_name = os.getenv("APP_ENV", "development")
    yaml_path = BASE_DIR / f"config.{env_name}.yaml"
    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as file:
            yaml_layer = yaml.safe_load(file) or {}
        apply_layer(config, yaml_layer)

    dotenv_layer = dotenv_values(BASE_DIR / ".env")
    apply_layer(config, dotenv_layer)

    # OS environment variables override .env; APP_ENV selects the YAML file
    # and is not itself an application config field.
    os_layer = {
        key: value for key, value in os.environ.items()
        if key.startswith("APP_") and key != "APP_ENV"
    }
    apply_layer(config, os_layer)
    return config


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])) -> dict[str, Any]:
    config = load_config()
    for item in set:
        if "=" not in item:
            continue
        raw_key, value = item.split("=", 1)
        key = normalize_key(raw_key)
        if key in DEFAULTS:
            config[key] = coerce(key, value)
    config["api_key"] = "****"
    return config


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "endpoint": "/effective-config"}
