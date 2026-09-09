# DATALAYER

## O que é

`dataLayer` é um array JavaScript usado pelo GTM para receber eventos e
variáveis do site.

```js
window.dataLayer = window.dataLayer || [];
dataLayer.push({ ... });
```

## Padrão de push

Sempre empurrar objetos com pelo menos `event`:

```js
dataLayer.push({
  event: "generate_lead",
  lead_type: "form",
  service: "google_ads",
  page_path: "/google-ads/"
});
```

O campo `event` permite que triggers do GTM escutem o evento (ex.: trigger
"Custom Event" nomeado `generate_lead`).

## Regras

- eventos em minúsculas, com underscores;
- sem PII;
- sem campos de texto livre desnecessários;
- parâmetros consistentes entre eventos;
- push após o container carregar ou em momento adequado (em SPAs, cuidado
  com o timing de `page_view`).

## Onde empurrar

- em elementos: após clique (CTA, WhatsApp, telefone);
- em formulários: `form_start` na primeira interação, `form_submit` no envio,
  `lead_generated`/`generate_lead` no sucesso;
- em páginas de agradecimento: `generate_lead` (ou no handler do form).

## Naming

- usar variáveis de dataLayer no GTM (`dataLayer.<chave>`) para ler valores;
- não duplicar o mesmo valor em nomes de variáveis inconsistentes.

## Referência

- https://developers.google.com/tag-manager/devguide

## Dica FVS7

Manter `schemas/datalayer.md` como fonte da verdade dos eventos e parâmetros
para todos os projetos.