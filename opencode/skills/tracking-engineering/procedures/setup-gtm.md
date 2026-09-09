# PROCEDURE — CONFIGURAR GTM

> Antes de implementar, consultar a documentação oficial atual.
> Regra dura: nunca gerar enum inválido no container (evitar o erro
> "Unrecognized value").

## 1. Instalar o container no site

- Copiar os dois snippets do GTM (`GTM-XXXXXXX`).
- Em Astro: inserir no layout global uma única vez.
- Nunca duplicar a instalação.

## 2. Estrutura mínima do container

- **Google Tag** (GA4 config) + tag de evento GA4;
- **Google Ads conversion** tag (se houver conta Ads);
- **Conversion Linker** (necessário para conversões e Enhanced Conversions);
- triggers para cada evento (`Custom Event`, `Click`, `Form Submission`, etc.);
- variáveis (`dataLayer.<chave>`, `Page Path`, `Event Name`, etc.).

## 3. Carga única (crítico para Astro/SPA)

- Se o GTM carrega o Google Tag, **não** carregar gtag.js diretamente no site;
- disparar `page_view` via trigger adequado (All Pages + History Change) e
  validar contra duplicação.

## 4. Regras de tags/triggers

- nomear tags/triggers/variáveis de forma consistente;
- evitar triggers não utilizados;
- versionar cada publicação com descrição clara.

## 5. Geração de container JSON (importação)

> Usar o fluxo dedicado: `procedures/import-gtm-container.md`.
> Resumo das regras (detalhe em `knowledge/gtm-container-schema.md`):

- usar `scripts/generate-gtm-container.cjs` + `configs/<cliente>.json`;
- enums no formato atual (UPPERCASE em ParameterType/EventType/ConditionType;
  lowercase em TagType/VariableType);
- **JSON mínimo**: somente GA4, sem `eventParameters`/`userProperties` (MAP),
  sem Google Ads;
- Google Tag com `sendPageView: false`;
- validar com `scripts/test` antes de importar;
- importar na UI: **Admin → Importar contêiner → Substituir → Publicar**.

## 6. Validação

- GTM Preview mostra cada tag disparando no trigger correto;
- nenhum `page_view` duplicado em navegação real;
- ver `procedures/validate.md`.

## Referência

- https://developers.google.com/tag-manager
- https://developers.google.com/tag-manager/api/v2