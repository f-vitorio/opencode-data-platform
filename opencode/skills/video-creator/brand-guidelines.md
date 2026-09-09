# FVS7 Growth - Brand Guidelines

## IDENTIDADE VISUAL

### Nome
**FVS7 Growth Engineering**

### Tagline
"Google Ads e Landing Pages que Transformam Cliques em Clientes"

### Proposta de Valor
Especialistas em conversão. Criamos e gerenciamos campanhas de Google Ads e desenvolvemos landing pages estratégicas para transformar tráfego pago em leads e oportunidades reais de venda.

---

## CORES

### Paleta Principal

| Cor | Código | Uso |
|-----|--------|-----|
| Azul Escuro | `#1a1a2e` | Fundo principal |
| Azul Marinho | `#16213e` | Fundo secundário |
| Azul Médio | `#0f3460` | Destaques, botões |
| Vermelho | `#e94560` | Acento, CTA urgente |
| Branco | `#ffffff` | Texto principal |
| Amarelo | `#FFD700` | URL do site, destaque |

### Gradiente
```
Background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)
CTA: linear-gradient(90deg, #e94560 0%, #ff6b6b 100%)
```

### Uso das Cores
- **Fundo de vídeo**: Azul escuro (#1a1a2e) ou gradiente
- **Texto principal**: Branco (#ffffff)
- **Texto de destaque**: Amarelo (#FFD700)
- **CTA e urgência**: Vermelho (#e94560)
- **Elementos gráficos**: Azul médio (#0f3460)

---

## TIPOGRAFIA

### Fontes Recomendadas
- **Títulos**: Montserrat Bold (ou DejaVu Sans Bold)
- **Corpo**: Inter Regular (ou DejaVu Sans)
- **Código/URL**: Monospace

### Tamanhos para Vídeo 9:16 (1080x1920)

| Elemento | Tamanho | Cor | Posição |
|----------|---------|-----|---------|
| Texto principal | 48px | Branco | Centro, y=1350 |
| Marca (inferior) | 32px | Branco 90% | Centro, y=1780 |
| URL (inferior) | 36px | Amarelo | Centro, y=1840 |

### Estilo de Texto
```css
/* Marca no topo */
text-brand {
  font-size: 32px;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

/* Texto do roteiro */
text-body {
  font-size: 48px;
  color: #ffffff;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9);
  border: 2px solid rgba(0, 0, 0, 0.4);
}

/* URL do site */
text-url {
  font-size: 36px;
  color: #FFD700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9);
}
```

---

## ELEMENTOS VISUAIS

### Logo/Texto da Marca
- **Texto**: "FVS7 MARKETING DIGITAL"
- **Posição**: Inferior centralizado
- **Estilo**: Branco, sombra sutil
- **Tamanho**: 32px

### URL do Site
- **Texto**: "www.fvs7.com.br"
- **Posição**: Inferior centralizado (abaixo da marca)
- **Estilo**: Amarelo (#FFD700), sombra escura
- **Tamanho**: 36px

### Fundo
- **Cor sólida**: Azul escuro (#1a1a2e)
- **Gradiente**: Opcional, mais profissional
- **Imagem**: Semi-transparente (30-40% opacidade)

---

## IMAGENS

### Estilo
- Profissional, corporativo
- Ambientes modernos, limpos
- Pessoas em contexto de trabalho
- Tecnologia: laptops, dashboards, telas

### Evitar
- Gráficos financeiros/marketplace
- Imagens genéricas de estoque
- Pessoas em poses artificiais
- Fundos cluttered ou coloridos

### Queries de Busca por Nicho

| Nicho | Query Pexels |
|-------|--------------|
| Marketing Digital | `digital marketing analytics dashboard laptop screen` |
| Google Ads | `google ads advertising analytics laptop office` |
| SEO | `seo search engine optimization laptop analytics` |
| Clínicas | `modern clinic reception patient appointment digital` |
| Advogados | `lawyer office professional client meeting modern` |
| Contadores | `accountant office calculator laptop financial` |
| Landing Pages | `landing page website conversion laptop screen` |
| Gestão de Tráfego | `traffic management advertising dashboard laptop` |
| Conversão | `conversion rate optimization analytics dashboard` |
| Leads | `lead generation crm dashboard laptop` |

---

## NARRAÇÃO

### Voz Recomendada
- **ElevenLabs**: Adam (pNInz6obpgDQGcFmaJgB)
- **Idioma**: Português do Brasil
- **Modelo**: eleven_multilingual_v2

### Voice Settings
```json
{
  "stability": 0.5,
  "similarity_boost": 0.75
}
```

### Estilo de Fala
- Tom profissional, mas acessível
- Ritmo moderado (não rápido demais)
- Ênfase em palavras-chave
- Pausas naturais entre segmentos

---

## ESTRUTURA DE VÍDEO

### Layout 9:16 (1080x1920)

```
┌─────────────────────────┐
│                         │
│                         │
│                         │
│    [TEXTO DO ROTEIRO]   │  ← y=1350, 48px, branco
│                         │
│                         │
│   FVS7 MARKETING DIGITAL│  ← y=1780, 32px, branco
│     www.fvs7.com.br     │  ← y=1840, 36px, amarelo
└─────────────────────────┘
```

### Elementos por Camada

1. **Fundo**: Imagem com Ken Burns + overlay escuro
2. **Texto**: Legendas do roteiro
3. **Branding**: Nome da marca na parte inferior
4. **CTA**: URL na parte inferior

---

## TOM DE VOZ

### Para Vídeos
- **Direto**: Vá direto ao ponto
- **Benefício**: Fale o que o cliente ganha
- **Prova**: Números e resultados
- **CTA**: Ação clara e simples

### Exemplos

**Bom**:
> "Seu anúncio pode gerar o clique. Sua página precisa gerar o resultado."

**Ruim**:
> "Nós somos uma empresa especializada em marketing digital com mais de 10 anos de experiência."

---

## CHECKLIST ANTES DE PUBLICAR

- [ ] Texto da marca "FVS7 MARKETING DIGITAL" visível na parte inferior?
- [ ] URL "www.fvs7.com.br" visível na parte inferior?
- [ ] Imagens relevantes para o nicho?
- [ ] Narração clara e sem erros?
- [ ] Legendas corretas e legíveis?
- [ ] Duração adequada (30-90s)?
- [ ] CTA claro no último segmento?
- [ ] Formato 9:16 (vertical)?
- [ ] Qualidade de vídeo boa (1080p)?
