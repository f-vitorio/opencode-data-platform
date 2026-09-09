# SCHEMA — EVENTOS (FVS7)

Definição canônica de cada evento e parâmetros. Fonte da verdade para
`dataLayer.push` em todos os projetos.

Convenção de nome: `objeto_ação[_contexto]`, minúsculas, underscores.

---

## page_view

Disparado automaticamente pelo Google Tag (All Pages / History Change).

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `page_title` | string | auto |
| `page_path` | string | auto |
| `page_location` | string | auto |

---

## scroll_90

Disparado quando o usuário rola 90% da página.

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `page_path` | string | sim |

---

## cta_click

Clique em qualquer CTA.

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `cta_text` | string | sim |
| `cta_location` | string | sim (hero, form, footer...) |
| `page_path` | string | sim |

---

## whatsapp_click

Clique em link do WhatsApp.

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `cta_location` | string | sim |
| `page_path` | string | sim |
| `phone` | string | opcional |

---

## phone_click

Clique em link telefônico.

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `cta_location` | string | sim |
| `page_path` | string | sim |
| `phone` | string | opcional |

---

## form_start

Primeira interação do usuário com o formulário.

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `form_id` | string | sim |
| `page_path` | string | sim |

---

## form_submit

Usuário enviou o formulário (independe do sucesso).

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `form_id` | string | sim |
| `page_path` | string | sim |

---

## generate_lead

Lead gerado com sucesso. **Conversão principal.**

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `lead_type` | string | sim (form, whatsapp, phone) |
| `service` | string | sim |
| `page_path` | string | sim |
| `form_id` | string | opcional |
| `utm_source` | string | preservado |
| `utm_campaign` | string | preservado |

Exemplo:

```js
dataLayer.push({
  event: "generate_lead",
  lead_type: "form",
  service: "google_ads",
  page_path: "/google-ads/"
});
```

---

## lead_generated

Alias de `generate_lead` para alguns fluxos. Manter consistência: usar
`generate_lead` como padrão principal.

---

## service_selected

Usuário selecionou um serviço (etapas de multi-serviço).

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `service` | string | sim |
| `page_path` | string | sim |

---

## qualified_lead / sale

Eventos offline vindos do CRM/Supabase (Measurement Protocol / Offline
Conversion Import). Não disparados no navegador.

| Parâmetro | Tipo | Obrigatório |
|-----------|------|-------------|
| `lead_id` | string | sim |
| `service` | string | sim |
| `value` | number | opcional (para sale) |

---

## Regras de conversão

- `generate_lead` → key event GA4 + primary no Google Ads.
- `page_view` → nunca é conversão.
- cliques (`cta_click`, `whatsapp_click`, `phone_click`) → microconversões.
- `form_start` → microconversão.
- contagem: 1 `generate_lead` por sessão por padrão.