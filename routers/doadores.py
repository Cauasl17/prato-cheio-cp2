"""Rotas dos doadores."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/doadores", tags=["Doadores"])


@router.get("", response_model=schemas.ListaDoadores, summary="Listar doadores")
def listar(
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    cidade: str | None = None,
    ativo: bool | None = None,
    db: Session = Depends(get_db),
):
    total, itens = crud.listar_doadores(db, pagina, limite, cidade, ativo)
    return {"total": total, "pagina": pagina, "itens": itens}


@router.get("/{doador_id}", response_model=schemas.DoadorResposta, summary="Buscar um doador")
def buscar(doador_id: int, db: Session = Depends(get_db)):
    return crud.buscar_doador(db, doador_id)


@router.post("", response_model=schemas.DoadorResposta, status_code=201, summary="Cadastrar doador")
def criar(dados: schemas.DoadorCriar, db: Session = Depends(get_db)):
    return crud.criar_doador(db, dados)


@router.put("/{doador_id}", response_model=schemas.DoadorResposta, summary="Atualizar doador")
def atualizar(doador_id: int, dados: schemas.DoadorAtualizar, db: Session = Depends(get_db)):
    return crud.atualizar_doador(db, doador_id, dados)


@router.delete("/{doador_id}", status_code=204, summary="Excluir doador")
def deletar(doador_id: int, db: Session = Depends(get_db)):
    crud.deletar_doador(db, doador_id)
