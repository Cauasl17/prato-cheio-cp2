import os
import secrets
import subprocess
import sys
os.environ.setdefault("API_TOKEN", secrets.token_urlsafe(32))
print("Chave administrativa:", os.environ["API_TOKEN"], flush=True)
subprocess.run([sys.executable,"seed.py"],check=True)
import uvicorn
uvicorn.run("main:app",host="0.0.0.0",port=8000)
