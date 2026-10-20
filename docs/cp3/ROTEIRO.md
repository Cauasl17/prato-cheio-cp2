# Roteiro de apresentação e demonstração

Duração sugerida: 8 a 10 minutos. Os papéis abaixo organizam a apresentação e não representam
um registro de autoria individual do código.

1. Leonardo: explicar o problema, público e fluxo de doação. Mostrar a arquitetura.
2. João Paulo: explicar SQLite, chaves estrangeiras e controle de saldo. Mostrar o Dockerfile,
   usuário sem root, volume e variáveis de ambiente sem exibir a chave.
3. Pedro: abrir a interface, cadastrar lote fictício, mostrar erro de reserva acima do saldo,
   criar reserva válida e registrar coleta. Mostrar o dashboard após atualizar.
4. Cauã: mostrar os oito cenários e resultados do pytest, fluxo HTTP e evidências Docker.
   Explicar a diferença entre teste simulado de contrato e geração real da LLM.
5. Mostrar `/health` no ambiente disponível. Somente apresentar deploy como concluído após
   registrar a URL HTTPS real e executar `scripts/smoke.py` contra ela.
6. Explicar assinatura proposta e simulação de custos, deixando explícitas as premissas.
7. Mostrar Trello e links do repositório. Encerrar com limitações e próximos passos.

Todos devem conseguir responder: por que o saldo não pode ficar negativo, o que ocorre em
reservas concorrentes, onde o banco fica, o que persiste após restart, como a chave é fornecida,
o que significam 401/409/422/503 e como o healthcheck detecta falhas.

Usar apenas dados fictícios. O protótipo não faz avaliação sanitária, pagamentos ou logística.
A apresentação de CP3 está em APRESENTACAO_CP3.pptx. A de CP2 permanece como histórico no repositório.
