"""Chave administrativa do protótipo, sem permissões por instituição."""
import os
import secrets
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
bearer = HTTPBearer(auto_error=False)
def autenticar(cred: HTTPAuthorizationCredentials | None = Depends(bearer)):
    token = os.getenv("API_TOKEN", "")
    if not token:
        raise HTTPException(503, "Configure API_TOKEN no .env ou execute iniciar.py.")
    if not cred or not secrets.compare_digest(cred.credentials, token):
        raise HTTPException(401, "Chave de acesso inválida.", headers={"WWW-Authenticate": "Bearer"})
