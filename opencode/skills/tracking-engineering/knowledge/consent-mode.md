# CONSENT MODE

> Documentação interna. A documentação oficial atual decide.
> Antes de implementar, consultar: https://developers.google.com/tag-platform/security/guides/consent

## O que é

Consent Mode permite que as tags do Google respeitem o estado de consentimento
do usuário antes de enviar dados. Necessário quando o site tem banner de
cookies / exigência de consentimento (LGPD, GDPR, etc.).

## Funcionamento

- O site comunica o consentimento ao Google via comandos (`gtag('consent', ...)`)
  ou pela API de consentimento de tags (`dataLayer.push({event: 'consent...'})`).
- Estados típicos: `granted` / `denied` para `ad_storage`, `analytics_storage`,
  `ad_user_data`, `ad_personalization`.
- Com `denied` em modo básico, as tags não disparam; com Consent Mode v2 /
  modelagem, o Google pode modelar conversões.

## Por que importa

- sem Consent Mode, tags podem disparar antes do consentimento (violação);
- com Consent Mode v2, manter conversões modeladas quando negado;
- requisito importante para Enhanced Conversions e personalização.

## Boas práticas

- configurar estado padrão (denied) no snippet inicial;
- atualizar estado quando o usuário decide;
- testar com consentimento negado e concedido;
- garantir que o botão do banner atualize o consentimento antes das tags.

## Referências oficiais

- https://developers.google.com/tag-platform/security/guides/consent
- https://support.google.com/google-ads/answer/10000067

## Dica FVS7

Quando houver banner, tratar Consent Mode como parte da implementação
obrigatória do `standards/fvs7-tracking-standard.md`. Verificar sempre a
versão atual (Consent Mode v2 e mudanças regionais).