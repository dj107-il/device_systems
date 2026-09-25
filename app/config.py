import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()

if len(SECRET_KEY) < 32:
    raise ValueError(
        "Configura SECRET_KEY en .env con una clave aleatoria "
        "de al menos 32 caracteres."
    )

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise ValueError(
        "ACCESS_TOKEN_EXPIRE_MINUTES debe ser mayor que cero."
    )

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

if "*" in CORS_ORIGINS:
    raise ValueError(
        "Configura origenes concretos para CORS."
    )