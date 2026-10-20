"""Cenários de aceitação e configuração da publicação."""
from unittest.mock import MagicMock
import pytest
from sqlalchemy.exc import SQLAlchemyError
from config import validar_ambiente
from tests.test_api import D, preparar, reservar


def registrar(record_property, cenario, esperado, obtido):
    record_property('cenario', cenario)
    record_property('esperado', str(esperado))
    record_property('obtido', str(obtido))
    assert obtido == esperado


def test_c01_saude_e_banco(client, record_property):
    r = client.get('/health',headers={'Authorization':''})
    registrar(record_property,'C01 - Saúde da API e conexão SQL',(200,'ok','ok'),
              (r.status_code,r.json()['status'],r.json()['banco']))


def test_c02_cadastro_valido(client, record_property):
    r = client.post('/doadores',json=D)
    registrar(record_property,'C02 - Cadastro válido persistido',(201,D['nome']),
              (r.status_code,client.get('/doadores/'+str(r.json()['id'])).json()['nome']))


def test_c03_cadastro_invalido(client, record_property):
    r = client.post('/doadores',json={**D,'cnpj':'123'})
    registrar(record_property,'C03 - CNPJ inválido rejeitado',(422,0),
              (r.status_code,client.get('/doadores').json()['total']))


def test_c04_reserva_acima_saldo(client, record_property):
    l,i = preparar(client)
    r = reservar(client,l,i,11)
    registrar(record_property,'C04 - Reserva acima do saldo não altera estoque',(422,0),
              (r.status_code,client.get(f'/doacoes/{l}').json()['quantidade_reservada']))


def test_c05_fluxo_coleta_dashboard(client, record_property):
    l,i = preparar(client)
    reserva = reservar(client,l,i,10).json()
    r = client.patch(f'/reservas/{reserva["id"]}/coletar')
    registrar(record_property,'C05 - Coleta atualiza lote e dashboard',(200,'COLETADA',1),
              (r.status_code,client.get(f'/doacoes/{l}').json()['status'],client.get('/dashboard').json()['coletas']))


def test_c06_cancelar_reserva(client, record_property):
    l,i = preparar(client)
    r = reservar(client,l,i,5)
    cancelamento = client.delete(f'/reservas/{r.json()["id"]}')
    registrar(record_property,'C06 - Cancelamento devolve saldo',(200,0),
              (cancelamento.status_code,client.get(f'/doacoes/{l}').json()['quantidade_reservada']))


def test_c07_acesso_sem_chave(client, record_property):
    r = client.get('/dashboard',headers={'Authorization':''})
    registrar(record_property,'C07 - Requisição sem chave é bloqueada',401,r.status_code)


def test_c08_arquivos_interface(client, record_property):
    resultados = tuple(client.get(p).status_code for p in ['/app','/static/app.js','/static/style.css','/openapi.json'])
    registrar(record_property,'C08 - Interface, recursos e contrato disponíveis',(200,200,200,200),resultados)


def test_health_banco_indisponivel(client,monkeypatch):
    engine = MagicMock()
    engine.connect.side_effect = SQLAlchemyError('detalhe interno')
    monkeypatch.setattr('main.engine',engine)
    response = client.get('/health')
    assert response.status_code==503
    assert response.json()=={'status':'indisponivel','banco':'erro'}
    assert 'detalhe interno' not in response.text


@pytest.mark.parametrize('token',['','curto'])
def test_inicializacao_rejeita_chave_fraca(monkeypatch,token):
    monkeypatch.setenv('API_TOKEN',token)
    with pytest.raises(ValueError,match='API_TOKEN'):
        validar_ambiente()


def test_inicializacao_porta_e_diretorio(monkeypatch,tmp_path):
    monkeypatch.setenv('API_TOKEN','x'*40)
    monkeypatch.setenv('PORT','10000')
    monkeypatch.setenv('DATABASE_URL','sqlite:///'+str(tmp_path/'dados'/'app.db'))
    assert validar_ambiente()==10000
    assert (tmp_path/'dados').is_dir()


@pytest.mark.parametrize('porta',['0','65536','abc'])
def test_inicializacao_porta_invalida(monkeypatch,porta):
    monkeypatch.setenv('API_TOKEN','x'*40)
    monkeypatch.setenv('PORT',porta)
    with pytest.raises(ValueError):
        validar_ambiente()
