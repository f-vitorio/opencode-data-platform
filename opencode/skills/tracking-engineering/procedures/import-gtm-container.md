# PROCEDURE — IMPORTAR CONTAINER GTM (por cliente)

> Fluxo reutilizável para configurar tracking via importação de container em
> qualquer site da FVS7. Uso: sempre que montar o tracking de um novo cliente.

## Por que importar

O import via UI é o método mais confiável (não depende de API/OAuth). O JSON é
gerado por script com o schema atual, então passa sem erros de enum.

---

## 1. Criar o config do cliente

Criar `scripts/configs/<cliente>.json` com:

```json
{
  "gtmPublicId": "GTM-XXXXXXX",
  "ga4MeasurementId": "G-XXXXXXXXXX",
  "accountId": "1234567890",
  "containerId": "123456789",
  "containerName": "www.cliente.com.br",
  "events": ["page_view", "form_submit_whatsapp", "generate_lead", ...],
  "variables": ["value", "currency", "page_path", ...]
}
```

**Dados a obter do cliente/Google:**
- `accountId` e `containerId`: no GTM, ao abrir o container, a URL contém
  `accounts/<accountId>/containers/<containerId>`.
- `gtmPublicId`: o `GTM-XXXXXXX`.
- `ga4MeasurementId`: o `G-XXXXXXX` da propriedade GA4 do cliente.

## 2. Gerar o JSON de import

```bash
node scripts/generate-gtm-container.cjs scripts/configs/<cliente>.json
```

Gera `<cliente>.import.json` ao lado do config.

## 3. Validar antes de entregar

```bash
scripts/test scripts/configs/<cliente>.import.json
```

Conferir: JSON válido, sem `MAP`/`LIST`, sem enums antigos, sem placeholder `< >`.

## 4. Importar no GTM (UI — ação do cliente/agência)

1. tagmanager.google.com → abrir o container do cliente.
2. **Admin → Importar contêiner**.
3. Selecionar `<cliente>.import.json`.
4. Opção: **Substituir** (Overwrite).
5. Revisar no workspace → **Publicar**.

## 5. Deploy do site

Fazer o deploy do site (o código novo depende do GTM). Sem deploy, o tracking
não dispara.

## 6. Conversão do Google Ads (direto no Google Ads)

A conversão NÃO vai no container. No Google Ads:
1. **Objetivos → Conversões → Nova conversão** → website.
2. Vincular ao evento do GA4 linkado (ex.: `form_submit_whatsapp`).
3. Marcar como conversão primária (Lead).

Assim o Google Ads lê a conversão do GA4, sem tag extra no GTM.

## 7. Pós-import: adicionar parâmetros/Enhanced na UI

O JSON de import é mínimo (sem `eventParameters`/Enhanced por segurança de
schema). Após importar, adicionar na UI do GTM, quando necessário:
- **Parâmetros customizados** em cada tag GA4 Event (eventParameters).
- **Enhanced Conversions** na tag `generate_lead`.
- **Consent Mode** no site (ver `knowledge/consent-mode.md`).

## 8. Validar

- GTM Preview / GA4 DebugView: `form_submit_whatsapp` dispara 1x no sucesso.
- `page_view` sem duplicação.
- Google Ads: conversão registrada.

---

## Checklist final (todo site)

- [ ] Container importado e publicado (só GA4).
- [ ] Site com deploy (GTM único host; sem gtag direto).
- [ ] `form_submit_whatsapp` = conversão/key event no GA4.
- [ ] Conversão do Google Ads (Lead) importada direto no Google Ads.
- [ ] `docs/tracking.md` gerado.
- [ ] Auditoria validada (`scripts/audit`).