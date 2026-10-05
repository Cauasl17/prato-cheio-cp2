"""Rotas das reservas."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.get("", response_model=schemas.ListaReservas, summary="Listar reservas")
def listar(
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    status: str | None = None,
    doacao_id: int | None = None,
    instituicao_id: int | None = None,
    db: Session = Depends(get_db),
):
    total, itens = crud.listar_reservas(db, pagina, limite, status, doacao_id, instituicao_id)
    return {"total": total, "pagina": pagina, "itens": itens}


@router.get("/{reserva_id}", response_model=schemas.ReservaResposta, summary="Buscar uma reserva")
def buscar(reserva_id: int, db: Session = Depends(get_db)):
    return crud.buscar_reserva(db, reserva_id)


@router.post("", response_model=schemas.ReservaResposta, status_code=201, summary="Criar reserva")
def criar(dados: schemas.ReservaCriar, db: Session = Depends(get_db)):
    return crud.criar_reserva(db, dados)


@router.patch("/{reserva_id}/coletar", response_model=schemas.ReservaResposta, summary="Registrar coleta")
def coletar(reserva_id: int, db: Session = Depends(get_db)):
    return crud.coletar_reserva(db, reserva_id)


@router.delete("/{reserva_id}", response_model=schemas.ReservaResposta, summary="Cancelar reserva")
def cancelar(reserva_id: int, db: Session = Depends(get_db)):
    return crud.cancelar_reserva(db, reserva_id)
