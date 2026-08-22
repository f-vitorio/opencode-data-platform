---
name: contracts
description: Geração e revisão de contratos comerciais da agência, com coleta estruturada de dados do contratante, escopo, valores, entrada, pagamentos, responsabilidades e condições contratuais.
---

# CONTRACTS — Skill de Contratos

## 1. OBJETIVO

Esta Skill é responsável por criar, revisar e estruturar contratos comerciais para a agência.

O contrato deve transformar a proposta comercial e as condições negociadas em um documento claro, coerente e juridicamente organizado.

Não tratar contrato como simples documento administrativo.

O contrato deve proteger:

- escopo;
- prazo;
- pagamento;
- margem;
- responsabilidades;
- propriedade intelectual;
- confidencialidade;
- cancelamento;
- limites de responsabilidade;
- condições de início;
- condições de entrega;
- relacionamento comercial.

---

# 2. REGRA DE INÍCIO DO TRABALHO

Por padrão, o contrato deve estabelecer explicitamente que:

> O início da execução dos serviços fica condicionado ao pagamento da entrada/sinal acordado entre as partes.

A Skill DEVE perguntar ao usuário:

> Qual percentual ou valor da entrada você deseja estabelecer para este contrato?

Não assumir automaticamente 50%.

O usuário pode definir:

- percentual;
- valor fixo;
- pagamento integral;
- parcelamento;
- outra condição comercial.

Se a entrada não tiver sido definida, NÃO inventar.

Informar que a condição precisa ser definida antes da versão final do contrato.

---

# 3. DADOS DA CONTRATADA

Utilizar os dados empresariais disponíveis no Company Profile da agência.

Não pedir novamente informações que já estejam disponíveis em uma fonte interna confiável.

Se algum dado obrigatório estiver ausente, solicitar somente o dado ausente.

Não inventar:

- CNPJ;
- endereço;
- representante;
- CPF;
- e-mail;
- telefone;
- dados bancários.

---

# 4. DADOS DO CONTRATANTE

Antes de gerar a versão final, coletar os dados necessários do contratante.

Para pessoa jurídica:

- razão social;
- nome fantasia, quando aplicável;
- CNPJ;
- endereço completo;
- cidade/UF;
- CEP;
- e-mail;
- telefone;
- nome do representante legal;
- CPF do representante;
- cargo/função.

Para pessoa física:

- nome completo;
- CPF;
- endereço;
- cidade/UF;
- CEP;
- e-mail;
- telefone.

Não inventar dados ausentes.

---

# 5. DADOS COMERCIAIS

Antes da versão final, confirmar:

- serviço contratado;
- descrição do serviço;
- escopo;
- entregáveis;
- prazo;
- valor total;
- forma de pagamento;
- entrada/sinal;
- número de parcelas;
- datas de pagamento;
- recorrência, quando aplicável;
- condições de reajuste, quando aplicável;
- condições de início;
- condições de entrega.

Se houver uma proposta aprovada, utilizar a proposta como fonte principal para os dados comerciais.

Não alterar valores ou condições negociadas sem autorização.

---

# 6. PIX

A forma de pagamento preferencial da agência é PIX.

Quando o contrato utilizar PIX, apresentar os dados disponíveis no Company Profile ou configuração comercial segura da agência.

Nunca inventar:

- chave PIX;
- banco;
- favorecido.

Se o dado não estiver disponível na fonte interna, solicitar ao usuário.

---

# 7. ESCOPO

O contrato deve diferenciar claramente:

### Incluído

Tudo que faz parte da contratação.

### Não incluído

Tudo que não faz parte do escopo.

### Serviços adicionais

Qualquer trabalho fora do escopo deve ser tratado separadamente e poderá exigir novo orçamento ou aditivo contratual.

Evitar expressões vagas como:

> "conforme necessidade"

quando isso puder gerar dúvida sobre o escopo.

---

# 8. PRAZOS

Definir claramente:

- data de início;
- prazo de execução;
- prazo de entrega;
- prazo de aprovação;
- dependências do cliente.

Quando o cliente atrasar o fornecimento de informações, materiais, acessos ou aprovações necessários, o cronograma poderá ser ajustado proporcionalmente.

Não prometer prazo que não tenha sido definido.

---

# 9. PAGAMENTO

O contrato deve separar claramente:

**Honorários da agência**

de:

**Investimentos de terceiros.**

Exemplo:

Google Ads:

> Honorários de gestão: valor contratado.

> Verba de mídia: responsabilidade do cliente.

A verba destinada às plataformas não deve ser tratada como receita da agência.

---

# 10. ATRASO DE PAGAMENTO

Prever condições para atraso de pagamento de acordo com a legislação aplicável.

Não inventar percentuais ou penalidades quando o usuário não tiver definido uma política.

Quando necessário, apresentar opções para o usuário decidir antes da versão final.

---

# 11. RECORRÊNCIA

Para serviços recorrentes, definir:

- periodicidade;
- valor;
- vencimento;
- prazo contratual;
- renovação;
- reajuste, quando aplicável;
- condições de cancelamento.

Diferenciar claramente:

**implantação/setup**

de

**gestão recorrente**.

---

# 12. CANCELAMENTO E RESCISÃO

O contrato deve estabelecer condições claras para:

- cancelamento;
- rescisão;
- aviso prévio;
- valores pendentes;
- serviços já executados;
- entregáveis em andamento;
- acesso a contas e materiais.

Não criar penalidades abusivas ou sem fundamento.

Quando houver dúvida jurídica relevante, sinalizar que a cláusula precisa de validação profissional.

---

# 13. PROPRIEDADE INTELECTUAL

Definir, quando aplicável:

- materiais produzidos;
- código;
- textos;
- imagens;
- criativos;
- contas;
- arquivos editáveis;
- licenças de terceiros;
- ferramentas;
- templates;
- componentes reutilizáveis.

Diferenciar:

**material criado especificamente para o cliente**

de

**recursos, frameworks, templates, bibliotecas ou conhecimentos preexistentes da agência.**

---

# 14. CONFIDENCIALIDADE

Quando apropriado, incluir cláusula de confidencialidade cobrindo informações comerciais, estratégicas, técnicas e dados recebidos durante a prestação dos serviços.

Não criar obrigações excessivamente amplas sem necessidade.

---

# 15. LGPD

Quando houver tratamento de dados pessoais, considerar cláusulas relacionadas à proteção de dados e responsabilidades das partes.

Não afirmar conformidade jurídica absoluta apenas pela inclusão de uma cláusula.

Se a operação envolver tratamento relevante de dados pessoais, sinalizar a necessidade de validação jurídica.

---

# 16. RESPONSABILIDADES DO CLIENTE

Definir responsabilidades relacionadas a:

- fornecimento de informações;
- acessos;
- aprovação de materiais;
- pagamentos;
- veracidade das informações;
- autorização de uso de materiais;
- atendimento de leads, quando aplicável;
- cumprimento de prazos de aprovação.

A agência não deve assumir responsabilidade por fatores que estejam sob controle do cliente ou de terceiros.

---

# 17. RESULTADOS

Nunca prometer resultados garantidos.

Especialmente em:

- Google Ads;
- SEO;
- CRO;
- geração de leads;
- vendas;
- posicionamento orgânico;
- campanhas de mídia.

O contrato deve diferenciar:

**prestação de serviço**

de

**resultado econômico do cliente**.

---

# 18. CONTRATOS DERIVADOS DE PROPOSTAS

Quando existir uma proposta aprovada:

1. consultar a proposta;
2. identificar serviços;
3. identificar escopo;
4. identificar valores;
5. identificar condições negociadas;
6. identificar prazo;
7. identificar condições especiais;
8. transformar essas informações em contrato.

Não contradizer a proposta aprovada.

Se houver divergência entre proposta e informação fornecida posteriormente pelo usuário, apontar a divergência antes de gerar o contrato final.

---

# 19. INTEGRAÇÃO COM OUTRAS SKILLS

Esta Skill pode ser acionada por:

- proposals;
- negotiation;
- client-management;
- pricing.

### Proposals

Pode solicitar a geração de contrato depois da aprovação de uma proposta.

### Negotiation

Pode fornecer as condições comerciais finais negociadas.

### Client-management

Pode fornecer os dados do contratante e histórico da negociação.

### Pricing

Pode fornecer referência de preço, mas NÃO deve alterar automaticamente o valor já negociado.

---

# 20. ORDEM DE CONFIANÇA DOS DADOS

Para dados contratuais:

1. contrato/condições explicitamente aprovadas pelo usuário;
2. proposta aprovada;
3. dados internos da agência;
4. histórico comercial;
5. fontes externas;
6. inferência.

Nunca usar inferência para preencher:

- valores;
- dados pessoais;
- dados bancários;
- CNPJ;
- CPF;
- prazos;
- percentuais;
- obrigações contratuais.

---

# 21. VALIDAÇÃO JURÍDICA

Cláusulas jurídicas podem ser pesquisadas e comparadas com fontes públicas confiáveis.

Porém:

- pesquisa na internet não equivale a aconselhamento jurídico;
- não apresentar cláusula como juridicamente válida em qualquer situação;
- verificar legislação aplicável quando necessário;
- sinalizar cláusulas de maior risco;
- recomendar revisão por advogado quando a complexidade justificar.

Separar:

FACT
CLAUSE
LEGAL INTERPRETATION
RECOMMENDATION

---

# 22. ESTRUTURA PADRÃO

Quando apropriado, utilizar:

1. Identificação das partes
2. Objeto
3. Escopo dos serviços
4. Obrigações da contratada
5. Obrigações do contratante
6. Prazo
7. Investimento e pagamento
8. Condição de início mediante pagamento da entrada
9. Serviços adicionais
10. Propriedade intelectual
11. Confidencialidade
12. Proteção de dados
13. Limitação de responsabilidade
14. Rescisão
15. Disposições gerais
16. Foro
17. Assinaturas

A estrutura pode ser adaptada ao tipo de serviço.

---

# 23. CHECKLIST ANTES DA VERSÃO FINAL

Verificar:

- [ ] dados da contratada;
- [ ] dados do contratante;
- [ ] serviço;
- [ ] escopo;
- [ ] entregáveis;
- [ ] prazo;
- [ ] valor;
- [ ] entrada;
- [ ] parcelas;
- [ ] vencimentos;
- [ ] forma de pagamento;
- [ ] condição de início;
- [ ] serviços adicionais;
- [ ] responsabilidades;
- [ ] cancelamento;
- [ ] propriedade intelectual;
- [ ] confidencialidade;
- [ ] LGPD, quando aplicável;
- [ ] ausência de promessa de resultado;
- [ ] coerência com a proposta aprovada.

Se qualquer informação crítica estiver faltando, perguntar antes de considerar o contrato finalizado.

---

# 24. REGRA DE SEGURANÇA

Nunca:

- inventar dados;
- inventar condições comerciais;
- inventar assinaturas;
- inventar cláusulas específicas como se fossem exigências legais;
- alterar valores negociados;
- iniciar trabalho antes da condição de entrada acordada;
- afirmar garantia de resultado;
- expor dados confidenciais desnecessariamente.

---

# 25. COMPORTAMENTO

Quando o usuário disser:

> "Crie um contrato para esse cliente."

Primeiro verificar quais informações já estão disponíveis.

Não fazer perguntas que já possam ser respondidas pelas fontes internas.

Depois identificar apenas as lacunas necessárias.

Quando tudo estiver disponível:

1. apresentar um resumo das condições;
2. destacar a entrada/sinal;
3. confirmar eventuais pontos críticos;
4. gerar o contrato.

---

# 26. PRINCÍPIO FINAL

O contrato deve proteger a relação comercial sem tornar o documento desnecessariamente complexo.

Priorizar:

**clareza → escopo → pagamento → responsabilidades → proteção → execução.**

O contrato deve refletir a negociação real.

Não utilizar o contrato para criar condições que não foram discutidas sem informar claramente o usuário.

---

# 27. INTEGRAÇÃO COM BANCO DE DADOS

## Registrar Contrato

Todo contrato deve ser registrado na tabela `contracts` do Supabase.

### Criar registro

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  INSERT INTO contracts (
    client_id, title, contract_value,
    monthly_value, entry_value, payment_method, payment_terms,
    start_date, status
  ) VALUES (
    (SELECT id FROM clients WHERE slug = 'slug'),
    'Contrato - Gestao Google Ads',
    7000.00,
    2500.00,
    3500.00,
    'PIX',
    'Entrada 50% + 1 parcela em 30 dias',
    CURRENT_DATE,
    'EM_ANDAMENTO'
  );
"
```

### Atualizar status

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  UPDATE contracts 
  SET status = 'ASSINADO'
  WHERE id = 'id-do-contrato';
"
```

### Consultar contratos de um cliente

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  SELECT title, contract_value, monthly_value, status, start_date
  FROM contracts
  WHERE client_id = (SELECT id FROM clients WHERE slug = 'slug')
  ORDER BY created_at DESC;
"
```

## Atualizar Pipeline

Quando o contrato for assinado, atualizar o estagio do cliente:

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  UPDATE clients 
  SET stage = 'ONBOARDING',
      monthly_value = 3500.00,
      next_followup_date = CURRENT_DATE + INTERVAL '1 day',
      next_followup_note = 'Iniciar onboarding'
  WHERE slug = 'slug';
"
```

## Registrar Interacao

```bash
source ~/.config/opencode/.env
psql "$DATABASE_URL" -c "
  INSERT INTO interactions (client_id, interaction_type, subject, content)
  VALUES (
    (SELECT id FROM clients WHERE slug = 'slug'),
    'CONTRATO',
    'Contrato assinado',
    'Contrato assinado. Valor: R$ 7.000. PIX. Entrada 50%. Duracao: 6 meses.'
  );
"
```
