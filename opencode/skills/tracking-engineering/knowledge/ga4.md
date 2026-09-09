# GA4 — Google Analytics 4

> Documentação interna. A documentação oficial atual decide.
> Antes de implementar, consultar: https://developers.google.com/analytics

## O que é

GA4 é o produto de analytics do Google baseado em eventos (não em sessões
hierárquicas como o Universal Analytics). Cada interação significativa é um
evento com parâmetros.

## Conceitos-chave

- **Evento:** unidade de medição (ex.: `page_view`, `generate_lead`).
- **Parâmetro:** contexto do evento (ex.: `lead_type`, `service`).
- **Key Event:** evento que você considera conversão e quer acompanhar.
- **Eventos recomendados:** nomes sugeridos pelo Google para padronização.
- **Eventos personalizados:** eventos próprios (`generate_lead`).
- **Measurement ID:** identificador `G-XXXXXXX` / `GT-XXXXXXX` da stream web.

## Eventos automáticos vs manual

- `page_view` é gerado automaticamente pela configuração do Google Tag.
- Eventos personalizados exigem `dataLayer.push` + tag/trigger no GTM.

## Limites conhecidos (verificar no docs)

- total de eventos por hit;
- cardinalidade de parâmetros (50 parâmetros por evento);
- tamanho de strings;
- PII nunca deve ser enviada como parâmetro.

## page_view em SPA/Astro

- Em SPA, disparar `page_view` a cada mudança de rota real.
- Evitar disparo duplicado quando o script está tanto direto quanto via GTM.
- Consultar docs sobre "SPA" / view transitions antes de implementar.

## Referências oficiais

- https://developers.google.com/analytics/devguides/collection/ga4
- https://developers.google.com/analytics/devguides/collection/ga4/reference
- https://support.google.com/analytics/answer/9322687

## Dica FVS7

Tratar `generate_lead` como key event principal. Não tratar `page_view` como
conversão.