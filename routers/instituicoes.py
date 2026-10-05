"""Rotas das instituicoes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/instituicoes", tags=["Instituicoes"])


@router.get("", response_model=schemas.ListaInstituicoes, summary="Listar instituicoes")
def listar(
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    cidade: str | None = None,
    possui_refrigeracao: bool | None = None,
    db: Session = Depends(get_db),
):
    total, itens = crud.listar_instituicoes(db, pagina, limite, cidade, possui_refrigeracao)
    return {"total": total, "pagina": pagina, "itens": itens}


@router.get("/{instituicao_id}", response_model=schemas.InstituicaoResposta, summary="Buscar uma instituicao")
def buscar(instituicao_id: int, db: Session = Depends(get_db)):
    return crud.buscar_instituicao(db, instituicao_id)


@router.post("", response_model=schemas.InstituicaoResposta, status_code=201, summary="Cadastrar instituicao")
def criar(dados: schemas.InstituicaoCriar, db: Session = Depends(get_db)):
    return crud.criar_instituicao(db, dados)


@router.put("/{instituicao_id}", response_model=schemas.InstituicaoResposta, summary="Atualizar instituicao")
def atualizar(instituicao_id: int, dados: schemas.InstituicaoAtualizar, db: Session = Depends(get_db)):
    return crud.atualizar_instituicao(db, instituicao_id, dados)


@router.delete("/{instituicao_id}", status_code=204, summary="Excluir instituicao")
def deletar(instituicao_id: int, db: Session = Depends(get_db)):
    crud.deletar_instituicao(db, instituicao_id)
