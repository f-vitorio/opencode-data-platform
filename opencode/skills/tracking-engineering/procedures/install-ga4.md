# PROCEDURE — INSTALAR GA4

> Antes de implementar, consultar a documentação oficial atual.

## Pré-requisitos

- acesso à propriedade GA4;
- stream de dados web com Measurement ID (`G-XXXXXXX` / `GT-XXXXXXX`);
- decidir se o GA4 será carregado via GTM ou diretamente (recomendado: via GTM).

## Decisão de carga

**Recomendado (FVS7):** instalar via GTM (ver `setup-gtm.md`). O GTM carrega
o Google Tag (GA4 config). Isso evita duplicação de `page_view`.

## Passos (via GTM)

1. Criar tag "Google Tag" (GA4 config) com o Measurement ID.
2. Definir trigger: "All Pages".
3. Conferir se `page_view` automático está ativo e sem duplicidade.
4. Publicar e validar.

## Passos (direto, sem GTM)

1. Inserir o snippet do Google Tag (`gtag`) no `<head>`.
2. Em Astro/SSG, garantir que carregue apenas uma vez.
3. Em SPA, configurar o envio de `page_view` em cada rota sem duplicar.

## Validação

- GA4 DebugView mostra `page_view` sem duplicidade;
- um único hit de page_view por carregamento real de página;
- ver `procedures/validate.md`.

## Referência

- https://developers.google.com/analytics/devguides/collection/ga4
- https://support.google.com/tagmanager/answer/12159116