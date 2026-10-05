# Roteiro do CP2 (8 a 10 minutos)

Distribuição sugerida. Todos devem conhecer o fluxo inteiro.

| Integrante | Parte |
|---|---|
| Leonardo Viana - 571969 | Problema, escopo e evolução do CP1 |
| João Paulo Melo - 570118 | Arquitetura, banco e otimizações |
| Pedro Grigorio - 570308 | Interface, dashboard e demonstração das requisições |
| Cauã da Silva Lima - 571023 | Testes e LLM contextual |

## Demonstração

1. Abrir /app com a chave local. Mostrar dashboard e saldo separado por unidade.
2. Abrir Doações, filtrar categoria e disponibilidade. Mostrar que o dado vem do banco.
3. Criar uma doação do doador 1, AMBIENTE, 10 KG, validade futura.
4. Criar uma reserva de 4 KG para a instituição 1 usando o ID do lote criado.
5. Voltar ao lote e conferir 4 comprometidos. Cancelar a reserva e conferir saldo devolvido.
6. Reservar 10 KG, registrar coleta e mostrar o indicador de coletas atualizado.
7. No Swagger, autorizar com a mesma chave e mostrar GET /doacoes, POST /reservas e GET /dashboard.
8. Demonstrar erro: quantidade acima do saldo ou lote refrigerado para instituição 2 sem refrigeração.
9. Executar python -m pytest -q e explicar o teste concorrente.
10. Com Ollama disponível, gerar o relatório, mostrar o contexto enviado e consultar o histórico.
11. Mostrar o quadro Trello/Notion real após publicação. Os arquivos locais são apoio de organização.

## Perguntas técnicas

**Como evita duas reservas acima do saldo?** SQLite inicia uma transação de escrita e a atualização
confere saldo/status/validade. Reserva e quantidade comprometida são confirmadas juntas.

**O que mudou no banco?** Integridade referencial ativa, checks, índices e histórico da LLM.
A quantidade comprometida é uma redundância controlada que inclui valores já coletados.

**Por que separar unidades no dashboard?** KG, LITRO, UNIDADE e PORCAO não são comparáveis.

**A IA decide se o alimento pode ser doado?** Não. A IA resume indicadores e sugere prioridade.
O backend aplica as regras de validade, refrigeração, disponibilidade e quantidade.

**Os dados são reais?** São registros de demonstração persistidos no banco da aplicação.
O dashboard faz consultas reais a esse banco. Não são operações reais de uma instituição.

**Qual limitação da autenticação?** É uma chave administrativa compartilhada para o protótipo.
Não existe isolamento de acesso por doador/instituição nesta versão.
