# ENHANCED CONVERSIONS

> Documentação interna. A documentação oficial atual decide.
> Antes de implementar, consultar: https://support.google.com/google-ads/answer/10071027

## O que é

Enhanced Conversions complementa a conversão de website com dados de primeiro
party (email/telefone) com hash, enviados de forma segura, para melhorar a
precisão de atribuição (especialmente com cookies limitados).

## Como funciona

- os dados do usuário (ex.: email, telefone) são coletados no formulário;
- são transformados em hash (SHA-256) antes do envio;
- o Google usa para reconciliar com contas logadas (atribuição mais precisa);
- para leads, é a variante "Enhanced Conversions for Leads".

## Formas de implementar

- via GTM (tag de conversão com configuração de enhanced conversions);
- via código (função `gtag('set', 'user_data', {...})` no momento da conversão);
- via API (para leads, envio dos dados no momento do lead).

## Requisitos

- consentimento adequado;
- endereço (email) com hash SHA-256 em letras minúsculas e sem espaços;
- telefone normalizado;
- coleta apenas quando legalmente permitido.

## Importância para leads

O envio de email/telefone do formulário junto à conversão permite ao Google
Ads otimizar por leads de maior qualidade.

## Referências oficiais

- https://support.google.com/google-ads/answer/10071027 (enhanced)
- https://support.google.com/google-ads/answer/10071027#leads (enhanced for leads)

## Dica FVS7

Configurar Enhanced Conversions para `generate_lead` sempre que o formulário
coletar email ou telefone. Não enviar dados sem consentimento.