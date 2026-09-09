# TEMPLATE — GTM CONTAINER (FVS7 STANDARD)

Modelo de container para importação no Google Tag Manager.

## ⚠️ AVISO OBRIGATÓRIO

**O schema do GTM muda.** Os códigos de tipo (`type`, `builtInVariable.type`,
códigos de tag/trigger/variável) usados abaixo são pontos de falha conhecidos
— o erro `Error deserializing enum type [Type]. Unrecognized value [1]`
acontece exatamente quando um valor de enum é inválido/desatualizado.

**ANTES de entregar o JSON para importação:**

1. Validar TODOS os valores de enum contra o schema atual do GTM
   (Tag Manager API v2 — `https://developers.google.com/tag-manager/api/v2`).
2. Substituir os valores placeholder (`GTM-XXXXXXX`, Measurement IDs,
   Conversion IDs, nomes).
3. Validar o JSON estruturalmente (JSON válido, sem comentários).
4. Testar em um container de rascunho antes de publicar.

O arquivo `gtm-container.json` ao lado é um **ponto de partida**, não uma
verdade absoluta. A documentação oficial atual decide.

## Campos a preencher

| Placeholder | Descrição |
|-------------|-----------|
| `GTM-XXXXXXX` | Public ID do container |
| `example.com` | domínio de destino |
| `G-XXXXXXXXXX` | Measurement ID do GA4 |
| `AW-000000000 / <LABEL>` | Conversion ID / Label do Google Ads |
| `FVS7 Template` | nome do container |

## Estrutura incluída

- container (web)
- builtInVariable: Page Path, Event Name, Click URL, Click Text,
  Form ID, Page URL
- variáveis de dataLayer: `event`, `lead_type`, `service`, `page_path`
- triggers: page view (All Pages + History Change), custom events
  (`scroll_90`, `cta_click`, `whatsapp_click`, `phone_click`, `form_start`,
  `form_submit`, `generate_lead`), click, form submission
- tags: Google Tag GA4 config, GA4 event (generate_lead), Google Ads
  conversion (Lead), Conversion Linker

## Validação de enums (o que conferir)

- `tag[].type` e `trigger[].type`: strings do schema (ex.: `gaawec`, `gaawe`,
  `gaawc`, `html`, `linkid`, `customEvent`, `click`, `form`, `pageview`,
  `historyChange`).
- `builtInVariable[].type`: **código numérico** — este é o campo mais propenso
  ao erro "Unrecognized value". Conferir o número atual para cada variável
  embutida.
- `variable[].type`: código de string (ex.: `d` = dataLayer value, `c` =
  constant).
- todos os IDs de `containerId`/`accountId` podem ser `0` (placeholder) na
  exportação para importação.