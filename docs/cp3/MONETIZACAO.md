# Proposta de monetização

## Público e problema

Padarias, mercados e pequenos restaurantes que doam excedentes com frequência precisam organizar lotes,
reservas e retiradas. Instituições recebedoras precisam consultar saldo e condições de armazenamento.
O sistema reduz a dependência de mensagens dispersas e mantém o histórico operacional.
Não há economia de alimentos ou redução de custos medida em cliente nesta entrega.

## Modelo de receita

Assinatura de R$ 99 por estabelecimento/mês para acesso à gestão de doações, dashboard, histórico
e suporte em horário comercial. Instituições recebedoras teriam acesso gratuito.
Cobrar do estabelecimento preserva a participação de quem recebe as doações.
O preço é uma hipótese comercial para validação, sem pesquisa de disposição a pagar.
A versão atual usa chave administrativa compartilhada; uma oferta comercial exige contas individuais,
isolamento entre organizações, trilha de auditoria, contrato e política de tratamento de dados.

## Simulação mensal

| Item | Premissa | Valor |
|---|---|---:|
| Receita | 20 estabelecimentos x R$ 99 | R$ 1.980 |
| Hospedagem da aplicação | Reserva de orçamento | R$ 150 |
| Persistência e backups | Reserva de orçamento | R$ 50 |
| Execução da LLM | Reserva de orçamento | R$ 80 |
| Manutenção e suporte | 8 horas x R$ 40 | R$ 320 |
| Ferramentas e administração | Reserva de orçamento | R$ 70 |
| Custo operacional estimado | Soma dos cinco custos | R$ 670 |
| Saldo operacional estimado | Receita menos custos | R$ 1.310 |

O saldo corresponde a aproximadamente 66,2% da receita. Não representa lucro líquido:
tributos, taxas de recebimento, aquisição de clientes e desenvolvimento inicial não estão incluídos.
Todos os custos acima são premissas de planejamento, não cotações de fornecedores.

Com o custo fixo simplificado de R$ 670 e sem custo variável adicional por cliente, o ponto de equilíbrio
é 7 assinaturas (arredondamento de 670 / 99). A estrutura de custos precisa ser recalculada quando
crescer o volume de usuários, suporte ou inferências. Com 5 clientes, a receita seria R$ 495,
insuficiente para cobrir essa estrutura. Com 10, seria R$ 990 e o saldo R$ 320.

## Viabilidade e próximos passos

Começar com um piloto em poucos estabelecimentos para medir frequência de uso, disponibilidade de
retirada, esforço de suporte e interesse em pagar. O modelo pequeno local evita cobrança por token,
mas exige CPU/memória e operação do serviço. O custo de inferência não desaparece.
A hospedagem gratuita proposta para demonstração não compõe a infraestrutura comercial:
o SQLite efêmero desse ambiente precisa ser substituído por armazenamento persistente e backup.
Não há gateway de pagamento ou cobrança automática implementados, conforme permitido no CP3.
