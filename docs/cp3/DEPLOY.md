# Deploy e acesso

## Situação da publicação

O serviço está preparado para hospedagem por Docker. A publicação em provedor e o endereço HTTPS
permanecem pendentes de autenticação na conta de hospedagem. GitHub Actions executa validação temporária;
o endereço do runner não é uma API publicada nem substitui o requisito de deploy.

## Publicação no Render

O arquivo `render.yaml` configura um serviço Docker de demonstração no plano gratuito,
com `/health` como verificação de disponibilidade, chave administrativa gerada pelo provedor
e banco SQLite em `/tmp/prato-cheio/prato_cheio.db`.

1. Entrar em https://dashboard.render.com e criar um Blueprint a partir de
   https://github.com/Cauasl17/prato-cheio-cp2 .
2. Conferir o plano gratuito antes de confirmar a criação. O nome do serviço pode receber um sufixo;
   usar somente a URL efetivamente fornecida pelo Render.
3. Aguardar a construção e o deploy. A aplicação usa a variável `PORT` fornecida pela hospedagem.
4. Conferir `GET /health`, que precisa retornar 200 com `status=ok` e `banco=ok`.
5. Acessar `/app` ou `/docs`. Obter `API_TOKEN` no painel de variáveis do serviço e fornecê-la
   apenas ao avaliador por meio privado. Não anexar a chave ao repositório ou ao ZIP público.
6. Atualizar o campo de endereço do deploy no README com a URL real.

## Verificação após publicar

Executar primeiro, sem chave:

```bash
python scripts/smoke.py --base-url https://ENDERECO_REAL --output evidencias/deploy-saude.json
```

Para demonstrar cadastro, erro por saldo, reserva, coleta e consulta, definir `API_TOKEN` no
ambiente do terminal (sem incluí-la no comando ou relatório) e executar:

```bash
python scripts/smoke.py --base-url https://ENDERECO_REAL --exercise --output evidencias/deploy-fluxo.json
```

O fluxo cria registros fictícios identificados como demonstração CP3, que permanecem no histórico.
Utilizar somente o ambiente de avaliação, nunca dados de produção.
O JSON registra rotas e códigos esperados/obtidos, sem credenciais.

## Persistência e limites

No plano gratuito proposto, o disco do serviço é efêmero: reinícios/redeploys podem apagar os dados.
`SEED_DEMO=true` recria dados fictícios somente se o banco estiver vazio. Não usar esse plano para
histórico operacional real. Para persistência, usar um host com volume durável em `/dados`
ou contratar explicitamente um disco persistente e apontar `DATABASE_URL` para ele.
Nenhum recurso pago foi contratado nesta entrega.

O Ollama não acompanha o serviço web gratuito. A configuração padrão da hospedagem não oferece LLM:
`/ia/status` sinaliza indisponibilidade e `/ia/relatorio` retorna 503, sem resposta inventada.
Para disponibilizar a LLM, será necessário um serviço Ollama acessível por rede privada ou proxy
HTTPS autenticado, com revisão da configuração de acesso. Não expor a porta 11434 diretamente na internet.
O Compose local e o CI demonstram essa integração em ambiente isolado.

## Fontes técnicas

- https://render.com/docs/blueprint-spec
- https://render.com/docs/web-services
- https://render.com/docs/health-checks
- https://render.com/docs/free
