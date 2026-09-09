# SCHEMA — DATA LAYER

Definição de como o dataLayer deve ser estruturado.

## Inicialização

```js
window.dataLayer = window.dataLayer || [];
```

## Formato de push

Sempre um objeto com `event` (obrigatório) + parâmetros.

```js
dataLayer.push({
  event: "generate_lead",
  lead_type: "form",
  service: "google_ads",
  page_path: "/google-ads/"
});
```

## Convenções

- `event` em minúsculas, com underscores;
- parâmetros em snake_case;
- sem PII (email, telefone) exceto em fluxos de Enhanced Conversions tratados
  com hash;
- sem espaços em valores de enumeração (usar snake_case);
- sem campos de texto livre desnecessários.

## Variáveis de dataLayer no GTM

No GTM, ler valores via variáveis de dataLayer:

- `dataLayer.event`
- `dataLayer.lead_type`
- `dataLayer.service`
- `dataLayer.page_path`
- etc.

## Carga inicial (importante)

Ao invés de muitos `push` isolados, é aceitável empurrar uma estrutura inicial
no load:

```js
dataLayer.push({
  event: "page_view",
  page_path: location.pathname,
  page_title: document.title
});
```

## Regras de timing

- eventos de clique: imediatamente no handler;
- `form_start`: primeira interação;
- `form_submit`: no submit;
- `generate_lead`: apenas no sucesso confirmado;
- `page_view` em SPA: a cada rota, sem duplicar.

## Referência

- https://developers.google.com/tag-manager/devguide