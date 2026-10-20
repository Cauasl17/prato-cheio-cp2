# Execução por Docker

## Configuração

Requisitos: Docker Engine/Desktop com Compose. Na pasta do projeto:

```bash
python scripts/configurar.py
docker compose build
docker compose up -d
docker compose ps
```

O inicializador cria uma chave aleatória no `.env` apenas se o arquivo ainda não existir.
Ler `API_TOKEN` localmente e utilizá-la no login de `/app` ou no botão Authorize do Swagger.
Os logs do contêiner não imprimem essa chave. A porta fica restrita ao próprio computador.

Interface: http://127.0.0.1:8000/app
Swagger: http://127.0.0.1:8000/docs
Saúde: http://127.0.0.1:8000/health

## LLM opcional

```bash
docker compose --profile llm up -d
docker compose logs -f ollama-init
```

Aguardar o download de `qwen2.5:0.5b`. A API continua disponível quando o Ollama está indisponível;
somente a geração de relatórios retorna 503. O modelo exige espaço em disco, memória e CPU.
Para baixar uma imagem reproduzível de produção, fixar o digest do Ollama após homologação;
a demonstração usa a tag `latest` e registra a execução no CI.

## Construção e execução sem Compose

Com API_TOKEN já definido de forma privada no ambiente:

```bash
docker build -t prato-cheio:cp3 .
docker run -d --name prato-cheio -p 127.0.0.1:8000:8000 -e API_TOKEN -e SEED_DEMO=true -v prato-dados:/dados prato-cheio:cp3
docker ps --filter name=prato-cheio
docker logs prato-cheio
python scripts/smoke.py --exercise
```

## Persistência e encerramento

A imagem executa com UID 10001, sem root, e grava em `/dados`. O volume mantém o SQLite
quando o contêiner é recriado. Para verificar o histórico após reiniciar:

```bash
docker compose restart api
```

Após o serviço voltar a responder em `/health`, consultar o lote e a reserva antes criados.
`docker compose down` preserva os volumes; `docker compose down -v` apaga os bancos e modelos.
Não usar `-v` para encerrar uma demonstração cujo histórico precisa ser mantido.

## Automação e evidências

`.github/workflows/cp3.yml` instala dependências, executa pytest, constrói a imagem,
inicia o contêiner, valida 12 requisições, reinicia e verifica a persistência.
Os arquivos do artefato `evidencias-cp3` incluem logs, estado do contêiner, resultado HTTP,
JUnit e cobertura. O token temporário é aleatório e mascarado pelo GitHub Actions.
Os arquivos da imagem são limitados ao código, dependências e frontend; não incluem `.env`,
banco de demonstração, testes, evidências ou histórico Git.
