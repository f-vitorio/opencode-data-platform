# PROCEDURE — RASTREAR FORMULÁRIO

> Objetivo: medir `form_start`, `form_submit` e `generate_lead` (lead).

## 1. Auditar o formulário

- localizar o formulário (id, classes, handler de submit);
- identificar como o sucesso é detectado (redirect, resposta AJAX, página de
  agradecimento).

## 2. Evento de sucesso

- definir a página/condição que representa o lead gerado;
- normalmente: sucesso do submit do formulário.

## 3. Implementar dataLayer

- `form_start` na primeira interação do usuário com o formulário;
- `form_submit` quando o usuário envia;
- `generate_lead` no sucesso (NÃO em submit que pode falhar).

```js
dataLayer.push({ event: "form_start", form_id: "lead-form", page_path: location.pathname });
dataLayer.push({ event: "form_submit", form_id: "lead-form", page_path: location.pathname });
// no sucesso:
dataLayer.push({ event: "generate_lead", lead_type: "form", service: "google_ads", page_path: location.pathname });
```

## 4. GA4

- criar tags de evento GA4 para `form_start`, `form_submit`, `generate_lead`;
- marcar `generate_lead` como **key event** quando apropriado.

## 5. Google Ads

- criar tag de conversão `Lead` disparando em `generate_lead`;
- marcar como primary;
- configurar Enhanced Conversions (email/telefone) quando aplicável.

## 6. Consentimento

- garantir que as tags respeitem o Consent Mode (ver `consent-mode.md`).

## 7. Validação

- preencher o formulário no GTM Preview e no GA4 DebugView;
- confirmar `generate_lead` apenas no sucesso real;
- ver `procedures/validate.md`.

## Referência

- https://developers.google.com/tag-manager/form-triggers