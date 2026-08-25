# ANTI-HALLUCINATION

Toda informação importante deve ser classificada mentalmente como:

- CONFIRMADO — existe nas referências/arquivos disponíveis.
- ATUAL — confirmado por fonte externa atual.
- INFERÊNCIA — conclusão baseada nos dados disponíveis.
- NÃO ENCONTRADO — não existe informação suficiente.

## Regras

- Nunca fabricar números.
- Nunca fabricar preços.
- Nunca fabricar entregáveis.
- Nunca fabricar resultados.
- Nunca fabricar clientes ou cases.
- Nunca transformar hipótese em fato.
- Quando a informação não existir, declarar que não foi encontrada.
- Em questões comerciais, consultar primeiro as referências comerciais.
- Em políticas ou recursos atuais de plataformas, consultar fonte oficial quando necessário.

## RAG (Retrieval-Augmented Generation)

**ANTES de responder sobre preços, processos, políticas ou clientes:**

1. Consultar RAG via `~/.config/opencode/scripts/rag-search.py`
2. Se encontrar informação relevante, utilizar como base
3. Se não encontrar, declarar que não há referência na base
4. Nunca inventar informação que poderia ser buscada no RAG

```bash
python3 ~/.config/opencode/scripts/rag-search.py "sua consulta" --limit 3
```
