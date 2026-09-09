# SERVER-SIDE TAGGING

> Documentação interna. A documentação oficial atual decide.
> Antes de implementar, consultar: https://developers.google.com/tag-platform/tag-manager/server-side

## O que é

Server-side tagging move a orquestração de tags do navegador para um servidor
próprio (ex.: Google Cloud Run, App Engine), onde um container GTM server-side
processa e reencaminha dados. O navegador envia para um domínio próprio.

## Benefícios

- performance (menos tags no cliente);
- controle de dados (first-party);
- melhor consentimento e governança;
- reduz impactos de bloqueadores e limitações de cookies.

## Quando usar

Para sites da FVS7, considerar quando:

- houver exigência avançada de consentimento/privacy;
- precisar consolidar dados de múltiplas fontes;
- quiser preparar conversões offline / MP robusto;
- quiser um domínio first-party (Google Tag Gateway).

## Componentes

- container server-side (GTM server-side);
- domínio próprio para o endpoint;
- clientes (clients) que recebem requests;
- tags server-side que reencaminham para GA4/Ads/CRM.

## Atenção

- custo e operação de infraestrutura (Cloud Run etc.);
- configuração de domínio/SSL;
- o Google Tag Gateway for Advertisers é apresentado pelo Google como uma
  configuração mais durável e first-party — consultar docs antes de decidir.

## Referências oficiais

- https://developers.google.com/tag-platform/tag-manager/server-side

## Dica FVS7

Começar com tracking client-side bem feito. Server-side é evolução para
projetos com requisitos de privacidade ou consolidação de dados. Deixar
previsto na arquitetura, não obrigatório em todo site.