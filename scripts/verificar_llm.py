"""Registra a geração real e a persistência de um relatório da LLM."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.request

parser=argparse.ArgumentParser()
parser.add_argument('--base-url',default='http://127.0.0.1:8000')
parser.add_argument('--output',default='evidencias/llm-real.json')
args=parser.parse_args()
base=args.base_url.rstrip('/')
headers={'Authorization':'Bearer '+os.environ['API_TOKEN']}
request=urllib.request.Request(base+'/ia/relatorio',headers=headers,method='POST')
with urllib.request.urlopen(request,timeout=180) as response:
    status=response.status
    relatorio=json.load(response)
assert status==200 and relatorio['origem']=='ollama' and relatorio['texto'].strip()
with urllib.request.urlopen(urllib.request.Request(base+'/ia/relatorios',headers=headers),timeout=15) as response:
    historico=json.load(response)
assert any(r['id']==relatorio['id'] and r['texto']==relatorio['texto'] for r in historico)
resultado={'executado_em':datetime.now(timezone.utc).isoformat(),'base_url':base,
    'http_status':status,'modelo':relatorio['modelo'],'origem':relatorio['origem'],
    'relatorio_id':relatorio['id'],'persistencia_confirmada':True,
    'texto':relatorio['texto'],'aviso':relatorio['aviso']}
output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('LLM real: geração e histórico confirmados. Revise a qualidade do texto no relatório.')
