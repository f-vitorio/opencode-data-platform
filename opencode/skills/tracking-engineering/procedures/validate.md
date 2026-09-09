# PROCEDURE — VALIDAR TRACKING

> Nenhuma implementação está concluída sem validação.

## Ferramentas

- GTM Preview (modo preview do container);
- GA4 DebugView;
- Google Ads (teste de conversão / ações);
- console do navegador.

## Passos obrigatórios

1. **GTM Preview** — ativar preview e navegar no site.
2. **GA4 DebugView** — confirmar eventos recebidos.
3. **Google Ads** — confirmar conversão e Enhanced Conversions.
4. **Console** — verificar erros de JS, PII, duplicidade.

## Checklist de eventos

- `page_view` dispara uma vez por carregamento real;
- `scroll_90` dispara após rolar;
- `cta_click`, `whatsapp_click`, `phone_click` disparam por clique;
- `form_start` dispara na interação com o formulário;
- `form_submit` dispara no envio;
- `generate_lead` dispara **apenas no sucesso** (não em submit que falha).

## Checagens específicas

### page_view duplicado (Astro/SPA)

- navegar entre páginas;
- confirmar que cada rota gera um único `page_view`;
- verificar se o script está carregado direto E via GTM (duplicação).

### Consent Mode

- testar com consentimento negado e concedido;
- confirmar comportamento correto das tags em cada estado.

### Enhanced Conversions

- disparar um lead de teste;
- confirmar recebimento dos dados com hash no Google Ads.

## Output

- registrar resultado em `docs/tracking.md`;
- reportar qualquer evento não validado como pendência.