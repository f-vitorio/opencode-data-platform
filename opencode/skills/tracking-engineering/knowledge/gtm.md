# GTM — Google Tag Manager

> Documentação interna. A documentação oficial atual decide.
> Antes de implementar, consultar: https://developers.google.com/tag-manager

## O que é

GTM é um gerenciador de tags. Hospeda tags (GA4, Google Ads, etc.) e as dispara
por triggers, usando variáveis. A comunicação com o site ocorre via dataLayer.

## Componentes

- **Container:** config com ID `GTM-XXXXXXX`.
- **Tag:** o que executar (ex.: GA4 config, GA4 event, Google Ads conversion).
- **Trigger:** condição para disparar uma tag.
- **Variable:** valor usado por tags/triggers (ex.: `Page Path`,
  `Event Name`, variáveis de dataLayer).
- **dataLayer:** objeto JS `window.dataLayer` usado para passar eventos.

## Instalação

Dois snippets no site: um no `<head>` e um após a abertura do `<body>`.
Em frameworks (React/Astro/Vue), usar a forma adequada e evitar duplicação.

## Regras de uso

- usar GTM para **orquestração**, não para lógica pesada;
- empurrar eventos limpos no dataLayer (não misturar lógica no GTM);
- evitar múltiplos containers;
- versionar cada publicação;
- nomes de trigger/variável consistentes.

## Google Tag no GTM

A partir das mudanças de abril de 2025, o Google Tag (`gtag`) é o formato
recomendado dentro do GTM para GA4 e Google Ads. Consultar a documentação
atual sobre o comportamento do Google Tag antes de montar o container.

## Geração/validação de container JSON

Ao gerar um container JSON para importação, **respeitar o schema atual**.
Enums devem usar os valores de string corretos do schema. Um erro do tipo:

```
Error deserializing enum type [Type]. Unrecognized value [1]
```

indica valor de enum inválido. Evitar. Validar o JSON antes de entregar.

## Referências oficiais

- https://developers.google.com/tag-manager
- https://developers.google.com/tag-manager/api/v2
- https://support.google.com/tagmanager/answer/6103696

## Dica FVS7

Carga única: instalar o GTM e deixar ele carregar o Google Tag. Nunca
carregar gtag.js direto **e** via GTM ao mesmo tempo (fonte de `page_view`
duplicado).