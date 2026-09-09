# PROCEDURE — RASTREAR TELEFONE

> Objetivo: medir cliques em links telefônicos (`phone_click`) como
> microconversão.

## 1. Identificar os links

- links `tel:<número>`;
- botões que disparam ligação.

## 2. Implementar dataLayer

```js
dataLayer.push({
  event: "phone_click",
  cta_location: "header",
  page_path: location.pathname,
  phone: "5511999999999"      // opcional (sem PII indevida)
});
```

## 3. GA4

- tag de evento GA4 para `phone_click`;
- pode marcar como key event (microconversão).

## 4. Google Ads

- opcional: tag de conversão secundária para `phone_click`;
- manter como secondary.

## 5. Validação

- clicar no link `tel:` no GTM Preview;
- confirmar push disparado uma única vez;
- ver `procedures/validate.md`.