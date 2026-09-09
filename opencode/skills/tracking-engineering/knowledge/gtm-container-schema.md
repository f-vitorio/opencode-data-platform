# GTM CONTAINER — SCHEMA E REGRAS DE IMPORTAÇÃO

> Aprendizado prático da configuração do container GTM para a FVS7 (set/2026).
> Este arquivo é a fonte das regras para GERAR e IMPORTAR o JSON do container.
> A documentação oficial atual decide; estes são os pontos verificados na prática.

## Objetivo

Permitir **gerar e importar** o container GTM de forma confiável para qualquer
site/cliente, sem bater contra erros de schema.

---

## 1. ENUMS — FORMATO ATUAL (2026)

O GTM migrou os enums do container para **UPPERCASE**. Valores antigos
(lowercase) são rejeitados na importação.

| Enum | Campo | Formato atual | Valor antigo (rejeitado) |
|------|-------|---------------|---------------------------|
| ParameterType | `parameter[].type` | `TEMPLATE`, `MAP`, `BOOLEAN`, `INTEGER`, `LIST` | `template`, `map`, ... |
| EventType | `trigger[].type` | `CUSTOM_EVENT`, `PAGEVIEW`, ... | `customEvent`, `pageview` |
| ConditionType | `customEventFilter[].type` | `EQUALS`, ... | `equals` |
| TagType | `tag[].type` | `googtag`, `gaawe`, `awct` (lowercase) | — (não muda) |
| VariableType | `variable[].type` | `v`, `c`, `d` (lowercase) | — (não muda) |
| BuiltInVariableType | `builtInVariable[].type` | `PAGE_URL`, `EVENT`, `PAGE_PATH`, ... | — (não muda) |

**Atenção:** TagType e VariableType permanecem lowercase; ParameterType,
EventType e ConditionType são UPPERCASE.

---

## 2. ERROS CONHECIDOS E CAUSAS

| Erro | Causa | Solução |
|------|-------|---------|
| `Unrecognized value [template]` | `parameter[].type` lowercase | usar `TEMPLATE` |
| `Unrecognized value [customEvent]` | `trigger[].type` lowercase | usar `CUSTOM_EVENT` |
| `O valor precisa ser uma tabela` | parâmetro `MAP`/`LIST` (`eventParameters`, `userProperties`) com estrutura não aceita | **evitar** MAP no JSON de import; adicionar parâmetros/Enhanced na UI |
| `formato inválido` na tag de conversão Ads | `conversionId` com placeholder `<...>` | não usar `< >`; exigir label real, ou remover a tag e importar conversão direto no Google Ads |

---

## 3. REGRA DE OURO: JSON DE IMPORTAÇÃO MÍNIMO

Para **garantir** que o import sempre passe:

1. **Somente GA4** no container de import (config + tags de evento). **Sem**
   Google Ads (conversão/remarketing) — a conversão do Ads é importada direto
   no Google Ads lendo o evento do GA4 linkado.
2. **Sem `eventParameters`/`userProperties` (MAP)** nas tags GA4 Event.
   Usar apenas `eventName` + `measurementIdOverride`. Parâmetros customizados
   e Enhanced Conversions são adicionados na **UI do GTM** (sem risco de schema).
3. **Google Tag (googtag) com `sendPageView: false`**. O `page_view` é enviado
   por uma tag GA4 Event (gaawe) com o trigger `CUSTOM_EVENT page_view`, o que
   evita `page_view` duplicado.
4. **IDs reais** (nunca placeholder): `tagId` (G-), `measurementIdOverride` (G-).
5. **`exportFormatVersion: 2`** com `containerVersion` contendo
   `container`, `builtInVariable`, `variable`, `trigger`, `tag`.

---

## 4. ESTRUTURA DE UMA TAG GA4 EVENT MÍNIMA

```json
{
  "accountId": "6335101254",
  "containerId": "241254853",
  "tagId": "2",
  "name": "GA4 - Event - form_submit_whatsapp",
  "type": "gaawe",
  "parameter": [
    { "type": "TEMPLATE", "key": "eventName", "value": "form_submit_whatsapp" },
    { "type": "TEMPLATE", "key": "measurementIdOverride", "value": "G-XDVNT4HQ2W" }
  ],
  "firingTriggerId": ["1"]
}
```

## 5. ESTRUTURA DE UM TRIGGER CUSTOM EVENT

```json
{
  "accountId": "6335101254",
  "containerId": "241254853",
  "triggerId": "1",
  "name": "CE - form_submit_whatsapp",
  "type": "CUSTOM_EVENT",
  "customEventFilter": [
    {
      "type": "EQUALS",
      "parameter": [
        { "type": "TEMPLATE", "key": "arg0", "value": "{{_event}}" },
        { "type": "TEMPLATE", "key": "arg1", "value": "form_submit_whatsapp" }
      ]
    }
  ]
}
```

---

## 6. VALIDAÇÃO ANTES DE ENTREGAR

Sempre rodar antes de enviar ao cliente:

- `scripts/test <arquivo>` — valida sintaxe JSON.
- Conferir que NÃO há `parameter[].type` lowercase, `MAP`/`LIST`, nem
  placeholder `< >`.
- Conferir enums: `TEMPLATE/BOOLEAN/INTEGER`, `CUSTOM_EVENT/PAGEVIEW`, `EQUALS`.

---

## 7. PRODUÇÃO DO JSON

Usar `scripts/generate-gtm-container.cjs` + `scripts/configs/<cliente>.json`
(ver `procedures/import-gtm-container.md`). Nunca gerar manualmente para cada
cliente — é o mesmo fluxo, só mudam os IDs e o nome.