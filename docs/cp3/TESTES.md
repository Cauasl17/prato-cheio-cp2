# Testes do CP3

Execução em 20/10/2026: 39 testes aprovados. Cobertura de linhas: 80% nos módulos
crud, security, config, routers e services. Essa medição não representa cobertura de todo o frontend.

## Cenários funcionais

Os resultados abaixo são extraídos das propriedades do relatório JUnit da execução.
Cada teste utiliza um banco temporário isolado, com dados fictícios.

| Cenário | Esperado | Obtido | Resultado |
|---|---|---|---|
| C01 - Saúde da API e conexão SQL | (200, 'ok', 'ok') | (200, 'ok', 'ok') | Aprovado |
| C02 - Cadastro válido persistido | (201, 'Padaria Teste') | (201, 'Padaria Teste') | Aprovado |
| C03 - CNPJ inválido rejeitado | (422, 0) | (422, 0) | Aprovado |
| C04 - Reserva acima do saldo não altera estoque | (422, 0) | (422, 0.0) | Aprovado |
| C05 - Coleta atualiza lote e dashboard | (200, 'COLETADA', 1) | (200, 'COLETADA', 1) | Aprovado |
| C06 - Cancelamento devolve saldo | (200, 0) | (200, 0.0) | Aprovado |
| C07 - Requisição sem chave é bloqueada | 401 | 401 | Aprovado |
| C08 - Interface, recursos e contrato disponíveis | (200, 200, 200, 200) | (200, 200, 200, 200) | Aprovado |

## Integração e evidências

- `evidencias/pytest.xml`: resultados individuais dos 39 testes.
- `evidencias/coverage.xml` e `evidencias/testes.txt`: cobertura e saída do pytest.
- `evidencias/http-smoke.json`: 12 requisições HTTP reais contra processo Uvicorn local.
- `evidencias/http-runtime.txt`: log dessa execução, sem a chave de acesso.
- GitHub Actions: construção da imagem, execução do contêiner e persistência após reinício.

Códigos verificados: 200/201 para operações válidas, 401 sem autenticação,
409 para conflito e 422 para dados/regras inválidos. O healthcheck retorna 503
quando a conexão SQL falha e omite detalhes internos.

## Correções realizadas

1. Remoção da chave administrativa dos logs do contêiner.
2. Inicialização exige chave de 32 caracteres ou mais e valida PORT.
3. Diretório do banco criado antes da inicialização, permitindo paths da hospedagem.
4. Seed passou a ser uma opção explícita, preservando dados existentes.
5. Contêiner executa com usuário sem root e imagem não inclui segredos ou bancos locais.
6. Healthcheck verifica SQL e permite monitorar disponibilidade.

## Limites de validação

Os testes de contrato da LLM usam substituição controlada do cliente HTTP.
A geração real foi aprovada no CI em 20/10/2026: HTTP 200 e histórico confirmado.
Evidência: `evidencias/ci/llm-real.json`. O texto produzido contém interpretações imprecisas e
termina truncado pelo limite de geração; o teste verifica integração e persistência, não a qualidade semântica.
O smoke HTTP verifica entrega dos arquivos do frontend e o fluxo da API, sem equivaler
a um teste visual de cliques no navegador. A demonstração no deploy só deve ser registrada
após existir uma URL publicada e uma execução contra esse endereço.

## Reprodução

```bash
pip install -r requirements-dev.txt
python -m pytest --junitxml=evidencias/pytest.xml --cov=crud --cov=security --cov=config --cov=routers --cov=services --cov-report=term-missing --cov-report=xml:evidencias/coverage.xml
```
