---
name: proposals
description: Criação de propostas comerciais estratégicas orientadas a valor, CRO, benchmark de mercado, negociação e proteção de escopo.
---

# PROPOSALS — Skill de Propostas Comerciais

## FLUXO OBRIGATÓRIO — SALVAMENTO NO BANCO

**Toda proposta criada DEVE ser salva no banco de dados Supabase.**

Ao finalizar uma proposta, SEMPRE execute:

1. Inserir registro na tabela `proposals`
2. Atualizar o `stage` do cliente para `'PROPOSTA'` na tabela `clients`

Isso garante rastreabilidade completa do pipeline comercial.

---

## 1. OBJETIVO

Criar propostas comerciais que aumentem a percepção de valor da solução antes de apresentar o investimento.

A proposta não deve funcionar como uma tabela de preços.

Ela deve construir a lógica:

PROBLEMA
→ IMPACTO
→ OPORTUNIDADE
→ SOLUÇÃO
→ MECANISMO
→ ENTREGAS
→ VALOR
→ INVESTIMENTO
→ PRÓXIMO PASSO

O objetivo é ajudar o cliente a compreender por que a solução é necessária e por que o investimento é justificável.

---

# 2. REGRA PRINCIPAL

Nunca criar uma proposta baseada apenas em:

- nome do serviço;
- quantidade de entregas;
- horas de trabalho;
- preço informado pelo usuário.

Antes de definir a proposta, entender:

- quem é o cliente;
- qual é o negócio;
- qual problema está tentando resolver;
- qual objetivo possui;
- qual oportunidade existe;
- qual solução é adequada;
- qual escopo é necessário;
- quais riscos existem;
- qual nível de complexidade existe.

Quando informações essenciais estiverem ausentes, fazer perguntas antes de gerar a proposta.

---

# 3. POSICIONAMENTO

A proposta deve posicionar a agência como especialista em aquisição e conversão.

Evitar posicionamento de:

"freelancer que executa tarefas."

Priorizar:

"especialista que estrutura soluções para aquisição, conversão e crescimento."

Os serviços devem ser apresentados como meios para alcançar o objetivo do cliente.

Exemplo:

Não escrever simplesmente:

> Criação de Landing Page.

Preferir:

> Desenvolvimento de uma Landing Page estruturada para transformar tráfego qualificado em oportunidades comerciais.

---

# 4. CRO

Aplicar princípios de CRO à própria proposta.

A proposta deve:

- reduzir incerteza;
- tornar o problema evidente;
- mostrar o impacto do problema;
- apresentar uma solução clara;
- reduzir objeções;
- demonstrar lógica;
- aumentar percepção de valor;
- facilitar a decisão;
- apresentar CTA claro.

Evitar excesso de texto sem função comercial.

Cada seção deve responder a uma pergunta do cliente.

---

# 5. ESTRUTURA PADRÃO

Quando apropriado, utilizar:

## 1. Contexto

Mostrar que a agência compreendeu o negócio.

## 2. Diagnóstico

Explicar o problema ou oportunidade identificada.

## 3. Impacto

Mostrar por que o problema importa.

## 4. Oportunidade

Explicar o que pode ser melhorado.

## 5. Solução proposta

Apresentar a solução de forma estratégica.

## 6. Como funciona

Explicar o mecanismo e as etapas.

## 7. Entregas

Detalhar o que será efetivamente realizado.

## 8. Diferenciais

Mostrar por que a solução possui valor.

## 9. Investimento

Apresentar o preço somente depois de estabelecer valor.

## 10. Condições

Informar pagamento, prazo e demais condições.

## 11. O que não está incluído

Proteger o escopo.

## 12. Próximos passos

Indicar claramente o caminho para contratação.

---

# 6. INVESTIMENTO

A Skill de Propostas não deve inventar preços.

Quando houver uma Skill de Pricing disponível:

- consultar o Pricing;
- utilizar benchmark de mercado;
- considerar complexidade;
- considerar escopo;
- considerar responsabilidade;
- considerar prazo;
- considerar risco;
- considerar personalização;
- considerar recorrência;
- considerar posicionamento.

A antiga tabela interna de preços da agência NÃO deve ser tratada como fonte obrigatória de preço.

O objetivo é evitar subprecificação causada por decisões emocionais.

Quando houver dúvida sobre preço:

apresentar:

- benchmark/faixa de mercado;
- preço recomendado;
- justificativa;
- riscos de cobrar abaixo;
- alternativas de escopo.

---

# 7. REGRA CONTRA SUBPRECIFICAÇÃO

Nunca recomendar preço abaixo do benchmark apenas porque:

- o usuário está precisando de dinheiro;
- o cliente reclamou;
- o usuário está inseguro;
- o usuário quer fechar rapidamente;
- existe medo de perder o cliente.

Situação financeira ou ansiedade do usuário não deve determinar automaticamente o preço de mercado.

Se o preço pretendido estiver significativamente abaixo do benchmark, alertar:

> "Esse valor parece estar abaixo da referência de mercado para este escopo. Antes de apresentar ao cliente, recomendo revisar o posicionamento ou reduzir o escopo."

---

# 8. DESCONTO

Nunca aplicar desconto automaticamente.

Se o cliente solicitar desconto:

1. identificar a objeção;
2. verificar se é realmente preço;
3. avaliar percepção de valor;
4. avaliar orçamento;
5. avaliar escopo;
6. avaliar prazo;
7. considerar contrapartidas.

Quando houver desconto, sempre que possível trocar por:

- redução de escopo;
- pagamento antecipado;
- contrato mais longo;
- menor frequência;
- menor quantidade de entregas;
- fechamento de pacote.

Nunca reduzir preço mantendo exatamente o mesmo escopo sem justificar o impacto.

---

# 9. PROTEÇÃO DE ESCOPO

Toda proposta deve deixar claro:

- o que está incluído;
- o que não está incluído;
- quantidade de entregas;
- quantidade de revisões quando aplicável;
- prazo;
- responsabilidades do cliente;
- dependências;
- integrações;
- manutenção;
- serviços recorrentes.

Não utilizar expressões vagas como:

> "ajustes necessários"

sem definir o limite quando isso puder gerar conflito de escopo.

---

# 10. RESULTADOS

Nunca prometer resultados garantidos.

Evitar:

> "Vamos gerar 100 leads."

Preferir:

> "A estratégia será estruturada para aumentar a capacidade de geração e conversão de oportunidades qualificadas."

Separar:

- entregáveis;
- objetivos;
- hipóteses;
- resultados esperados;
- fatores externos.

---

# 11. GOOGLE ADS

Quando a proposta envolver Google Ads, diferenciar claramente:

HONORÁRIOS DA AGÊNCIA

e

VERBA DE MÍDIA.

Exemplo:

> Gestão Google Ads: R$ X/mês
>
> Investimento recomendado em mídia: R$ Y/mês

A verba de mídia não deve ser apresentada como receita da agência.

---

# 12. PROJETOS + RECORRÊNCIA

Quando existir implantação e gestão:

separar:

### Implantação

O trabalho inicial necessário para colocar a estrutura em funcionamento.

### Gestão

O trabalho recorrente de acompanhamento e otimização.

Nunca esconder implantação dentro de uma mensalidade sem explicar a estrutura.

---

# 13. PACOTES

Quando fizer sentido, avaliar se uma combinação de serviços cria uma solução de maior valor.

Exemplo:

Landing Page
+
Tracking
+
Google Ads
+
CRO

Pode ser apresentada como:

> Sistema de Aquisição de Leads.

O pacote deve ser vendido como solução integrada, não simplesmente como soma de serviços.

---

# 14. OBJEÇÕES

Antes de finalizar uma proposta, procurar antecipar objeções relacionadas a:

- preço;
- prazo;
- risco;
- confiança;
- necessidade;
- comparação com concorrentes;
- complexidade;
- manutenção;
- resultados.

Responder objeções através da própria estrutura da proposta quando possível.

Não criar uma seção artificial de "objeções" se isso prejudicar a fluidez comercial.

---

# 15. NEGOCIAÇÃO

Quando a Skill de Negotiation estiver disponível, utilizar seus princípios para:

- identificar possíveis objeções;
- estruturar concessões;
- evitar descontos prematuros;
- formular alternativas;
- preparar a apresentação do preço;
- preservar margem.

A proposta deve facilitar uma negociação saudável.

Não utilizar manipulação ou pressão artificial.

---

# 16. CONTRATO

Quando a Skill de Contracts estiver disponível:

- não prometer na proposta algo incompatível com o contrato;
- manter coerência entre escopo e obrigações;
- indicar condições de pagamento;
- indicar necessidade de entrada quando aplicável;
- deixar claro que o início do trabalho depende do pagamento da entrada definida;
- evitar obrigações abertas ou ilimitadas.

A proposta comercial não substitui o contrato.

---

# 17. APRESENTAÇÃO DO PREÇO

Não apresentar o preço no início da proposta.

Primeiro estabelecer:

1. contexto;
2. problema;
3. impacto;
4. oportunidade;
5. solução;
6. escopo;
7. valor gerado pela solução.

Somente então apresentar:

> Investimento

O preço deve aparecer como consequência lógica da solução apresentada.

---

# 18. COMPARAÇÃO DE PLANOS

Quando houver múltiplas opções, pode utilizar:

### Essencial
Resolve o problema principal.

### Estratégico
Solução recomendada.

### Completo
Maior abrangência e profundidade.

A opção recomendada deve ser claramente identificada quando houver justificativa.

Não criar opções artificiais apenas para manipular a escolha.

---

# 19. TOM

Utilizar linguagem:

- profissional;
- clara;
- consultiva;
- objetiva;
- segura;
- sem exageros;
- sem promessas irreais.

Evitar:

- linguagem agressiva;
- urgência artificial;
- escassez falsa;
- superlativos sem prova;
- promessas garantidas.

---

# 20. CHECKLIST FINAL

Antes de entregar uma proposta, verificar:

[ ] O problema do cliente está claro?

[ ] A oportunidade está clara?

[ ] A solução responde ao problema?

[ ] O valor foi estabelecido antes do preço?

[ ] O escopo está claro?

[ ] O que não está incluído está claro?

[ ] Implantação e recorrência estão separadas?

[ ] Verba de mídia e honorários estão separados?

[ ] O preço foi baseado em referência adequada?

[ ] Não houve subprecificação emocional?

[ ] Não foi aplicado desconto automaticamente?

[ ] Não existem promessas de resultado garantido?

[ ] As condições de pagamento estão claras?

[ ] Os próximos passos estão claros?

[ ] A proposta é coerente com o futuro contrato?

---

# 21. REGRA FINAL

A função desta Skill não é ajudar a agência a "cobrar qualquer preço".

Sua função é ajudar a agência a:

CLIENTE CERTO
+
PROBLEMA CERTO
+
SOLUÇÃO CERTA
+
ESCOPO CERTO
+
VALOR PERCEBIDO
+
PREÇO JUSTIFICÁVEL
=
PROPOSTA COMERCIAL FORTE.

Se o preço parecer baixo demais, sinalizar.

Se o escopo parecer grande demais para o preço, sinalizar.

Se a solução não justificar o investimento, sinalizar.

Se faltarem informações importantes, perguntar.

Nunca sacrificar margem apenas para aumentar a chance de fechamento.

---

# 22. INTEGRAÇÃO COM BANCO DE DADOS — OBRIGATÓRIO

## ⚠️ FLUXO OBRIGATÓRIO

**Ao criar qualquer proposta, você DEVE:**

1. Criar registro na tabela `proposals`
2. Atualizar o `stage` do cliente para `'PROPOSTA'`

**NÃO** finalize uma proposta sem salvar no banco.

### Criar registro de proposta

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  INSERT INTO proposals (
    client_id, title, services,
    total_value, monthly_value, status
  ) VALUES (
    (SELECT id FROM clients WHERE slug = 'slug'),
    'Proposta - Google Ads + Landing Page',
    '[{\"servico\": \"Google Ads\", \"valor\": 2500}, {\"servico\": \"Landing Page\", \"valor\": 1000}]'::jsonb,
    3500.00,
    2500.00,
    'RASCUNHO'
  );
"
```

### Atualizar status da proposta

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  UPDATE proposals 
  SET status = 'ENVIADA', sent_at = NOW()
  WHERE id = 'id-da-proposta';
"
```

### Registrar aprovação

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  UPDATE proposals 
  SET status = 'APROVADA', approved_at = NOW()
  WHERE id = 'id-da-proposta';
"
```

### Consultar propostas de um cliente

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  SELECT title, total_value, monthly_value, status, sent_at, approved_at
  FROM proposals
  WHERE client_id = (SELECT id FROM clients WHERE slug = 'slug')
  ORDER BY created_at DESC;
"
```

## Vincular à Cliente

Sempre vincular a proposta ao cliente correto usando `client_id`.

## Atualizar Pipeline

Quando uma proposta for enviada, atualizar o estágio do cliente:

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  UPDATE clients 
  SET stage = 'AGUARDANDO_DECISAO',
      opportunity_value = 3500.00,
      monthly_value = 2500.00,
      next_followup_date = CURRENT_DATE + INTERVAL '3 days',
      next_followup_note = 'Follow-up pos-envio da proposta'
  WHERE slug = 'slug';
"
```

## Registrar Interação

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  INSERT INTO interactions (client_id, interaction_type, subject, content)
  VALUES (
    (SELECT id FROM clients WHERE slug = 'slug'),
    'PROPOSTA',
    'Proposta enviada - Google Ads + Landing Page',
    'Proposta no valor de R$ 3.500 enviada por e-mail. Escopo: gestao de campanhas, LP, tracking.'
  );
"
```
