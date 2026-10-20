"""Configuração de execução do serviço."""
import os
from pathlib import Path


def validar_ambiente():
    token = os.getenv("API_TOKEN", "")
    if len(token) < 32:
        raise ValueError("Defina API_TOKEN com pelo menos 32 caracteres no ambiente.")
    port = int(os.getenv("PORT", "8000"))
    if not 1 <= port <= 65535:
        raise ValueError("PORT deve estar entre 1 e 65535.")
    url = os.getenv("DATABASE_URL", "sqlite:///./prato_cheio.db")
    if not url.startswith("sqlite:///"):
        raise ValueError("Esta versão usa SQLite; outro banco exige revisão das transações.")
    arquivo = url.removeprefix("sqlite:///")
    if arquivo != ":memory:":
        Path(arquivo).expanduser().parent.mkdir(parents=True, exist_ok=True)
    return port
