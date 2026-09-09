# PROCEDURE — RASTREAR WHATSAPP

> Objetivo: medir cliques em links do WhatsApp (`whatsapp_click`) como
> microconversão.

## 1. Identificar os links

- links com `https://wa.me/<número>` ou `https://api.whatsapp.com/send?...`;
- botões e CTAs que abrem o WhatsApp.

## 2. Implementar dataLayer

Nos cliques desses links:

```js
dataLayer.push({
  event: "whatsapp_click",
  cta_location: "hero",       // onde estava o botão
  page_path: location.pathname,
  phone: "5511999999999"      // opcional (sem PII indevida)
});
```

## 3. GA4

- tag de evento GA4 para `whatsapp_click`;
- pode marcar como key event (microconversão).

## 4. Google Ads

- opcional: tag de conversão secundária para `whatsapp_click`;
- manter como secondary para não inflar a primary.

## 5. Validação

- clicar no botão no GTM Preview;
- confirmar push disparado uma única vez por clique;
- ver `procedures/validate.md`.

## Referência

- https://support.google.com/analytics/answer/9607278