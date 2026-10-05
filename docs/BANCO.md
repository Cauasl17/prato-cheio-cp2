# Revisão do banco

## Relacionamentos

Doador 1:N Doação. Doação 1:N Reserva. Instituição 1:N Reserva.
Relatório de IA armazena modelo, texto e data sem repetir dados de cadastro.
As tabelas representam entidades separadas e as referências utilizam IDs.
O campo de quantidade comprometida mantém a estrutura do CP1 e acelera a verificação do saldo.
A redundância requer transação. Cancelar um lote preserva a quantidade coletada e cancela só pendências.

## Integridade

CNPJ único em cada tipo de cadastro. FK ativa por conexão SQLite.
CHECK: quantidade_total > 0, 0 <= quantidade_reservada <= quantidade_total e reserva.quantidade > 0.
Registros com histórico de doações/reservas não podem ser apagados.
A aplicação bloqueia reserva pendente duplicada e usa uma transação de escrita SQLite.

## Índices

`ix_doacao_busca(status, data_validade, categoria)`, `ix_doacao_doador(doador_id)`,
`ix_reserva_doacao(doacao_id)` e `ix_reserva_instituicao_status(instituicao_id, status)`.
O índice composto favorece consultas que começam com status.
Uma busca somente por categoria pode continuar varrendo a tabela: não há alegação de otimização universal.

## Migração de um SQLite do CP1

O ZIP inclui um banco novo com a estrutura CP2. `create_all` não altera tabelas antigas.
Para preservar um banco CP1 real, pare a API e faça uma cópia de segurança.
Execute `python migrar_cp1.py caminho_do_banco_antigo.db caminho_do_banco_cp2.db`.
O destino deve ser um arquivo novo. O script cria a estrutura CP2 e copia os registros,
validando FKs, checks e coerência do saldo. Em caso de falha, o arquivo antigo fica intacto.
Depois configure DATABASE_URL para o novo banco. Confira os registros antes de retomar a API.
