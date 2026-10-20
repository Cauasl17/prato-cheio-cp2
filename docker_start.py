"""Inicialização configurada para contêiner e hospedagem."""
import os
import subprocess
import sys
from dotenv import load_dotenv
from config import validar_ambiente


def main():
    load_dotenv()
    port = validar_ambiente()
    if os.getenv("SEED_DEMO", "false").lower() == "true":
        subprocess.run([sys.executable, "seed.py"], check=True)
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
