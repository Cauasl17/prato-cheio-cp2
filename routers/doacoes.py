"""Rotas das doacoes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/doacoes", tags=["Doacoes"])


@router.get("", response_model=schemas.ListaDoacoes, summary="Listar doacoes")
def listar(
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    status: str | None = None,
    categoria: str | None = None,
    apenas_disponiveis: bool = False,
    db: Session = Depends(get_db),
):
    total, itens = crud.listar_doacoes(db, pagina, limite, status, categoria, apenas_disponiveis)
    return {"total": total, "pagina": pagina, "itens": itens}


@router.get("/{doacao_id}", response_model=schemas.DoacaoResposta, summary="Buscar uma doacao")
def buscar(doacao_id: int, db: Session = Depends(get_db)):
    return crud.buscar_doacao(db, doacao_id)


@router.post("", response_model=schemas.DoacaoResposta, status_code=201, summary="Cadastrar doacao")
def criar(dados: schemas.DoacaoCriar, db: Session = Depends(get_db)):
    return crud.criar_doacao(db, dados)


@router.put("/{doacao_id}", response_model=schemas.DoacaoResposta, summary="Atualizar doacao")
def atualizar(doacao_id: int, dados: schemas.DoacaoAtualizar, db: Session = Depends(get_db)):
    return crud.atualizar_doacao(db, doacao_id, dados)


@router.patch("/{doacao_id}/cancelar", response_model=schemas.DoacaoResposta, summary="Cancelar doacao")
def cancelar(doacao_id: int, db: Session = Depends(get_db)):
    return crud.cancelar_doacao(db, doacao_id)


@router.delete("/{doacao_id}", status_code=204, summary="Excluir doacao")
def deletar(doacao_id: int, db: Session = Depends(get_db)):
    crud.deletar_doacao(db, doacao_id)
