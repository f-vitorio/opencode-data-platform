# LP Templates - Biblioteca de Templates Aprovados

Esta skill contem estruturas, blocos de copy e padroes CSS aprovados para reutilizacao em landing pages. Consulte via RAG antes de gerar uma nova pagina.

---

## Templates Disponiveis

### 1. LANDING PAGE SIMPLES - E-commerce / Produtos

**Estrutura:**
```
Header fixo → Hero (badge + H1 + sub + CTA) → Beneficios (3 cards) → Produto (imagem + lista + preco + CTA) → Depoimentos (3 cards) → FAQ (5 itens) → CTA Final → Footer
```

**Paleta:**
- Cor primaria: escolher conforme nicho
- Cor secundaria: complementar
- Fundo claro: #FFFAF0 ou #FFF5E6
- Fundo escuro: #2C2C2C

**Headline formula:** "O [ITEM] Perfeito para Seu [BENEFICIO]"
**Sub-headline:** Descrever o que e em 1 frase
**CTA primario:** "Garanta o Seu Agora" ou "Comprar Agora"
**Badge:** "🔥 Edicao Limitada — Frete Gratis"

**Card de Beneficio:** Emoji grande (3rem) + titulo (1.25rem bold) + descricao (0.95rem cinza)
**Card de Depoimento:** Estrelas (★★★★★) + texto italico + avatar (circle) + nome/cidade

**Item de FAQ:**
- Pergunta: font-weight 600, cursor pointer
- Resposta: max-height animado, oculto por padrao
- Seta: "+" troca para "−" ao abrir

---

### 2. LANDING PAGE SIMPLES - Servicos / Profissionais

**Estrutura:**
```
Header → Hero (H1 + sub + CTA + badge confianca) → Sobre (2 colunas: imagem + texto) → Servicos (3 cards com icone) → Como Funciona (4 passos) → Depoimentos → CTA Final → Footer
```

**Paleta:**
- Profissionais liberais: azul (#1E40AF) + branco
- Saude/medicos: verde (#059669) + branco
- Restaurantes: vermelho (#C41E3A) + dourado (#D4760A)
- Educacao: roxo (#7C3AED) + branco
- Consultoria: cinza escuro (#2C2C2C) + dourado

**Headline formula:** "Seu [PROFISSIONAL] de Confianca em [LOCALIZACAO]"
**Sub:** "Atendimento personalizado com [DIFERENCIAL]"
**CTA:** "Agende sua Consulta" ou "Fale Conosco pelo WhatsApp"
**Badge:** "✓ Atendemos [LOCALIZACAO] e Regiao"

---

### 3. LANDING PAGE COMPLETA - Estrutura Avancada

**Estrutura:**
```
Header → Hero → Problema → Solucao → Beneficios → Prova Social → Depoimentos → Como Funciona → FAQ → CTA Final → Footer
```

**Framework de Copy:** AIDA (Atencao → Interesse → Desejo → Acao)

**Secoes obrigatorias:**
1. Hero: badge + H1 (beneficio+especificidade) + sub + CTA primario
2. Problema: 3 dores do publico + empatia
3. Solucao: apresentar o produto/servico como resposta
4. Beneficios: 4-6 cards com icone + titulo + descricao
5. Prova social: numeros (clientes, avaliacao, tempo)
6. Depoimentos: 3-4 com foto/nome/ocupacao
7. FAQ: 5-8 perguntas com dados estruturados JSON-LD
8. CTA final: urgencia + garantia + botao

---

## Blocos de Copy Aprovados

### Hero - Badge
- "🔥 Edicao Limitada — Frete Gratis"
- "⚡ 50% OFF por tempo limitado"
- "✅ Garantia de 30 dias ou seu dinheiro de volta"
- "⭐ Mais de [NUMERO] clientes satisfeitos"
- "🚚 Entrega gratis para todo o Brasil"

### CTA Primarios
- "Garanta o Seu Agora"
- "Comprar com Frete Gratis"
- "Comece Agora — e Gratis"
- "Agendar Minha Consulta"
- "Fale Conosco pelo WhatsApp"
- "Quero Saber Mais"

### Secao Garantia (HTML padrao)
```html
<div style="display:flex;align-items:center;gap:20px;padding:20px;background:rgba(255,255,255,0.1);border-radius:12px;max-width:500px;margin:25px auto 0">
  <span style="font-size:2.5rem">🛡️</span>
  <div style="text-align:left">
    <strong style="color:var(--laranja-claro);display:block;margin-bottom:3px">Garantia de 30 Dias</strong>
    <span style="color:rgba(255,255,255,0.8);font-size:0.9rem">Nao gostou? Devolvemos 100% do seu dinheiro.</span>
  </div>
</div>
```

### Preco (HTML padrao)
```html
<div class="preco" style="display:flex;align-items:baseline;gap:15px;margin-bottom:25px">
  <span style="font-size:1.1rem;color:var(--cinza-medio);text-decoration:line-through">De R$ XXX</span>
  <span style="font-size:2.8rem;font-weight:800;color:var(--vermelho)">R$ XXX<small>,XX</small></span>
</div>
<p style="font-size:0.95rem;color:var(--cinza-medio)">ou XXx de R$ XX,XX sem juros</p>
```

---

## Paletas CSS por Tema

### Churrasco / Carnes / Gaucha
```css
:root {
  --vermelho: #C41E3A;
  --vermelho-escuro: #8B0000;
  --laranja: #D4760A;
  --laranja-claro: #F4A236;
  --marrom: #5C3317;
  --bege: #FFF5E6;
  --creme: #FFFAF0;
  --cinza-escuro: #2C2C2C;
}
```

### Saude / Medico / Clinica
```css
:root {
  --primaria: #059669;
  --primaria-escuro: #047857;
  --secundaria: #D1FAE5;
  --fundo: #F0FDF4;
  --texto: #1F2937;
  --branco: #FFFFFF;
}
```

### Consultoria / B2B / SaaS
```css
:root {
  --primaria: #1E40AF;
  --primaria-escuro: #1E3A8A;
  --secundaria: #3B82F6;
  --acento: #F59E0B;
  --fundo: #F8FAFC;
  --texto: #1E293B;
  --branco: #FFFFFF;
}
```

### Beleza / Estetica
```css
:root {
  --rosa: #EC4899;
  --rosa-escuro: #BE185D;
  --dourado: #D4AF37;
  --fundo: #FFF5F7;
  --texto: #1F2937;
  --branco: #FFFFFF;
}
```

### Educacao / Cursos / Mentoria
```css
:root {
  --roxo: #7C3AED;
  --roxo-escuro: #5B21B6;
  --lilas: #DDD6FE;
  --fundo: #FAF5FF;
  --texto: #1F2937;
  --branco: #FFFFFF;
}
```

---

## Templates Anteriores Aprovados

### Kit para Churrasco (2026-08-23)
- **Estrutura:** Hero + Beneficios (3) + Kit Completo + Depoimentos (3) + FAQ (5) + CTA Final
- **Paleta:** Vermelho/laranja/marrom (churrasco classico)
- **Diferenciais:** Garantia 30 dias, frete gratis, e-book incluso
- **Arquivo:** ~/Documents/PROJETOS/sites-templates/kit-churrasco.html
- **Status:** Aprovado, funcional, responsivo
