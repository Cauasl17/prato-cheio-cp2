"""Relatório contextual com Ollama. Falhas reais nunca geram texto simulado."""
import json
import os
import httpx
from fastapi import HTTPException
from services.dashboard import montar_dashboard

async def gerar_relatorio(db):
    contexto = montar_dashboard(db)
    modelo = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
    url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
    instrucao = ("Escreva em português um relatório breve de gestão de doações de alimentos. "
        "Use somente os números do JSON. Destaque os lotes que vencem em até dois dias pelos IDs. "
        "Não some KG com UNIDADE, LITRO ou PORCAO. Não invente instituições nem benefícios medidos. "
        "Recomende conferir validade e capacidade de refrigeração antes da reserva. "
        "Não autorize coletas, reservas ou consumo. A resposta é apoio à decisão humana.")
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url + "/api/generate", json={"model": modelo, "system": instrucao,
                "prompt": json.dumps(contexto, ensure_ascii=False), "stream": False,
                "options": {"temperature": 0.1, "num_predict": 500}})
            r.raise_for_status()
            texto = r.json()["response"].strip()
            if not texto or len(texto)>8000:
                raise ValueError("Resposta vazia ou extensa")
    except (httpx.HTTPError, ValueError, KeyError):
        raise HTTPException(503, "LLM indisponível. Inicie o Ollama e baixe o modelo configurado no .env.")
    return {"modelo": modelo, "texto": texto, "dados_enviados": contexto, "origem": "ollama",
        "aviso": "Revise o relatório. A LLM pode errar e não modifica reservas ou estoque."}
