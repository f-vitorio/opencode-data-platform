# Google Ads Customer ID

## FVS7
- Customer ID: **604-535-1809**
- Conta principal da agência

## Regra
Sempre perguntar o Customer ID (formato XXX-XXX-XXXX) ao criar campanhas em CSV para importação no Google Ads.

# Lições Aprendidas - CSV Google Ads

## Erros Comuns e Correções

### 1. Customer ID
- **Erro:** ID faltando ou em coluna errada
- **Correção:** Sempre perguntar o Customer ID (formato XXX-XXX-XXXX) ANTES de criar os CSVs
- **Regra:** ID obrigatório em TODOS os arquivos (campanha, grupos, keywords, anúncios, negativas)

### 2. Language
- **Erro:** Usar "pt-BR" não é reconhecido
- **Correção:** Usar apenas "pt" para português

### 3. EU political ads
- **Erro:** Coluna vazia causa erro
- **Correção:** Sempre incluir "No" (a menos que seja propaganda política na UE)

### 4. Formato do Customer ID
- **Erro:** Colocar em coluna errada (position mismatch)
- **Correção:** Verificar sempre a posição exata da coluna "Customer ID" no header de cada template

## Ordem de Importação (sempre)
1. campanha.csv
2. grupos_de_anuncio.csv
3. palavras_chave.csv
4. anuncios_rsa.csv
5. palavras_chave_negativas.csv

## Checklist Antes de Criar CSVs
- [ ] Perguntar Customer ID
- [ ] VerificarLanguage = "pt" (não "pt-BR")
- [ ] Verificar EU political ads = "No"
- [ ] Confirmar Customer ID em TODOS os arquivos

## Campanha Criada (CSV - ainda não importada)
- **Status**: Aguardando MCP Google Ads
- **Arquivos**: ~/Documents/GOOGLE ADS/campanha-gestor-trafego/
- **Estrutura**:
  - 1 campanha "Gestor de Tráfego - Search" (Search, R$ 30/dia, pausada)
  - 3 ad groups (Gestor de Tráfego, Google Ads para Empresas, Landing Pages)
  - 18 keywords (6 por grupo)
  - 9 RSA ads (3 por grupo, 15 headlines + 4 descriptions cada)
  - 28 negativas (10 globais + 18 por grupo)
  - URL: https://fvs7.com.br/gestor-trafego/
