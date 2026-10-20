"""Gera configuração local sem sobrescrever um ambiente existente."""
from pathlib import Path
import secrets

if __name__ == "__main__":
    arquivo = Path(".env")
    if arquivo.exists():
        print(".env existente preservado.")
    else:
        arquivo.write_text(
            "DATABASE_URL=sqlite:///./prato_cheio.db\nAPI_TOKEN=" + secrets.token_urlsafe(32)
            + "\nPORT=8000\nSEED_DEMO=true\nOLLAMA_URL=http://ollama:11434\nOLLAMA_MODEL=qwen2.5:0.5b\n",
            encoding="utf-8",
        )
        arquivo.chmod(0o600)
        print("Configuração local criada em .env. Não publique esse arquivo.")
