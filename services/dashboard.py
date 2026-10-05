from datetime import date, timedelta
from sqlalchemy import func
import models

def montar_dashboard(db):
    hoje = date.today()
    d = models.Doacao
    disponivel = (d.status.in_(["DISPONIVEL", "PARCIALMENTE_RESERVADA"]), d.data_validade >= hoje)
    categorias = db.query(d.categoria, func.count(d.id)).group_by(d.categoria).all()
    unidades = db.query(d.unidade, func.sum(d.quantidade_total - d.quantidade_reservada)).filter(*disponivel).group_by(d.unidade).all()
    urgentes = db.query(d).filter(*disponivel, d.data_validade <= hoje + timedelta(days=2)).order_by(d.data_validade, d.id).limit(10).all()
    return {
        "doadores": db.query(models.Doador).count(),
        "instituicoes": db.query(models.Instituicao).count(),
        "doacoes": db.query(d).count(),
        "disponiveis": db.query(d).filter(*disponivel).count(),
        "reservas_pendentes": db.query(models.Reserva).filter(models.Reserva.status == "PENDENTE").count(),
        "coletas": db.query(models.Reserva).filter(models.Reserva.status == "COLETADA").count(),
        "por_categoria": [{"categoria": k, "total": v} for k, v in categorias],
        "saldo_por_unidade": [{"unidade": k, "quantidade": round(v or 0, 3)} for k, v in unidades],
        "alertas": [{"id": x.id, "categoria": x.categoria, "validade": x.data_validade.isoformat(), "saldo": x.quantidade_total-x.quantidade_reservada, "unidade": x.unidade} for x in urgentes],
        "data_referencia": hoje.isoformat(),
    }
