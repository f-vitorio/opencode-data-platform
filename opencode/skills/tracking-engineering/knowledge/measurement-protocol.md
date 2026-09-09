# MEASUREMENT PROTOCOL

> Documentação interna. A documentação oficial atual decide.
> Antes de implementar, consultar: https://developers.google.com/analytics/devguides/collection/protocol/ga4

## O que é

Measurement Protocol (MP) do GA4 permite enviar eventos **diretamente para o
servidor** do Google Analytics, sem passar pelo navegador. Ideal para eventos
que ocorrem no servidor (ex.: lead enviado ao CRM).

## Uso na FVS7

Enviar eventos que ocorrem fora do navegador ou para enriquecer dados:

- `generate_lead` confirmado no servidor (formulário processado);
- `qualified_lead`, `sale` vindos do CRM/Supabase;
- quando o navegador não é a fonte confiável.

## Como funciona

- endpoint do GA4 (`/mp/collect`) com `measurement_id` e `api_secret`;
- envia JSON com eventos e parâmetros;
- eventos podem incluir `client_id` para correlacionar com o mesmo usuário.

## Atenção

- exigências de validação de eventos customizados podem mudar;
- não enviar PII;
- usar `api_secret` de forma segura (nunca expor em código de cliente);
- eventos do MP podem alimentar produtos de publicidade vinculados.

## Referências oficiais

- https://developers.google.com/analytics/devguides/collection/protocol/ga4

## Dica FVS7

O MP permite medir **oportunidade/venda** real no servidor — o que transforma
tracking em infraestrutura de aquisição. Combinar com Offline Conversion Import
para Google Ads.