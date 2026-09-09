# PROCEDURE — CONFIGURAR GOOGLE ADS

> Objetivo: configurar a conversão `Lead` e, quando aplicável, Enhanced
> Conversions e conversões offline.

## 1. Criar a ação de conversão

- em Google Ads: Tools → Conversions;
- criar conversão de **website** do tipo "Lead".

## 2. Criar a tag de conversão no GTM

- tag de conversão do Google Ads disparando em `generate_lead`;
- usar o Conversion ID / Conversion Label da ação.

## 3. Primary vs secondary

- `Lead` → **primary**;
- microconversões (`whatsapp_click`, `phone_click`, `form_start`) → secondary.

## 4. Enhanced Conversions (se o formulário coletar email/telefone)

- habilitar Enhanced Conversions na ação;
- coletar os dados com hash (SHA-256) no momento do `generate_lead`;
- ver `knowledge/enhanced-conversions.md`.

## 5. Offline Conversion Import (quando houver CRM)

- exportar conversões qualificadas/venda do CRM;
- enviar via Offline Conversion Import (ou Measurement Protocol);
- ver `knowledge/measurement-protocol.md`.

## 6. Consentimento

- garantir Consent Mode configurado (ver `consent-mode.md`).

## 7. Validação

- disparar um lead de teste e verificar a conversão no Google Ads;
- confirmar Enhanced Conversions no teste;
- ver `procedures/validate.md`.

## Referência

- https://support.google.com/google-ads/answer/3417291
- https://support.google.com/google-ads/answer/6089979
- https://support.google.com/google-ads/answer/10071027