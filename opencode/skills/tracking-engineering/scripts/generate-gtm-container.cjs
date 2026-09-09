#!/usr/bin/env node
/**
 * tracking-engineering: generate-gtm-container
 * Gera o container GTM de IMPORTACAO (somente GA4) para qualquer cliente.
 *
 * USO:
 *   node scripts/generate-gtm-container.cjs scripts/configs/<cliente>.json
 *
 * O config JSON define o que muda por cliente. O restante e o padrao FVS7:
 *   - Somente GA4 (config + tags de evento), sem Google Ads.
 *   - Tags GA4 Event minimas: eventName + measurementIdOverride (sem MAP).
 *   - sendPageView=false; page_view vai pela tag de evento.
 *   - Enums no formato atual (TEMPLATE/BOOLEAN/INTEGER, CUSTOM_EVENT/PAGEVIEW, EQUALS).
 *
 * CONFIG (scripts/configs/<cliente>.json):
 * {
 *   "gtmPublicId": "GTM-XXXXXXX",
 *   "ga4MeasurementId": "G-XXXXXXXXXX",
 *   "accountId": "1234567890",
 *   "containerId": "123456789",
 *   "containerName": "www.cliente.com.br",
 *   "events": ["form_submit_whatsapp", "page_view", "generate_lead", ...]
 * }
 *
 * SAIDA: cria <arquivo>.import.json ao lado do config.
 */
const { readFileSync, writeFileSync } = require("node:fs");
const { join } = require("node:path");

const configPath = process.argv[2];
if (!configPath) {
  console.error("Uso: node generate-gtm-container.cjs scripts/configs/<cliente>.json");
  process.exit(1);
}

const cfg = JSON.parse(readFileSync(configPath, "utf8"));
const outPath = configPath.replace(/\.json$/, ".import.json");

const AID = cfg.accountId;
const CID = cfg.containerId;
const GTM_ID = cfg.gtmPublicId;
const GA4_ID = cfg.ga4MeasurementId;
const events = cfg.events;

// ===== Triggers =====
const triggers = events.map((ev, i) => ({
  triggerId: String(i + 1),
  name: `CE - ${ev}`,
  type: "CUSTOM_EVENT",
  customEventFilter: [
    {
      type: "EQUALS",
      parameter: [
        { type: "TEMPLATE", key: "arg0", value: "{{_event}}" },
        { type: "TEMPLATE", key: "arg1", value: ev },
      ],
    },
  ],
}));
const allPagesTriggerId = String(events.length + 1);
triggers.push({
  accountId: AID,
  containerId: CID,
  triggerId: allPagesTriggerId,
  name: "All Pages",
  type: "PAGEVIEW",
});

const triggerIdByEvent = {};
events.forEach((ev, i) => (triggerIdByEvent[ev] = String(i + 1)));

// ===== Tags =====
const tags = [
  {
    accountId: AID,
    containerId: CID,
    tagId: "1",
    name: "GA4 - Configuration",
    type: "googtag",
    parameter: [
      { type: "TEMPLATE", key: "tagId", value: GA4_ID },
      { type: "BOOLEAN", key: "sendPageView", value: "false" },
    ],
    firingTriggerId: [allPagesTriggerId],
  },
  ...events.map((ev, i) => ({
    accountId: AID,
    containerId: CID,
    tagId: String(i + 2),
    name: `GA4 - Event - ${ev}`,
    type: "gaawe",
    parameter: [
      { type: "TEMPLATE", key: "eventName", value: ev },
      { type: "TEMPLATE", key: "measurementIdOverride", value: GA4_ID },
    ],
    firingTriggerId: [triggerIdByEvent[ev]],
  })),
];

// ===== Variáveis DLV padrão (opcional; ajustar por cliente) =====
const DLV = cfg.variables || [
  "value", "currency", "page_path", "service_interest",
  "business_segment", "event_label",
];
const variables = DLV.map((name, i) => ({
  accountId: AID,
  containerId: CID,
  variableId: String(i + 1),
  name: `DLV - ${name}`,
  type: "v",
  parameter: [
    { type: "INTEGER", key: "dataLayerVersion", value: "2" },
    { type: "TEMPLATE", key: "name", value: name },
  ],
}));

// ===== builtInVariable padrão =====
const builtInVariable = [
  { accountId: AID, containerId: CID, type: "PAGE_URL", name: "Page URL" },
  { accountId: AID, containerId: CID, type: "PAGE_HOSTNAME", name: "Page Hostname" },
  { accountId: AID, containerId: CID, type: "PAGE_PATH", name: "Page Path" },
  { accountId: AID, containerId: CID, type: "REFERRER", name: "Referrer" },
  { accountId: AID, containerId: CID, type: "EVENT", name: "Event" },
];

const cv = {
  accountId: AID,
  containerId: CID,
  containerVersionId: "0",
  container: {
    accountId: AID,
    containerId: CID,
    name: cfg.containerName,
    publicId: GTM_ID,
    usageContext: ["WEB"],
    fingerprint: "0",
    tagManagerUrl: `https://tagmanager.google.com/#/container/accounts/${AID}/containers/${CID}/workspaces?apiLink=container`,
    features: {
      supportUserPermissions: true,
      supportEnvironments: true,
      supportWorkspaces: true,
      supportGtagConfigs: false,
      supportBuiltInVariables: true,
      supportClients: false,
      supportFolders: true,
      supportTags: true,
      supportTemplates: true,
      supportTriggers: true,
      supportVariables: true,
      supportVersions: true,
      supportZones: true,
      supportTransformations: false,
    },
    tagIds: [GTM_ID],
  },
  builtInVariable,
  variable: variables,
  trigger: triggers,
  tag: tags,
  folder: [],
  customTemplate: [],
  fingerprint: "0",
};

const out = {
  exportFormatVersion: 2,
  exportTime: new Date().toISOString().replace("T", " ").slice(0, 19),
  containerVersion: cv,
};

writeFileSync(outPath, JSON.stringify(out, null, 4));
console.log("Gerado:", outPath);
console.log("  container:", GTM_ID, "/", cfg.containerName);
console.log("  GA4:", GA4_ID);
console.log("  triggers:", triggers.length, " tags:", tags.length, " vars:", variables.length);
console.log("  eventos:", events.join(", "));