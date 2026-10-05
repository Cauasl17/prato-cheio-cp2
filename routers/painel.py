import os
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from database import get_db
from services.dashboard import montar_dashboard
from services.llm import gerar_relatorio
import models
router = APIRouter(tags=["Dashboard e IA"])
class RelatorioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    modelo: str
    texto: str
    criado_em: datetime
@router.get("/dashboard", summary="Indicadores e alertas calculados no banco")
def dashboard(db: Session = Depends(get_db)):
    return montar_dashboard(db)
@router.get("/ia/status", summary="Verificar o serviço e o modelo configurado")
async def ia_status():
    modelo=os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r=await client.get(os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")+"/api/tags")
            r.raise_for_status()
            instalado=any(m.get("name")==modelo for m in r.json().get("models",[]))
            return {"disponivel": instalado, "modelo": modelo}
    except (httpx.HTTPError, ValueError):
        return {"disponivel": False, "modelo": modelo}
@router.post("/ia/relatorio", summary="Gerar relatório por LLM com indicadores reais", responses={503:{"description":"Ollama ou modelo indisponível"}})
async def relatorio(db: Session = Depends(get_db)):
    saida=await gerar_relatorio(db)
    item=models.RelatorioIA(modelo=saida["modelo"], texto=saida["texto"])
    db.add(item);db.commit();db.refresh(item)
    return {**saida, "id": item.id}
@router.get("/ia/relatorios", response_model=list[RelatorioSaida], summary="Últimos 20 relatórios gerados")
def historico(db: Session = Depends(get_db)):
    return db.query(models.RelatorioIA).order_by(models.RelatorioIA.id.desc()).limit(20).all()
