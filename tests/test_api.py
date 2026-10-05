from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import httpx
import pytest
from sqlalchemy import text
from database import engine

D={'cnpj':'11222333000181','nome':'Padaria Teste','tipo':'PADARIA','email':'padaria@example.com','telefone':'11999999999','cidade':'São Paulo'}
I={'cnpj':'02558157000162','nome':'ONG Teste','responsavel':'Responsável','email':'ong@example.com','telefone':'11988888888','cidade':'São Paulo','possui_refrigeracao':True}
def preparar(c, armazenamento='AMBIENTE'):
    d=c.post('/doadores',json=D); assert d.status_code==201,d.text
    i=c.post('/instituicoes',json=I); assert i.status_code==201,i.text
    lote={'doador_id':d.json()['id'],'descricao':'Pães embalados','categoria':'PANIFICACAO','tipo_armazenamento':armazenamento,'unidade':'KG','quantidade_total':10,'data_validade':(date.today()+timedelta(days=1)).isoformat(),'local_retirada':'Balcão'}
    r=c.post('/doacoes',json=lote); assert r.status_code==201,r.text
    return r.json()['id'],i.json()['id']
def reservar(c,l,i,q):return c.post('/reservas',json={'doacao_id':l,'instituicao_id':i,'quantidade':q})
def test_fluxo_reserva_coleta(client):
    l,i=preparar(client);r=reservar(client,l,i,10);assert r.status_code==201
    assert client.patch(f'/reservas/{r.json()["id"]}/coletar').status_code==200
    assert client.get(f'/doacoes/{l}').json()['status']=='COLETADA'
    assert client.get('/dashboard').json()['coletas']==1

def test_cancelamento_devolve_saldo(client):
    l,i=preparar(client);r=reservar(client,l,i,6)
    assert client.delete('/reservas/'+str(r.json()['id'])).status_code==200
    assert client.get('/doacoes/'+str(l)).json()['quantidade_reservada']==0

def test_cancelamento_preserva_coleta_parcial(client):
    l,i=preparar(client);r=reservar(client,l,i,4).json();client.patch(f'/reservas/{r["id"]}/coletar')
    r2=reservar(client,l,i,3).json();client.patch(f'/doacoes/{l}/cancelar')
    assert client.get(f'/doacoes/{l}').json()['quantidade_reservada']==4
    assert client.get(f'/reservas/{r2["id"]}').json()['status']=='CANCELADA'
    assert client.get('/dashboard').json()['coletas']==1

def test_sem_refrigeracao(client):
    l,i=preparar(client,'REFRIGERADO');client.put(f'/instituicoes/{i}',json={'possui_refrigeracao':False})
    assert reservar(client,l,i,2).status_code==422

def test_saldo_e_reserva_duplicada(client):
    l,i=preparar(client);assert reservar(client,l,i,11).status_code==422
    assert reservar(client,l,i,5).status_code==201
    assert reservar(client,l,i,1).status_code==409

@pytest.mark.parametrize('dados',[{'quantidade_total':0},{'quantidade_total':-1},{'descricao':' '},{'data_validade':'2000-01-01'},{'quantidade_total':None},{'categoria':None},{'campo_extra':1}])
def test_edicao_invalida(client,dados):
    l,i=preparar(client);assert client.put(f'/doacoes/{l}',json=dados).status_code==422
    assert client.get(f'/doacoes/{l}').json()['quantidade_total']==10

def test_inativos(client):
    l,i=preparar(client);client.put(f'/instituicoes/{i}',json={'ativo':False})
    assert reservar(client,l,i,1).status_code==422

def test_cnpj_duplicado_e_invalido(client):
    assert client.post('/doadores',json=D).status_code==201
    assert client.post('/doadores',json=D).status_code==409
    assert client.post('/doadores',json={**D,'cnpj':'11111111111111'}).status_code==422

def test_integridade_exclusao(client):
    l,i=preparar(client);r=reservar(client,l,i,3).json();client.patch(f'/reservas/{r["id"]}/coletar');client.patch(f'/doacoes/{l}/cancelar')
    for rota in [f'/doadores/1',f'/instituicoes/{i}',f'/doacoes/{l}']:
        assert client.delete(rota).status_code==409

def test_filtros_paginacao(client):
    preparar(client);a=client.get('/doacoes?categoria=LATICINIOS').json();assert a['total']==0
    assert client.get('/doacoes?pagina=2&limite=1').json()['itens']==[]
    assert client.get('/doacoes?limite=101').status_code==422

def test_dashboard_unidades_e_alertas(client):
    l,i=preparar(client);d=client.get('/dashboard').json()
    assert d['saldo_por_unidade']==[{'unidade':'KG','quantidade':10}]
    assert d['alertas'][0]['id']==l
    reservar(client,l,i,4)
    assert client.get('/dashboard').json()['saldo_por_unidade'][0]['quantidade']==6

def test_auth(client):
    assert client.get('/dashboard',headers={'Authorization':'Bearer incorreto'}).status_code==401
    assert client.post('/doadores',json=D,headers={'Authorization':''}).status_code==401

def test_swagger_e_interface(client):
    s=client.get('/openapi.json').json()
    assert '/ia/relatorio' in s['paths']
    assert s['paths']['/doacoes']['post']['security']
    assert client.get('/app').status_code==200
    assert client.get('/static/app.js').status_code==200

def test_coleta_vencida(client):
    l,i=preparar(client);r=reservar(client,l,i,2).json()
    with engine.begin() as conn:conn.execute(text("UPDATE doacoes SET data_validade='2000-01-01'"))
    assert client.patch(f'/reservas/{r["id"]}/coletar').status_code==422
    assert client.get('/dashboard').json()['disponiveis']==0

def test_duas_reservas_concorrentes(client):
    l,i=preparar(client);j=client.post('/instituicoes',json={**I,'cnpj':'47960950000121','nome':'ONG 2'}).json()['id']
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados=list(pool.map(lambda k:reservar(client,l,k,7).status_code,[i,j]))
    assert sorted(resultados)==[201,422]
    assert client.get(f'/doacoes/{l}').json()['quantidade_reservada']==7

def test_llm_integracao_simulada_e_privacidade(client,monkeypatch):
    preparar(client);recebido={}
    class FakeClient:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,url,json):
            recebido.update(json)
            return httpx.Response(200,json={'response':'Priorize o lote #1.'},request=httpx.Request('POST',url))
    monkeypatch.setattr('services.llm.httpx.AsyncClient',FakeClient)
    r=client.post('/ia/relatorio');assert r.status_code==200,r.text
    assert r.json()['origem']=='ollama'
    prompt=recebido['prompt']
    assert D['email'] not in prompt and D['cnpj'] not in prompt and I['nome'] not in prompt
    assert json.loads(prompt)['alertas'][0]['id']==1
    assert client.get('/ia/relatorios').json()[0]['texto']=='Priorize o lote #1.'

def test_llm_indisponivel_sem_fallback(client,monkeypatch):
    class FakeClient:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,*args,**kwargs):raise httpx.ConnectError('offline')
    monkeypatch.setattr('services.llm.httpx.AsyncClient',FakeClient)
    assert client.post('/ia/relatorio').status_code==503
    assert client.get('/ia/relatorios').json()==[]

def test_reinicio_persistencia(client):
    preparar(client)
    from database import SessionLocal
    import models
    with SessionLocal() as db:assert db.query(models.Doacao).count()==1
