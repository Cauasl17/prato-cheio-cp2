# Integração com LLM

A funcionalidade analisa os dados consolidados de doações. A interface consome
POST /ia/relatorio e mostra o texto. O backend guarda a resposta do modelo para consulta posterior.
O endpoint /ia/status confere se o modelo configurado está instalado no Ollama.
O prompt real e o contrato estão em services/llm.py. A resposta inclui dados_enviados para auditoria.
O histórico persiste texto/modelo/data, sem armazenar a cópia completa do contexto.

A documentação oficial utilizada para o contrato:
https://docs.ollama.com/api/generate
https://github.com/ollama/ollama/blob/main/docs/api.md
https://fastapi.tiangolo.com/tutorial/security/

## Preparação e demonstração

1. Instalar Ollama e baixar qwen2.5:0.5b (ou usar docker compose up --build).
2. Verificar /ia/status com disponível=true.
3. Gerar o relatório pela interface.
4. Mostrar dados enviados, texto obtido e histórico.
5. Explicar que a IA recomenda e as regras do backend continuam decidindo se uma reserva é aceita.

## Limites dos testes entregues

A suíte substitui o serviço externo em um teste de contrato para verificar payload,
privacidade, retorno e persistência. Esse teste não executa os pesos da LLM.
Outro teste garante 503 sem texto inventado quando o serviço falha.
A geração real depende do Ollama e do download do modelo no computador da apresentação.
Não há evidência de geração real nesta entrega.
