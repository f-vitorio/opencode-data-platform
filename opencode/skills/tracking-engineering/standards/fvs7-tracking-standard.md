# FVS7 TRACKING STANDARD

Padrão obrigatório de mensuração para todos os projetos de sites da FVS7.

Objetivo: garantir que todo site da agência rastreie as mesmas ações, com os
mesmos nomes e parâmetros, independentemente do cliente ou do framework.

Isso permite:

- comparar sites/segmentos entre si;
- reutilizar configurações de GTM/GA4/Ads;
- documentar e auditar com consistência;
- alimentar o CRM e conversões offline de forma uniforme.

---

## 1. EVENTOS PADRÃO

Eventos obrigatórios em todo site de geração de leads:

| Evento            | Obrigatório | Trigger                      | GA4        | Google Ads        |
|-------------------|-------------|------------------------------|------------|-------------------|
| `page_view`       | Sim         | page load / History Change   | automático | -                 |
| `scroll_90`       | Sim         | 90% de rolagem               | key event  | - (opcional)      |
| `cta_click`       | Sim         | clique em CTA                | key event  | -                 |
| `whatsapp_click`  | Sim         | clique em link do WhatsApp   | key event  | microconversão    |
| `phone_click`     | Sim         | clique em link telefônico    | key event  | microconversão    |
| `form_start`      | Sim         | interação com formulário     | key event  | microconversão    |
| `form_submit`     | Sim         | envio de formulário          | key event  | -                 |
| `lead_generated`  | Sim         | conversão de lead            | **key event** | **primary**   |
| `generate_lead`   | Sim         | lead gerado (sucesso)        | **key event** | **primary**   |
| `service_selected`| Recomendado | seleção de serviço           | evento     | -                 |
| `qualified_lead`  | Opcional    | lead qualificado (CRM)       | -          | conversão offline |
| `sale`            | Opcional    | venda fechada (CRM)          | -          | conversão offline |

---

## 2. CONVERSÕES PRINCIPAIS E MICRO

### GA4

- `generate_lead` → **key event** (conversão principal).
- Microconversões marcadas como key events quando ajudarem decisões:
  `cta_click`, `whatsapp_click`, `phone_click`, `form_start`, `scroll_90`.

### Google Ads

- `Lead` (via `generate_lead`/`lead_generated`) → **primary conversion**.
- Microconversões (`whatsapp_click`, `phone_click`, `form_start`) →
  **secondary** (para otimização quando útil, sem inflar a primary).

### Offline (CRM)

- `qualified_lead` e `sale` enviadas por **Offline Conversion Import** ou
  **Measurement Protocol** a partir do CRM/Supabase, quando configurado.

---

## 3. PARÂMETROS POR EVENTO

Ver `schemas/events.md` para a definição completa de cada evento e parâmetros.

Resumo do exemplo de `generate_lead`:

```js
dataLayer.push({
  event: "generate_lead",
  lead_type: "form",        // form | whatsapp | phone
  service: "google_ads",    // serviço/serviço de origem
  page_path: "/google-ads/",
  form_id: "lead-form",     // opcional
  utm_source: "google",     // preservado
  utm_campaign: "google-ads"
});
```

---

## 4. IDENTIFICADORES OBRIGATÓRIOS POR PROJETO

Cada projeto deve ter um bloco de configuração único. Guardar em
`docs/tracking.md` do projeto (nunca em código versionado quando sensível):

- GA4 Measurement ID
- GTM Container ID
- Google Ads Conversion ID / Conversion Label
- WhatsApp número (para o link)
- IDs de formulário

---

## 5. NOMENCLATURA

- apenas letras minúsculas;
- underscores (`_`) como separador;
- sem espaços, sem hífens, sem caracteres especiais;
- padrão: `objeto_ação[_contexto]`.

Exemplos:

- `whatsapp_click`
- `phone_click`
- `form_start`
- `lead_generated`

---

## 6. REGRAS DE CONVERSÃO

- contagem: uma conversão por sessão para `generate_lead` (evitar duplicar);
- `page_view` **nunca** é conversão;
- CTA/clique **não** é conversão por si só — é microconversão;
- conversão real = lead gerado (ou venda via offline).

---

## 7. FRAMEWORKS

O padrão é o mesmo em todos os frameworks, mas a implementação do `page_view`
muda:

| Framework | page_view |
|-----------|-----------|
| MPA / SSG (Astro estático) | page load |
| SPA / Astro com view transitions | History Change / view transition |
| SSR | page load / History Change quando navegação client-side |

Sempre validar contra `page_view` duplicado (ver `procedures/validate.md`).

---

## 8. IMPLEMENTAÇÃO MÍNIMA ACEITÁVEL

Um projeto só é considerado "em padrão FVS7" quando tiver:

1. GA4 + GTM instalados (um só caminho de carga, sem duplicação).
2. Google Ads com conversão `Lead` configurada.
3. Eventos: `page_view`, `scroll_90`, `cta_click`, `whatsapp_click`,
   `phone_click`, `form_start`, `form_submit`, `lead_generated`.
4. dataLayer estruturado conforme `schemas/datalayer.md`.
5. Consent Mode configurado (se exigido).
6. `docs/tracking.md` gerado.
7. Auditoria validada (GA4 DebugView / GTM Preview / Google Ads).