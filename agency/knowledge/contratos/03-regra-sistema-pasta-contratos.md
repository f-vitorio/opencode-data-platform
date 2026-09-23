# Regra do Sistema — Pasta de Contratos

## Obrigação
Todos os contratos comerciais criados pela agência **DEVEM** ser salvos nas seguintes localizações:

1. **Google Drive — Pasta CONTRATOS**
   - URL: https://drive.google.com/drive/folders/1RnUbqIjnuun-_QseAsVFNXNFhUYyZLbA
   - Pasta específica: `CONTRATOS` (nível raiz da pasta oficial da agência)
   - Finalidade: Storage oficial e compartilhamento com a equipe

2. **Banco de Dados Supabase**
   - Tabela: `contracts`
   - Finalidade: Registro estruturado, pipeline comercial, histórico e relatórios

## Fluxo Obrigatório
Ao criar qualquer contrato, executar obrigatoriamente:

1. **Criar registro** na tabela `contracts` do Supabase
2. **Atualizar stage** do cliente para `'CONTRATO'` (ou manter se já estiver nessa etapa)
3. **Fazer upload** do contrato assinado/PDF para a pasta Google Drive `CONTRATOS`
4. **Registrar interação** no histórico do cliente (tabela `interactions`)

## Justificativa
- **Rastreabilidade**: O banco de dados Supabase é a fonte de verdade para o pipeline comercial
- **Acesso da equipe**: A pasta Google Drive permite que qualquer membro da equipe visualize e baixe os contratos
- **Backup**: Duplicidade de storage (cloud + banco) garante que nenhum contrato se perca
- **Conformidade**: Facilita auditorias e consultas históricas

## Consequência da Não-Compliance
- Contratos não salvos no Google Drive `CONTRATOS` serão considerados **não-oficiais** para fins de acesso da equipe
- Falha em atualizar o stage do cliente pode causar inconsistões no pipeline de vendas
- Ausência de registro no banco de dados impede geração de relatórios e métricas

## Exceções
Somente com autorização explícita do gestor:
- Contratos temporários ou de teste (devem ser marcados como tais e limpos após período definido)
- Casos de urgência onde o upload for impossibilitado (devidamente justificado e compensado posteriormente)

## Responsabilidade
- **Criador do contrato**: Responsável por executar os 3 passos obrigatórios (banco, drive, interação)
- **Gestor/Coordenação**: Responsável por fiscalizar a conformidade e autorizar exceções

## Documentação Relacionada
- Pasta oficial de conhecimento: `/home/fvitorio/.agency/knowledge/contratos/`
- Contrato exemplo: `02-contrato-site-vetorial.md` (Fernando Serrano Vicentini)
- Integração CRM: Skill `contracts` — fluxo `CREATE CONTRACT → UPDATE CLIENT STAGE → UPLOAD DRIVE → RECORD INTERACTION`