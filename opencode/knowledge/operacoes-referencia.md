# Referência Operacional da Agência

> Documento de consulta sob demanda (via RAG). Contém os detalhes operacionais
> removidos do AGENTS.md para reduzir contexto. As REGRAS continuam no AGENTS.md;
> aqui ficam os detalhes de implementação, comandos e tabelas.

---

## RAG — Uso avançado

Infraestrutura: Supabase + pgvector. Embeddings: Google Gemini `gemini-embedding-2` (3072 dims).
Tabela: `embeddings` no Supabase.

### Busca básica

```bash
python3 ~/.config/opencode/scripts/rag-search.py "sua consulta" --limit 5
```

### Filtros disponíveis

```bash
# Por tipo de conteúdo
python3 ~/.config/opencode/scripts/rag-search.py "preço" --type skill

# Por skill específica
python3 ~/.config/opencode/scripts/rag-search.py "Google Ads" --skill pricing

# Por cliente
python3 ~/.config/opencode/scripts/rag-search.py "acupuntura" --client valda-acupuntura

# Saída JSON para processamento
python3 ~/.config/opencode/scripts/rag-search.py "consulta" --json
```

### Quando consultar o RAG

Sempre antes de responder sobre:
1. Preços e precificação de serviços
2. Políticas de Google Ads
3. Processos da agência
4. Dados de clientes específicos
5. Metodologias de trabalho
6. Contratos e propostas
7. Estratégias de SEO/CRO
8. Negociação e objeções comerciais

### Regras de uso

1. NUNCA inventar informações que podem ser encontradas no RAG
2. SEMPRE consultar RAG antes de dar recomendações sobre preços, processos ou políticas
3. Citar fonte: "De acordo com [skill/pricing]..."
4. RAG complementa análise, não substitui
5. Atualizar base quando novos arquivos forem criados

### Atualização da base

```bash
python3 ~/.config/opencode/scripts/rag-ingest.py
```

Bases vetorizadas: skills em `~/.config/opencode/skills`, clientes em
`~/.config/opencode/clients`, agents em `~/.config/opencode/agents`,
company profile, AGENCY-KNOWLEDGE.md e esta pasta `knowledge/`.

---

## CLIENT ADD — Cadastro rápido de clientes

Script: `~/.config/opencode/scripts/client-add.py`
Cria registro no Supabase (`clients` + `interactions`) e markdown em `~/.config/opencode/clients/` em 1 chamada.

### Exemplo completo

```bash
python3 ~/.config/opencode/scripts/client-add.py \
  --name "Silvia Drobiarz" \
  --slug "silvia-humanoterapia" \
  --segment "Terapia Holistica" \
  --website "https://silvia-humanoterapia.com/" \
  --location "Miami, FL" \
  --phone "+1 (305) 322-3889" \
  --email "love@silvia-humanoterapia.com" \
  --contact "Nome do Contato" \
  --role "Cargo" \
  --services "Humanoterapia,Psicanalise,Radiestesia" \
  --origin "Origem do lead" \
  --priority "ALTA" \
  --note "Nota adicional" \
  --json
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `--name` | sim | Nome da empresa/cliente |
| `--slug` | sim | Slug único (sem espaços) |
| `--segment` | não | Segmento de atuação |
| `--website` | não | URL do site |
| `--location` | não | Localização |
| `--phone` | não | Telefone/WhatsApp |
| `--email` | não | Email |
| `--contact` | não | Nome do contato |
| `--role` | não | Cargo do contato |
| `--services` | não | Serviços (separados por vírgula) |
| `--origin` | não | Origem do lead |
| `--priority` | não | ALTA/MEDIA/BAIXA (default: MEDIA) |
| `--note` | não | Nota adicional |
| `--no-markdown` | não | Não criar arquivo markdown |
| `--json` | não | Saída em JSON |

### Regras

1. Sempre usar slug único — verificar duplicidade antes
2. Não inventar dados — preencher apenas o fornecido
3. Priorizar agilidade — usar este script em vez de tool calls manuais
4. Usar `--json` para processamento automatizado

---

## LP-TEMPLATES — Regra completa

ANTES de gerar uma landing page, consultar o RAG para templates aprovados:

```bash
python3 ~/.config/opencode/scripts/rag-search.py "landing page [nicho ou tema]" --skill lp-templates --limit 3
```

Se encontrar template relevante: reutilizar estrutura e blocos de copy, adaptar ao contexto,
manter padrão de qualidade do template. Se não encontrar, criar do zero usando as metodologias
das skills.

Atalho: sempre usar o agente `landing-page-creator` quando a tarefa for criar landing page.

---

## Fluxo comercial completo da agência

DIAGNÓSTICO → PRECIFICAÇÃO → PROPOSTA → NEGOCIAÇÃO → APROVAÇÃO → CONTRATO →
ENTRADA/PAGAMENTO → EXECUÇÃO → ENTREGA → RECORRÊNCIA → EXPANSÃO

Cada etapa tem sua própria lógica. Não misturar preço, proposta, negociação,
contrato e execução.

### Combinações de skills

- Proposta: `proposals → pricing → CRO` (+ `negotiation` se houver risco/objeção; + `contracts` se definir condições contratuais)
- Negociação de preço: `negotiation → pricing` (se mudar escopo: `+ proposals`)
- Contratação: `contracts → proposals` (verificar coerência contrato ↔ oferta aprovada)
- Pacote de serviços: `pricing → proposals → negotiation`
- Serviço novo: `pricing → proposals` (avaliar benchmark e complexidade antes de definir preço)

---

## Pricing Engine — processo detalhado

### Processo obrigatório de precificação

1. Identificar exatamente o serviço
2. Entender o escopo
3. Identificar nível de complexidade
4. Identificar nível de personalização
5. Identificar perfil provável do cliente
6. Pesquisar benchmarks atuais quando necessário
7. Comparar serviços equivalentes
8. Desconsiderar referências claramente inferiores ao nível de entrega
9. Identificar faixa de mercado comparável
10. Posicionar o serviço dentro da faixa
11. Recomendar um preço
12. Explicar a justificativa

Não usar simplesmente a média de todos os preços encontrados.

### Comparabilidade — NÃO usar como benchmark principal

- templates baratos; páginas DIY; freelancers de entrada
- ofertas extremamente simplificadas
- serviços sem estratégia, sem copy, sem desenvolvimento personalizado
- ofertas com escopo claramente inferior

### Estrutura da recomendação

- **Benchmark de mercado:** faixa encontrada para serviços comparáveis
- **Posicionamento recomendado:** onde a agência deveria estar na faixa
- **Preço recomendado:** valor sugerido
- **Faixa aceitável:** faixa de negociação sem comprometer posicionamento
- **Preço abaixo do mercado:** sinalizar explicitamente quando aplicável
- **Justificativa:** o que justifica o posicionamento

### Mercado não é preço obrigatório

O preço final pode sair da faixa quando houver justificativa: maior complexidade,
responsabilidade, urgência, personalização, potencial econômico para o cliente,
risco, recorrência, pacote, escopo reduzido, cliente estratégico. Sempre explicar.

### Orçamentos e propostas — checklist

1. Não aplicar automaticamente preços históricos
2. Avaliar escopo
3. Benchmark atual como referência
4. Separar implantação de recorrência
5. Separar honorários de verba de mídia
6. Não inventar descontos
7. Não prometer resultados garantidos
8. Identificar oportunidades de pacote
9. Justificar valores acima/abaixo do benchmark
10. Evitar reduzir preço sem reduzir escopo ou obter contrapartida

---

## Proteção contra decisões emocionais — protocolo

Quando o usuário demonstrar insegurança, ansiedade ou urgência financeira em
decisão comercial, separar:

- **Fato:** o que sabemos sobre mercado, escopo e cliente
- **Hipótese:** o que acreditamos que pode acontecer
- **Estratégia:** qual decisão tem melhor relação valor/risco/margem

Não validar redução de preço automaticamente. Se o usuário sugerir valor
significativamente abaixo do benchmark, informar: quanto está abaixo,
qual seria o preço recomendado, e a consequência provável de posicionar
muito abaixo do mercado. A decisão final é do usuário, mas deve ser
tratada como decisão deliberada de posicionamento.

---

## Hierarquia de decisão

Quando houver conflito entre informações:

1. Dados atuais e verificáveis
2. Benchmark de mercado atualizado
3. Knowledge Base validada
4. Skills especializadas
5. Dados históricos da agência
6. Inferência (sempre identificada como inferência)

Dados históricos nunca substituem informação atual de mercado quando a
tarefa exige preço de mercado.
