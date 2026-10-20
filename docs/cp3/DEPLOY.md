# Deploy e acesso

## Serviço publicado

- API: https://prato-cheio-cp3.onrender.com
- Interface: https://prato-cheio-cp3.onrender.com/app
- Swagger: https://prato-cheio-cp3.onrender.com/docs
- Saúde: https://prato-cheio-cp3.onrender.com/health
- Painel do proprietário: https://dashboard.render.com/web/srv-dbbusb3ncjis73fdlau0

O Render publicou o contêiner Docker no plano gratuito, região Virginia. Deploy
`dep-dbbusbjncjis73fdld60`, concluído em 20/10/2026, com código do commit
`b6317d44bc58888ec31be4d26df772ea81a2c5f8`.
A API responde por HTTPS e usa a porta fornecida pelo provedor.

## Acesso administrativo

As operações de negócio exigem Bearer token. O proprietário obtém `API_TOKEN` na seção
Environment do painel do serviço e fornece a chave ao avaliador por um meio privado.
Ela não consta no repositório, nos slides nem no ZIP. No Swagger, clicar em Authorize e
informar essa chave. Na interface, usar o campo de chave administrativa.
A página inicial, os arquivos da interface, o contrato OpenAPI e `/health` são públicos.

## Configurações

| Item | Configuração |
|---|---|
| Runtime | Docker, Dockerfile na raiz |
| Plano | free |
| Região | Virginia |
| PORT | Fornecida pelo Render |
| DATABASE_URL | sqlite:////tmp/prato-cheio/prato_cheio.db |
| SEED_DEMO | true, apenas em banco vazio |
| API_TOKEN | Valor aleatório privado, configurado no ambiente |
| OLLAMA_URL | http://127.0.0.1:11434, sem modelo hospedado |
| OLLAMA_MODEL | qwen2.5:0.5b |
| Auto-deploy | Desativado; novas versões exigem deploy manual |

O healthcheck da imagem Docker consulta `/health`. O serviço expõe esse endpoint para
verificação HTTP; a configuração direta do Render utiliza a verificação padrão do provedor.
`render.yaml` permanece como alternativa para recriar o ambiente por Blueprint.

## Verificação do fluxo público

Com `API_TOKEN` definido no ambiente do terminal, executar:

```bash
python scripts/smoke.py --base-url https://prato-cheio-cp3.onrender.com --exercise --output evidencias/deploy-fluxo.json
```

O script verifica saúde, interface, contrato, bloqueio sem chave, cadastro de doador e instituição,
lote, reserva acima do saldo (422), reserva válida, coleta, lote persistido e dashboard.
Ele cria dados fictícios identificados como demonstração CP3 e registra códigos esperados/obtidos,
sem salvar credenciais. A evidência da execução está em `evidencias/deploy-fluxo.json`.

## Atualização

Publicar o código no GitHub, abrir o painel e usar Manual Deploy para a versão desejada.
Confirmar o estado live, consultar `/health` e repetir o script de verificação.
Os commits de documentação podem ser posteriores ao commit da imagem publicada, sem alterar
a versão do código de aplicação que foi validada.

## Persistência e limites

O disco do plano gratuito é efêmero: reinícios/redeploys podem apagar os dados. O provedor também
pode suspender instâncias gratuitas ociosas, exigindo aguardar a retomada no primeiro acesso.
`SEED_DEMO=true` recria exemplos somente em banco vazio. Não usar esse ambiente para histórico
operacional real. Persistência durável exige um volume/serviço adequado e backup.
Nenhum recurso pago foi contratado.

O Ollama não acompanha o serviço web gratuito. `/ia/status` sinaliza indisponibilidade e
`/ia/relatorio` retorna 503 quando não há modelo, sem resposta inventada. A geração real foi
verificada separadamente no CI e no seu histórico, em `evidencias/ci/llm-real.json`.
O Compose permite essa integração em ambiente isolado. Para levá-la à hospedagem, será
necessário um serviço de inferência acessível com controle de acesso. Não expor a porta 11434
diretamente na internet. O teste de integração não elimina os erros de interpretação da LLM.

## Fontes técnicas

- https://render.com/docs/blueprint-spec
- https://render.com/docs/web-services
- https://render.com/docs/health-checks
- https://render.com/docs/free
