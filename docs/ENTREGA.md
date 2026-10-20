# Entregáveis do CP3

| Requisito | Arquivo/evidência | Situação |
|---|---|---|
| Cenários e testes automatizados | tests/, docs/cp3/TESTES.md | 39 testes aprovados |
| Resultados esperados e obtidos | evidencias/pytest.xml | Oito cenários registrados |
| Fluxo integrado por HTTP | evidencias/http-smoke.json e evidencias/deploy-fluxo.json | 12 requisições locais e 12 no deploy aprovadas |
| Containerização | Dockerfile, compose.yaml e GitHub Actions | Construção e fluxo verificados |
| Persistência no contêiner | Evidência do CI após docker restart | Verificada |
| Deploy | https://prato-cheio-cp3.onrender.com e evidencias/deploy-fluxo.json | Publicado em HTTPS |
| Monetização | docs/cp3/MONETIZACAO.md | Proposta e simulação incluídas |
| GitHub e equipe | README.md e INTEGRANTES_E_LINKS.txt | Incluídos |
| Organização ágil | https://trello.com/b/x4UExcxZ/trello-cp | Atualização CP3 no quadro |
| Apresentação | APRESENTACAO_CP3.pptx e docs/cp3/ROTEIRO.md | Preparadas |
| Cliente real | Opcional no enunciado | Não realizado |

O serviço gratuito tem SQLite efêmero e não hospeda a LLM; os limites constam em docs/cp3/DEPLOY.md.
