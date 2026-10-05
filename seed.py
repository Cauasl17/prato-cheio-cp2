"""Coloca alguns dados de exemplo no banco para poder testar a API.

Como usar:
    python seed.py
"""

from datetime import date, timedelta

import models
from database import Base, SessionLocal, engine

# Recria as tabelas do zero

Base.metadata.create_all(bind=engine)

db = SessionLocal()
if db.query(models.Doador).first():
    db.close()
    print("Banco existente preservado. Nenhum dado foi alterado.")
    raise SystemExit(0)

hoje = date.today()

doadores = [
    models.Doador(
        cnpj="11222333000181",
        nome="Padaria Pao Nosso",
        tipo="PADARIA",
        email="contato@example.com",
        telefone="(11) 3456-7890",
        cidade="Sao Paulo",
    ),
    models.Doador(
        cnpj="45997418000153",
        nome="Supermercado Bom Preco",
        tipo="MERCADO",
        email="contato@example.com",
        telefone="(11) 2222-3030",
        cidade="Sao Paulo",
    ),
    models.Doador(
        cnpj="60746948000112",
        nome="Cantina da Nonna",
        tipo="RESTAURANTE",
        email="cozinha@example.com",
        telefone="(11) 4002-8922",
        cidade="Sao Paulo",
    ),
]

instituicoes = [
    models.Instituicao(
        cnpj="02558157000162",
        nome="Associacao Maos Unidas",
        responsavel="Maria Aparecida Silva",
        email="contato@example.com",
        telefone="(11) 2233-4455",
        cidade="Sao Paulo",
        possui_refrigeracao=True,
    ),
    models.Instituicao(
        cnpj="47960950000121",
        nome="Casa de Apoio Semear",
        responsavel="Joao Batista Ferreira",
        email="semear@example.com",
        telefone="(11) 5566-7788",
        cidade="Sao Paulo",
        possui_refrigeracao=False,
    ),
]

db.add_all(doadores)
db.add_all(instituicoes)
db.commit()

doacoes = [
    models.Doacao(
        doador_id=1,
        descricao="Paes do dia anterior, embalados",
        categoria="PANIFICACAO",
        tipo_armazenamento="AMBIENTE",
        unidade="KG",
        quantidade_total=30,
        data_validade=hoje + timedelta(days=2),
        local_retirada="Rua Augusta, 1200 - fundos",
    ),
    models.Doacao(
        doador_id=2,
        descricao="Iogurtes perto do vencimento",
        categoria="LATICINIOS",
        tipo_armazenamento="REFRIGERADO",
        unidade="UNIDADE",
        quantidade_total=240,
        data_validade=hoje + timedelta(days=5),
        local_retirada="Av. Domingos de Morais, 980",
    ),
    models.Doacao(
        doador_id=2,
        descricao="Arroz e feijao com embalagem amassada",
        categoria="NAO_PERECIVEL",
        tipo_armazenamento="AMBIENTE",
        unidade="KG",
        quantidade_total=120,
        data_validade=hoje + timedelta(days=180),
        local_retirada="Av. Domingos de Morais, 980",
    ),
    models.Doacao(
        doador_id=3,
        descricao="Marmitas de massa feitas no dia",
        categoria="PRONTO_CONSUMO",
        tipo_armazenamento="REFRIGERADO",
        unidade="PORCAO",
        quantidade_total=80,
        data_validade=hoje + timedelta(days=1),
        local_retirada="Rua Mourato Coelho, 45",
    ),
]

db.add_all(doacoes)
db.commit()

# Uma reserva de exemplo, ja descontando o saldo da doacao
reserva = models.Reserva(doacao_id=1, instituicao_id=1, quantidade=18, status="PENDENTE")
db.add(reserva)

doacao1 = db.query(models.Doacao).filter(models.Doacao.id == 1).first()
doacao1.quantidade_reservada = 18
doacao1.status = "PARCIALMENTE_RESERVADA"

db.commit()
db.close()

print("Banco populado:")
print(f"  {len(doadores)} doadores")
print(f"  {len(instituicoes)} instituicoes")
print(f"  {len(doacoes)} doacoes")
print("  1 reserva")
