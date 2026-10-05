"""Inicializa o protótipo sem apagar o banco existente."""
from pathlib import Path
import secrets
import subprocess
import sys
import webbrowser
if not Path(".env").exists():
    Path(".env").write_text("DATABASE_URL=sqlite:///./prato_cheio.db\nAPI_TOKEN="+secrets.token_urlsafe(32)+"\nOLLAMA_URL=http://localhost:11434\nOLLAMA_MODEL=qwen2.5:0.5b\n", encoding="utf-8")
subprocess.run([sys.executable, "seed.py"], check=True)
from dotenv import dotenv_values
print("Abra http://127.0.0.1:8000/app")
print("Chave de acesso local:", dotenv_values(".env")["API_TOKEN"])
import uvicorn
uvicorn.run("main:app", host="127.0.0.1", port=8000)
