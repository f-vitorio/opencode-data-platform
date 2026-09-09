# GOOGLE ADS — Conversões

> Documentação interna. A documentação oficial atual decide.
> Antes de implementar, consultar: https://developers.google.com/google-ads

## O que é

Google Ads rastreia conversões (ações valiosas) atribuídas a cliques em
anúncios. Para a FVS7, a conversão principal é `Lead`.

## Conversões

- **Conversão de website:** disparada por tag (via GTM) quando o usuário
  conclui uma ação (ex.: `generate_lead`).
- **Primary vs secondary:** `Lead` como primary; microconversões como
  secondary.
- **Conversion ID / Label:** identificadores da ação de conversão.
- **Enhanced Conversions:** coleta de dados de hash (email/telefone) para
  melhorar atribuição (ver `knowledge/enhanced-conversions.md`).
- **Offline Conversion Import:** envia conversões do CRM (qualificação,
  venda) de volta ao Google Ads.

## Configuração de conversão de lead

1. Definir a ação de conversão (ex.: "Lead").
2. Criar tag de conversão no GTM disparando em `generate_lead`.
3. Associar à ação primária.
4. Configurar Enhanced Conversions se aplicável.

## Valor de conversão (opcional)

- Se o negócio tiver valor por lead, configurar o valor da conversão.
- Caso contrário, usar conversão sem valor.

## Referências oficiais

- https://developers.google.com/google-ads
- https://support.google.com/google-ads/answer/3417291 (conversões)
- https://support.google.com/google-ads/answer/6089979 (offline)
- https://support.google.com/google-ads/answer/10071027 (enhanced)

## Dica FVS7

Não contar apenas o formulário enviado. Sempre que possível, medir o lead
**qualificado/venda** via Offline Conversion Import — transforma tracking em
infraestrutura de aquisição.