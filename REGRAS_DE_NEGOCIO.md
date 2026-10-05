# Prato Cheio - Definicao do Problema e Regras de Negocio

## 1. Problema

Padarias, mercados e restaurantes jogam fora todo dia comida que ainda esta boa para
consumo. Ao mesmo tempo, ONGs e casas de apoio precisam dessa comida para servir refeicoes.

O problema nao e falta de comida. E falta de organizacao entre quem tem a sobra e quem
precisa dela. Hoje isso e resolvido por telefone e grupo de WhatsApp, e por isso acontece:

- a instituicao nao sabe o que esta disponivel naquele momento
- duas instituicoes combinam a mesma sobra e uma perde a viagem
- alimento que precisa de geladeira vai parar em quem nao tem geladeira
- a comida vence antes de alguem buscar

E um problema com prazo: a sobra de hoje serve por 1 ou 2 dias, nao por uma semana.

## 2. Publico-alvo

- **Doadores**: padarias, mercados, restaurantes e hortifrutis que tem sobra todo dia
- **Instituicoes**: ONGs, casas de apoio e cozinhas comunitarias que servem refeicoes

## 3. Objetivo principal

Diminuir o desperdicio de comida que ainda esta boa, criando um lugar onde o doador
publica o que sobrou e a instituicao consegue reservar antes que estrague.

## 4. Principais funcionalidades

1. Cadastro de doadores
2. Cadastro de instituicoes, informando se tem geladeira
3. Cadastro de doacoes com quantidade, validade e tipo de armazenamento
4. Lista das doacoes que ainda estao disponiveis, com filtros
5. Reserva de uma parte ou de toda a doacao
6. Registro da coleta quando a instituicao busca o alimento
7. Cancelamento de reserva, devolvendo a quantidade para a doacao

## 5. Regras de negocio

| Numero | Regra | Codigo de erro |
|---|---|---|
| 1 | O CNPJ precisa ser valido e nao pode estar cadastrado duas vezes | 422 se invalido, 409 se repetido |
| 2 | Doador desativado nao pode cadastrar doacao | 422 |
| 3 | Nao pode cadastrar, reservar ou coletar alimento vencido | 422 |
| 4 | A quantidade reservada nao pode passar do que sobrou na doacao | 422 |
| 5 | Nao da para diminuir a quantidade da doacao abaixo do que ja foi reservado | 422 |
| 6 | Instituicao desativada nao pode fazer reserva | 422 |
| 7 | So da para reservar doacao com status DISPONIVEL ou PARCIALMENTE_RESERVADA | 422 |
| 8 | Alimento REFRIGERADO ou CONGELADO so vai para instituicao que tem refrigeracao | 422 |
| 9 | Nao da para apagar doador que ainda tem doacao em aberto | 409 |
| 10 | Uma instituicao so pode ter uma reserva em aberto por doacao | 409 |
| 11 | Cancelar a reserva devolve a quantidade para a doacao | 200 |

### Regra extra: o status da doacao e calculado, nao enviado

O usuario nunca manda o status da doacao. O sistema calcula sozinho olhando a quantidade
reservada. Isso esta na funcao `atualizar_status_doacao()` do arquivo `crud.py`:

- quantidade reservada igual a zero: DISPONIVEL
- quantidade reservada entre zero e o total: PARCIALMENTE_RESERVADA
- quantidade reservada igual ao total: RESERVADA
- todas as reservas coletadas e lote acabou: COLETADA
- doador cancelou: CANCELADA

O status da reserva funciona parecido:

```
PENDENTE -> COLETADA     (a instituicao buscou)
PENDENTE -> CANCELADA    (desistiu ou o doador cancelou a doacao)
```

Uma vez COLETADA ou CANCELADA, a reserva nao muda mais.

## 6. Entidades principais

| Entidade | O que representa |
|---|---|
| Doador | o estabelecimento que tem a sobra |
| Instituicao | a ONG ou casa de apoio que recebe |
| Doacao | o alimento que foi disponibilizado |
| Reserva | a instituicao marcando uma parte da doacao para ela |

## 7. Relacionamento entre as informacoes

```
Doador (1) -----> (N) Doacao (1) -----> (N) Reserva (N) <----- (1) Instituicao
```

- **Doador tem varias Doacoes**: um mercado pode publicar varias sobras diferentes
- **Doacao tem varias Reservas**: um lote de 100 kg pode ser dividido entre 3 instituicoes
- **Instituicao tem varias Reservas**: a ONG reserva de varios doadores diferentes

Doacao e Instituicao tem relacao de muitos para muitos. Quem resolve isso e a tabela
`reservas`. Ela nao e so uma tabela de ligacao porque guarda informacao propria: a
quantidade reservada, o status e a data da coleta.

## 8. Restricoes relevantes

- Alimento vence, entao a data de validade e conferida na hora de cadastrar, de reservar e
  de registrar a coleta
- A regra da refrigeracao existe por seguranca alimentar, nao e preferencia
- Doacao e reserva com historico nao sao apagadas do banco, sao canceladas. Assim da para
  saber depois o que aconteceu
- O campo `quantidade_reservada` so muda quando uma reserva e criada ou cancelada. Nenhuma
  rota deixa alterar esse campo direto

O que ficou de fora deste checkpoint:

- login e senha (todo mundo pode chamar qualquer rota)
- rotina automatica para marcar doacoes vencidas
- envio de e-mail ou mensagem para as instituicoes

## 9. Tecnologias inicialmente escolhidas

| Para que | Tecnologia | Por que escolhemos |
|---|---|---|
| Linguagem | Python 3.11 | e a linguagem da disciplina |
| API | FastAPI | ja gera a documentacao Swagger sozinho |
| Banco | SQLite | nao precisa instalar servidor para rodar |
| ORM | SQLAlchemy | evita escrever SQL na mao |
| Validacao | Pydantic | ja vem junto com o FastAPI |
| Servidor | Uvicorn | e o servidor que o FastAPI usa |
