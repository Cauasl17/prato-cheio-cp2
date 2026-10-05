"""Arquivo principal da API do Prato Cheio."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi import Depends
from security import autenticar
from sqlalchemy.exc import IntegrityError
from routers import painel
from starlette.exceptions import HTTPException

import models
from database import Base, engine
from routers import doacoes, doadores, instituicoes, reservas

# Cria as tabelas no banco se ainda nao existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Prato Cheio API",
    description=(
        "API que conecta o alimento que sobra em padarias, mercados e restaurantes "
        "com ONGs e casas de apoio, antes que ele estrague.\n\n"
        "Fluxo do sistema:\n"
        "1. O doador cadastra uma doacao\n"
        "2. A instituicao ve as doacoes disponiveis\n"
        "3. A instituicao faz uma reserva\n"
        "4. Na retirada, a coleta e registrada"
    ),
    version="2.0.0",
)

for router in (doadores.router, instituicoes.router, doacoes.router, reservas.router, painel.router):
    app.include_router(router, dependencies=[Depends(autenticar)])

frontend = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend), name="static")
@app.get("/app", include_in_schema=False)
def interface():
    return FileResponse(frontend / "index.html")
@app.middleware("http")
async def cabecalhos(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response
@app.exception_handler(IntegrityError)
async def conflito_banco(request, exc):
    return JSONResponse(status_code=409, content={"erro": "Conflito de integridade. Verifique vínculos e duplicidades.", "status": 409})


# Deixa todos os erros com o mesmo formato de resposta
@app.exception_handler(HTTPException)
async def tratar_erro(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"erro": exc.detail, "status": exc.status_code},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_de_dados(request: Request, exc: RequestValidationError):
    campos = []
    for erro in exc.errors():
        campos.append({"campo": str(erro["loc"][-1]), "problema": erro["msg"]})

    return JSONResponse(
        status_code=422,
        content={"erro": "Os dados enviados estao incorretos.", "status": 422, "campos": campos},
    )


@app.get("/", tags=["Inicio"], summary="Informacoes da API")
def inicio():
    return {
        "api": "Prato Cheio",
        "versao": "2.0.0",
        "documentacao": "/docs",
    }
