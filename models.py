"""Tabelas do banco de dados."""

from datetime import datetime

from sqlalchemy import CheckConstraint, Index, Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Doador(Base):
    """Estabelecimento que doa o alimento que sobrou."""

    __tablename__ = "doadores"

    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    cidade = Column(String(50), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.now)

    # Um doador tem varias doacoes
    doacoes = relationship("Doacao", back_populates="doador")


class Instituicao(Base):
    """ONG ou casa de apoio que recebe o alimento."""

    __tablename__ = "instituicoes"

    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), unique=True, nullable=False)
    nome = Column(String(100), nullable=False)
    responsavel = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    cidade = Column(String(50), nullable=False)
    possui_refrigeracao = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.now)

    # Uma instituicao faz varias reservas
    reservas = relationship("Reserva", back_populates="instituicao")


class Doacao(Base):
    """Lote de alimento publicado por um doador."""

    __tablename__ = "doacoes"
    __table_args__ = (
        CheckConstraint("quantidade_total > 0", name="ck_total_positivo"),
        CheckConstraint("quantidade_reservada >= 0 AND quantidade_reservada <= quantidade_total", name="ck_saldo"),
        Index("ix_doacao_busca", "status", "data_validade", "categoria"),
        Index("ix_doacao_doador", "doador_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    doador_id = Column(Integer, ForeignKey("doadores.id"), nullable=False)
    descricao = Column(String(200), nullable=False)
    categoria = Column(String(20), nullable=False)
    tipo_armazenamento = Column(String(20), nullable=False)
    unidade = Column(String(10), nullable=False)
    quantidade_total = Column(Float, nullable=False)
    quantidade_reservada = Column(Float, default=0)
    data_validade = Column(Date, nullable=False)
    local_retirada = Column(String(200), nullable=False)
    status = Column(String(25), default="DISPONIVEL")
    criado_em = Column(DateTime, default=datetime.now)

    doador = relationship("Doador", back_populates="doacoes")
    reservas = relationship("Reserva", back_populates="doacao")


class Reserva(Base):
    """Liga uma instituicao a uma doacao. Guarda quanto foi reservado."""

    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_reserva_positiva"),
        Index("ix_reserva_instituicao_status", "instituicao_id", "status"),
        Index("ix_reserva_doacao", "doacao_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    doacao_id = Column(Integer, ForeignKey("doacoes.id"), nullable=False)
    instituicao_id = Column(Integer, ForeignKey("instituicoes.id"), nullable=False)
    quantidade = Column(Float, nullable=False)
    status = Column(String(15), default="PENDENTE")
    observacoes = Column(String(500), nullable=True)
    criado_em = Column(DateTime, default=datetime.now)
    coletado_em = Column(DateTime, nullable=True)

    doacao = relationship("Doacao", back_populates="reservas")
    instituicao = relationship("Instituicao", back_populates="reservas")

class RelatorioIA(Base):
    __tablename__ = "relatorios_ia"
    id = Column(Integer, primary_key=True)
    modelo = Column(String(100), nullable=False)
    texto = Column(String(8000), nullable=False)
    criado_em = Column(DateTime, default=datetime.now, nullable=False)
