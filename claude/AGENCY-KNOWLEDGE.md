# AGENCY KNOWLEDGE SYSTEM

O Agency Knowledge Engine é a camada de conhecimento operacional da agência.

## Ordem de consulta

Ao responder ou executar tarefas da agência, use esta prioridade:

1. Knowledge Base validada
2. Sources validadas
3. Sources externas em processo de validação
4. Pesquisa externa atualizada
5. Inferência própria, claramente identificada como inferência

## Proveniência

Nunca trate automaticamente uma fonte externa como conhecimento validado.

Diferencie sempre:

- FACT — fato sustentado por fonte
- CLAIM — afirmação que precisa de contexto ou validação
- FRAMEWORK — método ou estrutura
- RULE — regra operacional
- HYPOTHESIS — hipótese
- OPINION — opinião

## Google Ads

Para políticas, requisitos e regras atuais do Google Ads:

- priorizar documentação oficial do Google;
- verificar atualização da informação;
- preservar URL e data da fonte;
- não transformar interpretação em política oficial.

## Knowledge Base

Local principal:

~/.agency/knowledge/

Sources:

~/.agency/sources/

Fila:

~/.agency/queue/

## Regra de segurança

Não sobrescrever conhecimento existente automaticamente.

Não inventar fatos para preencher lacunas.

Quando houver conflito entre fontes, preservar o conflito e indicar qual fonte é mais recente ou mais autoritativa.

Quando a informação puder ter mudado, pesquisar e validar antes de tratá-la como atual.

## Agency CLI

Comandos principais:

agency status
agency dashboard
agency ingest URL
agency queue
agency queue classify ID AREA PRIORIDADE
agency next
agency next --research
agency validate ID
agency knowledge ID
agency research URL AREA PRIORIDADE
agency research queue

## Objetivo

Transformar pesquisa externa em conhecimento:

PESQUISA
→ FONTE
→ CLASSIFICAÇÃO
→ VALIDAÇÃO
→ EXTRAÇÃO
→ KNOWLEDGE
→ OPERAÇÃO

Sempre preservar rastreabilidade.
