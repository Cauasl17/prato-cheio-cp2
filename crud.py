"""Funcoes que acessam o banco e aplicam as regras de negocio.

As rotas so recebem a requisicao e chamam as funcoes daqui.
Assim as regras ficam todas em um lugar so.
"""

from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update, text

import models


def bloquear_transacao(db):
    # Protótipo SQLite: uma escrita por vez, com espera de até 10 segundos.
    if db.get_bind().dialect.name == "sqlite":
        db.execute(text("BEGIN IMMEDIATE"))

# --------------------------------------------------
# Validacao de CNPJ
# --------------------------------------------------

def limpar_cnpj(cnpj):
    """Deixa so os numeros, tirando ponto, barra e traco."""
    return "".join(caractere for caractere in cnpj if caractere.isdigit())


def cnpj_valido(cnpj):
    """Confere os dois digitos verificadores do CNPJ usando o modulo 11."""
    numeros = limpar_cnpj(cnpj)

    if len(numeros) != 14:
        return False
    if numeros == numeros[0] * 14:  # rejeita 111...1, 222...2 etc
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Primeiro digito verificador
    soma = 0
    for i in range(12):
        soma = soma + int(numeros[i]) * pesos1[i]
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    # Segundo digito verificador
    base = numeros[:12] + str(digito1)
    soma = 0
    for i in range(13):
        soma = soma + int(base[i]) * pesos2[i]
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return numeros[12] == str(digito1) and numeros[13] == str(digito2)


# --------------------------------------------------
# Doadores
# --------------------------------------------------

def listar_doadores(db: Session, pagina, limite, cidade=None, ativo=None):
    consulta = db.query(models.Doador)

    if cidade:
        consulta = consulta.filter(models.Doador.cidade == cidade)
    if ativo is not None:
        consulta = consulta.filter(models.Doador.ativo == ativo)

    total = consulta.count()
    itens = consulta.order_by(consulta.column_descriptions[0]["entity"].id).offset((pagina - 1) * limite).limit(limite).all()
    return total, itens


def buscar_doador(db: Session, doador_id):
    doador = db.query(models.Doador).filter(models.Doador.id == doador_id).first()
    if doador is None:
        raise HTTPException(status_code=404, detail="Doador nao encontrado.")
    return doador


def criar_doador(db: Session, dados):
    cnpj = limpar_cnpj(dados.cnpj)

    # Regra 1: o CNPJ precisa ser valido
    if not cnpj_valido(cnpj):
        raise HTTPException(status_code=422, detail="CNPJ invalido.")

    # Regra 1: e nao pode estar cadastrado ainda
    if db.query(models.Doador).filter(models.Doador.cnpj == cnpj).first():
        raise HTTPException(status_code=409, detail="Ja existe um doador com esse CNPJ.")

    doador = models.Doador(
        cnpj=cnpj,
        nome=dados.nome,
        tipo=dados.tipo.value,
        email=dados.email,
        telefone=dados.telefone,
        cidade=dados.cidade,
    )
    db.add(doador)
    db.commit()
    db.refresh(doador)
    return doador


def atualizar_doador(db: Session, doador_id, dados):
    doador = buscar_doador(db, doador_id)

    campos = dados.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo foi enviado.")

    for campo, valor in campos.items():
        if campo == "tipo":
            valor = valor.value
        setattr(doador, campo, valor)

    db.commit()
    db.refresh(doador)
    return doador


def deletar_doador(db: Session, doador_id):
    doador = buscar_doador(db, doador_id)

    # Regra 9: nao pode apagar doador que ainda tem doacao circulando
    em_aberto = (
        db.query(models.Doacao)
        .filter(
            models.Doacao.doador_id == doador_id,
            models.Doacao.status.in_(["DISPONIVEL", "PARCIALMENTE_RESERVADA", "RESERVADA"]),
        )
        .count()
    )
    if doador.doacoes:
        raise HTTPException(
            status_code=409,
            detail="O doador tem doacoes em aberto. Cancele as doacoes ou desative o cadastro.",
        )

    db.delete(doador)
    db.commit()


# --------------------------------------------------
# Instituicoes
# --------------------------------------------------

def listar_instituicoes(db: Session, pagina, limite, cidade=None, possui_refrigeracao=None):
    consulta = db.query(models.Instituicao)

    if cidade:
        consulta = consulta.filter(models.Instituicao.cidade == cidade)
    if possui_refrigeracao is not None:
        consulta = consulta.filter(models.Instituicao.possui_refrigeracao == possui_refrigeracao)

    total = consulta.count()
    itens = consulta.order_by(consulta.column_descriptions[0]["entity"].id).offset((pagina - 1) * limite).limit(limite).all()
    return total, itens


def buscar_instituicao(db: Session, instituicao_id):
    instituicao = (
        db.query(models.Instituicao).filter(models.Instituicao.id == instituicao_id).first()
    )
    if instituicao is None:
        raise HTTPException(status_code=404, detail="Instituicao nao encontrada.")
    return instituicao


def criar_instituicao(db: Session, dados):
    cnpj = limpar_cnpj(dados.cnpj)

    # Regra 1: mesma validacao usada no doador
    if not cnpj_valido(cnpj):
        raise HTTPException(status_code=422, detail="CNPJ invalido.")

    if db.query(models.Instituicao).filter(models.Instituicao.cnpj == cnpj).first():
        raise HTTPException(status_code=409, detail="Ja existe uma instituicao com esse CNPJ.")

    instituicao = models.Instituicao(
        cnpj=cnpj,
        nome=dados.nome,
        responsavel=dados.responsavel,
        email=dados.email,
        telefone=dados.telefone,
        cidade=dados.cidade,
        possui_refrigeracao=dados.possui_refrigeracao,
    )
    db.add(instituicao)
    db.commit()
    db.refresh(instituicao)
    return instituicao


def atualizar_instituicao(db: Session, instituicao_id, dados):
    instituicao = buscar_instituicao(db, instituicao_id)

    campos = dados.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo foi enviado.")

    for campo, valor in campos.items():
        setattr(instituicao, campo, valor)

    db.commit()
    db.refresh(instituicao)
    return instituicao


def deletar_instituicao(db: Session, instituicao_id):
    instituicao = buscar_instituicao(db, instituicao_id)

    reservas_abertas = (
        db.query(models.Reserva)
        .filter(
            models.Reserva.instituicao_id == instituicao_id,
            models.Reserva.status == "PENDENTE",
        )
        .count()
    )
    if instituicao.reservas:
        raise HTTPException(
            status_code=409,
            detail="A instituicao tem reservas em aberto. Cancele as reservas primeiro.",
        )

    db.delete(instituicao)
    db.commit()


# --------------------------------------------------
# Doacoes
# --------------------------------------------------

def atualizar_status_doacao(doacao):
    """Define o status da doacao olhando quanto ja foi reservado.

    O status nunca vem do usuario, e sempre calculado aqui.
    """
    if doacao.status == "CANCELADA":
        return

    if doacao.quantidade_reservada <= 0:
        doacao.status = "DISPONIVEL"
    elif doacao.quantidade_reservada >= doacao.quantidade_total:
        doacao.status = "RESERVADA"
    else:
        doacao.status = "PARCIALMENTE_RESERVADA"


def listar_doacoes(db: Session, pagina, limite, status=None, categoria=None, apenas_disponiveis=False):
    consulta = db.query(models.Doacao)

    if status:
        consulta = consulta.filter(models.Doacao.status == status)
    if categoria:
        consulta = consulta.filter(models.Doacao.categoria == categoria)
    if apenas_disponiveis:
        consulta = consulta.filter(
            models.Doacao.status.in_(["DISPONIVEL", "PARCIALMENTE_RESERVADA"]),
            models.Doacao.data_validade >= date.today(),
        )

    total = consulta.count()
    itens = consulta.order_by(consulta.column_descriptions[0]["entity"].id).offset((pagina - 1) * limite).limit(limite).all()
    return total, itens


def buscar_doacao(db: Session, doacao_id):
    doacao = db.query(models.Doacao).filter(models.Doacao.id == doacao_id).first()
    if doacao is None:
        raise HTTPException(status_code=404, detail="Doacao nao encontrada.")
    return doacao


def criar_doacao(db: Session, dados):
    doador = buscar_doador(db, dados.doador_id)

    # Regra 2: doador desativado nao publica doacao
    if not doador.ativo:
        raise HTTPException(
            status_code=422, detail="Esse doador esta inativo e nao pode cadastrar doacoes."
        )

    # Regra 3: nao adianta cadastrar alimento que ja venceu
    if dados.data_validade < date.today():
        raise HTTPException(
            status_code=422, detail="A data de validade nao pode ser anterior a hoje."
        )

    # Regra 4: quantidade tem que ser positiva
    if dados.quantidade_total <= 0:
        raise HTTPException(status_code=422, detail="A quantidade precisa ser maior que zero.")

    doacao = models.Doacao(
        doador_id=dados.doador_id,
        descricao=dados.descricao,
        categoria=dados.categoria.value,
        tipo_armazenamento=dados.tipo_armazenamento.value,
        unidade=dados.unidade.value,
        quantidade_total=dados.quantidade_total,
        quantidade_reservada=0,
        data_validade=dados.data_validade,
        local_retirada=dados.local_retirada,
        status="DISPONIVEL",
    )
    db.add(doacao)
    db.commit()
    db.refresh(doacao)
    return doacao


def atualizar_doacao(db: Session, doacao_id, dados):
    bloquear_transacao(db)
    doacao = buscar_doacao(db, doacao_id)

    if doacao.status in ["COLETADA", "CANCELADA"]:
        raise HTTPException(
            status_code=409, detail=f"A doacao esta {doacao.status} e nao pode ser alterada."
        )

    campos = dados.model_dump(exclude_unset=True)
    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo foi enviado.")

    if campos.get("data_validade") is not None and campos["data_validade"] < date.today():
        raise HTTPException(422, "A validade não pode ser anterior a hoje.")

    # Regra 5: nao pode diminuir a quantidade abaixo do que ja foi reservado
    nova_quantidade = campos.get("quantidade_total")
    if nova_quantidade is not None and nova_quantidade < doacao.quantidade_reservada:
        raise HTTPException(
            status_code=422,
            detail=f"Ja existem {doacao.quantidade_reservada} reservados nessa doacao.",
        )

    for campo, valor in campos.items():
        if campo == "categoria":
            valor = valor.value
        setattr(doacao, campo, valor)

    atualizar_status_doacao(doacao)
    db.commit()
    db.refresh(doacao)
    return doacao


def cancelar_doacao(db: Session, doacao_id):
    bloquear_transacao(db)
    doacao = buscar_doacao(db, doacao_id)

    if doacao.status in ["COLETADA", "CANCELADA"]:
        raise HTTPException(status_code=409, detail=f"A doacao ja esta {doacao.status}.")

    # Cancela junto todas as reservas que ainda estavam pendentes
    for reserva in doacao.reservas:
        if reserva.status == "PENDENTE":
            reserva.status = "CANCELADA"

    doacao.quantidade_reservada = sum(r.quantidade for r in doacao.reservas if r.status == "COLETADA")
    doacao.status = "CANCELADA"

    db.commit()
    db.refresh(doacao)
    return doacao


def deletar_doacao(db: Session, doacao_id):
    doacao = buscar_doacao(db, doacao_id)

    if len(doacao.reservas) > 0:
        raise HTTPException(
            status_code=409,
            detail="Essa doacao tem reservas registradas. Use o endpoint de cancelar.",
        )

    db.delete(doacao)
    db.commit()


# --------------------------------------------------
# Reservas
# --------------------------------------------------

def listar_reservas(db: Session, pagina, limite, status=None, doacao_id=None, instituicao_id=None):
    consulta = db.query(models.Reserva)

    if status:
        consulta = consulta.filter(models.Reserva.status == status)
    if doacao_id:
        consulta = consulta.filter(models.Reserva.doacao_id == doacao_id)
    if instituicao_id:
        consulta = consulta.filter(models.Reserva.instituicao_id == instituicao_id)

    total = consulta.count()
    itens = consulta.order_by(consulta.column_descriptions[0]["entity"].id).offset((pagina - 1) * limite).limit(limite).all()
    return total, itens


def buscar_reserva(db: Session, reserva_id):
    reserva = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if reserva is None:
        raise HTTPException(status_code=404, detail="Reserva nao encontrada.")
    return reserva


def criar_reserva(db: Session, dados):
    bloquear_transacao(db)
    doacao = buscar_doacao(db, dados.doacao_id)
    instituicao = buscar_instituicao(db, dados.instituicao_id)

    # Regra 6: instituicao desativada nao reserva
    if not instituicao.ativo:
        raise HTTPException(
            status_code=422, detail="Essa instituicao esta inativa e nao pode fazer reservas."
        )

    # Regra 3: alimento vencido nao pode ser reservado
    if doacao.data_validade < date.today():
        raise HTTPException(status_code=422, detail="Essa doacao esta vencida.")

    # Regra 7: so da para reservar doacao que ainda tem saldo
    if doacao.status not in ["DISPONIVEL", "PARCIALMENTE_RESERVADA"]:
        raise HTTPException(
            status_code=422, detail=f"A doacao esta {doacao.status} e nao aceita reservas."
        )

    # Regra 8: alimento gelado so vai para quem tem geladeira
    if doacao.tipo_armazenamento in ["REFRIGERADO", "CONGELADO"]:
        if not instituicao.possui_refrigeracao:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Esse alimento precisa ser {doacao.tipo_armazenamento.lower()} e a "
                    f"instituicao {instituicao.nome} nao tem refrigeracao."
                ),
            )

    # Regra 10: uma instituicao so pode ter uma reserva em aberto por doacao
    reserva_repetida = (
        db.query(models.Reserva)
        .filter(
            models.Reserva.doacao_id == doacao.id,
            models.Reserva.instituicao_id == instituicao.id,
            models.Reserva.status == "PENDENTE",
        )
        .first()
    )
    if reserva_repetida:
        raise HTTPException(
            status_code=409,
            detail="Essa instituicao ja tem uma reserva em aberto para essa doacao.",
        )

    # Regra 4: nao pode reservar mais do que sobrou
    disponivel = doacao.quantidade_total - doacao.quantidade_reservada
    if dados.quantidade <= 0:
        raise HTTPException(status_code=422, detail="A quantidade precisa ser maior que zero.")
    if dados.quantidade > disponivel:
        raise HTTPException(
            status_code=422,
            detail=f"Só sobraram {disponivel} {doacao.unidade} nessa doacao.",
        )

    reserva = models.Reserva(
        doacao_id=dados.doacao_id,
        instituicao_id=dados.instituicao_id,
        quantidade=dados.quantidade,
        observacoes=dados.observacoes,
        status="PENDENTE",
    )
    db.add(reserva)

    # Desconta do saldo da doacao e recalcula o status
    # UPDATE condicional impede que dois pedidos usem o mesmo saldo.
    resultado = db.execute(update(models.Doacao).where(
        models.Doacao.id == doacao.id,
        models.Doacao.quantidade_total - models.Doacao.quantidade_reservada >= dados.quantidade,
        models.Doacao.status.in_(["DISPONIVEL", "PARCIALMENTE_RESERVADA"]),
        models.Doacao.data_validade >= date.today(),
    ).values(quantidade_reservada=models.Doacao.quantidade_reservada + dados.quantidade),
        execution_options={"synchronize_session": False})
    if resultado.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Saldo alterado. Atualize a lista e tente novamente.")
    db.refresh(doacao)
    atualizar_status_doacao(doacao)

    db.commit()
    db.refresh(reserva)
    return reserva


def coletar_reserva(db: Session, reserva_id):
    bloquear_transacao(db)
    reserva = buscar_reserva(db, reserva_id)

    if reserva.status != "PENDENTE":
        raise HTTPException(
            status_code=409, detail=f"A reserva esta {reserva.status} e nao pode ser coletada."
        )

    doacao = reserva.doacao

    # Regra 3: nao registra retirada de alimento vencido
    if doacao.data_validade < date.today():
        raise HTTPException(status_code=422, detail="Essa doacao venceu, a coleta nao pode ser feita.")

    reserva.status = "COLETADA"
    reserva.coletado_em = datetime.now()

    # Se todo mundo ja retirou e o lote acabou, a doacao vira COLETADA
    ainda_pendentes = [r for r in doacao.reservas if r.status == "PENDENTE"]
    if len(ainda_pendentes) == 0 and doacao.quantidade_reservada >= doacao.quantidade_total:
        doacao.status = "COLETADA"

    db.commit()
    db.refresh(reserva)
    return reserva


def cancelar_reserva(db: Session, reserva_id):
    bloquear_transacao(db)
    reserva = buscar_reserva(db, reserva_id)

    if reserva.status != "PENDENTE":
        raise HTTPException(
            status_code=409, detail=f"A reserva ja esta {reserva.status}."
        )

    # Regra 11: cancelar devolve a quantidade para a doacao
    doacao = reserva.doacao
    doacao.quantidade_reservada = doacao.quantidade_reservada - reserva.quantidade
    if doacao.quantidade_reservada < 0:
        doacao.quantidade_reservada = 0

    reserva.status = "CANCELADA"
    atualizar_status_doacao(doacao)

    db.commit()
    db.refresh(reserva)
    return reserva
