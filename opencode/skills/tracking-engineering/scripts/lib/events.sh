#!/usr/bin/env bash
# tracking-engineering: lib/events
# Helper compartilhado — garante que audit e validate detectem eventos
# de forma IDENTICA. Fonte única da verdade de nomenclatura.
set -uo pipefail

# Eventos padrão FVS7 (ordem exibida em relatórios)
FVS7_EVENTS=(page_view scroll_90 cta_click whatsapp_click phone_click form_start form_submit generate_lead service_selected)

# Detecção: evento presente se aparecer como string literal (aspas simples OU
# duplas), em qualquer contexto — `event: "x"`, `pushEvent("x", ...)`,
# `gtag("event", "x", ...)`. Não exige `event:` porque chamadas de wrapper
# também emitem o evento.
#
# Uso: event_present <dir> <event>
event_present() {
  local dir="$1" ev="$2"
  grep -rqE --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=.git \
    --exclude-dir=.astro --exclude-dir=.cache \
    "[\"']${ev}[\"']" "$dir" 2>/dev/null
  return $?
}

# Lista eventos ausentes (para relatório)
# Uso: missing_events <dir> -> imprime eventos ausentes, um por linha
missing_events() {
  local dir="$1" ev
  for ev in "${FVS7_EVENTS[@]}"; do
    if ! event_present "$dir" "$ev"; then
      echo "$ev"
    fi
  done
}

# grep com exclusão de diretórios pesados/generados.
# Uso: rgrep <dir> <pattern> -> ecoa arquivos correspondentes
rgrep() {
  local dir="$1" pattern="$2"
  grep -rlE --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=.git \
    --exclude-dir=.astro --exclude-dir=.cache \
    "$pattern" "$dir" 2>/dev/null
}