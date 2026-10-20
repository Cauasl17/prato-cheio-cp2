"""Verifica um serviço HTTP local, em contêiner ou publicado."""
import argparse
from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import secrets
import time
import urllib.request
import urllib.error


def cnpj():
    digitos = [secrets.randbelow(10) for _ in range(8)] + [0, 0, 0, 1]
    for pesos in ([5,4,3,2,9,8,7,6,5,4,3,2], [6,5,4,3,2,9,8,7,6,5,4,3,2]):
        resto = sum(a*b for a,b in zip(digitos,pesos)) % 11
        digitos.append(0 if resto < 2 else 11-resto)
    return ''.join(map(str, digitos))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--exercise', action='store_true', help='Cria dados fictícios e registra uma coleta.')
    parser.add_argument('--output', default='evidencias/smoke.json')
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    if not base.startswith(('http://', 'https://')):
        parser.error('Informe uma URL HTTP(S).')
    token = os.getenv('API_TOKEN', '')
    passos = []

    def request(path, expected, method='GET', data=None, auth=True):
        headers = {'Content-Type':'application/json'}
        if auth and token:
            headers['Authorization'] = 'Bearer ' + token
        req = urllib.request.Request(base+path, headers=headers, method=method,
              data=json.dumps(data).encode() if data is not None else None)
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                status, body = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, body = error.code, error.read()
        passos.append({'metodo':method,'rota':path,'esperado':expected,'obtido':status,'aprovado':status==expected})
        assert status == expected, f'{method} {path}: esperado {expected}, obtido {status}'
        if body and 'json' in (response.headers.get('Content-Type','') if status < 400 else ''):
            return json.loads(body)
        try:
            return json.loads(body)
        except (ValueError, TypeError):
            return body.decode(errors='replace')

    inicio = time.monotonic()
    try:
        request('/health',200,auth=False)
        request('/app',200,auth=False)
        request('/openapi.json',200,auth=False)
        request('/dashboard',401,auth=False)
        if args.exercise:
            if not token:
                raise ValueError('Configure API_TOKEN no ambiente para executar o fluxo autenticado.')
            doador = request('/doadores',201,'POST',{
                'cnpj':cnpj(),'nome':'Doador Demonstração CP3','tipo':'PADARIA',
                'email':'doador@example.com','telefone':'11999999999','cidade':'São Paulo'})
            instituicao = request('/instituicoes',201,'POST',{
                'cnpj':cnpj(),'nome':'Instituição Demonstração CP3','responsavel':'Equipe CP3',
                'email':'instituicao@example.com','telefone':'11988888888','cidade':'São Paulo',
                'possui_refrigeracao':True})
            lote = request('/doacoes',201,'POST',{
                'doador_id':doador['id'],'descricao':'Lote fictício de demonstração CP3',
                'categoria':'PANIFICACAO','tipo_armazenamento':'AMBIENTE','unidade':'UNIDADE',
                'quantidade_total':2,'data_validade':(date.today()+timedelta(days=2)).isoformat(),
                'local_retirada':'Balcão de demonstração'})
            request('/reservas',422,'POST',{'doacao_id':lote['id'],'instituicao_id':instituicao['id'],'quantidade':3})
            reserva = request('/reservas',201,'POST',{'doacao_id':lote['id'],'instituicao_id':instituicao['id'],'quantidade':2})
            request(f'/reservas/{reserva["id"]}/coletar',200,'PATCH')
            salvo = request(f'/doacoes/{lote["id"]}',200)
            assert salvo['status']=='COLETADA' and salvo['quantidade_reservada']==2
            request('/dashboard',200)
    finally:
        output = Path(args.output)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps({'executado_em':datetime.now(timezone.utc).isoformat(),
            'base_url':base,'duracao_s':round(time.monotonic()-inicio,3),
            'passos':passos},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Verificação HTTP aprovada: {len(passos)} requisições; relatório em {args.output}.')


if __name__ == '__main__':
    main()
