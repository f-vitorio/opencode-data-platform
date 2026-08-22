# Regras para Importação CSV - Google Ads

## Obrigatório ANTES de criar CSVs
1. **Perguntar Customer ID** (formato XXX-XXX-XXXX) - salvar em conhecimento
2. **Não inventar dados** - sempre usar dados reais da conta

## Formatos que causam erro

| Campo | Errado | Correto |
|-------|--------|---------|
| Language | pt-BR | **pt** |
| EU political ads | (vazio) | **No** |
| Customer ID | (vazio) | **604-535-1809** (ou o ID da conta) |

## Colunas obrigatórias por arquivo

### campanha.csv
- Row Type, Action, Campaign status, **Customer ID**, Campaign, Campaign type, Networks, Budget, Language, Location, EU political ads

### grupos_de_anuncio.csv
- Row Type, Action, Ad group status, **Customer ID**, Campaign, Ad group, Ad group type

### palavras_chave.csv
- Row Type, Action, **Customer ID**, Keyword status, Campaign, Ad group, Keyword, Type

### anuncios_rsa.csv
- Row Type, Action, Ad status, **Customer ID**, Campaign, Ad group, Ad type, Headlines 1-15, Descriptions 1-4, Path 1/2, Final URL

### palavras_chave_negativas.csv
- Row Type, Action, Keyword status, **Customer ID**, Level, Campaign, Ad group, Negative keyword, Type

## Ordem de importação
1. campanha.csv
2. grupos_de_anuncio.csv
3. palavras_chave.csv
4. anuncios_rsa.csv
5. palavras_chave_negativas.csv

## Ferramenta preferida
Usar Python com `csv.writer` para evitar erros de formatação manual.
