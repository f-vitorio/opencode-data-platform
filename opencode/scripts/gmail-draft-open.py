#!/usr/bin/env python3
"""
Script para abrir Gmail e preparar draft.
Copia o conteúdo do email para a área de transferência e abre o Gmail.
"""

import subprocess
import sys
import os

EMAIL_TO = "vicentbox71@gmail.com"
EMAIL_SUBJECT = "Próximos passos — Landing Page Vicent Box MGA"
EMAIL_BODY = """Olá Fernando,

Tudo bem?

Meu nome é Vitorio, sou responsável pela criação da sua Landing Page.

Para começarmos com o pé direito, preciso de algumas informações sobre o seu trabalho. Isso vai me ajudar a criar uma página que realmente conecta com o seu público e traz resultados.

---

## Sobre o seu negócio

1. Qual é o nome completo do estúdio? "Fernando Serrano Vicentin" é o nome pessoal ou da empresa?

2. Há quanto tempo você atua com treinamento funcional e Pilates?

3. Qual é a localização exata do estúdio (endereço com bairro e cidade)?

4. Você atende presencialmente, online ou ambos?

---

## Público-alvo

5. Quem é seu cliente ideal? (idade, gênero, objetivo principal)

6. Você foca mais em:
   - Pessoas saudáveis que querem manter a forma?
   - Pessoas com doenças crônicas (hipertensão, diabetes)?
   - Pessoas com desvios posturais?
   - Todos os anteriores?

7. Como os clientes chegam até você? (indicação, redes sociais, Google, etc.)

8. Qual é o principal problema que seus clientes trazem quando chegam até você?

---

## Serviços e ofertas

9. Como funcionam as aulas? (individual, dupla, grupo, horários)

10. Você tem planos ou pacotes? Como funciona a cobrança?

11. Existe avaliação inicial antes de começar?

12. Você emite nota fiscal?

---

## Diferenciais

13. O que você diferencia de outros profissionais da região?

14. Você tem certificação ou especialização em doenças crônicas?

15. Trabalha com convênios, planos de saúde ou parcerias com médicos/fisioterapeutas?

---

## Objetivos da Landing Page

16. Qual é o principal objetivo? (captura de leads, agendamento de aula experimental, venda de planos)

17. Qual ação você quer que o visitante realize? (formulário, ligação, WhatsApp, agendamento)

18. Você já tem alguma oferta para colocar na página? (aula experimental, avaliação, desconto)

19. O que faz o cliente escolher você e não outro profissional?

---

## Contato e materiais

20. Qual número de WhatsApp para contato?

21. Qual horário de atendimento?

22. Você tem fotos, vídeos, logotipo ou identidade visual?

23. Quais são os links das suas redes sociais? (Instagram, Facebook, TikTok, YouTube, etc.)

24. Você tem Google Business Profile (Google Meu Negócio)? Se sim, qual é o link?

---

## Prazos

25. Qual é o prazo ideal para ter a Landing Page no ar?

26. Quem tomará as decisões finais sobre conteúdo e design?

---

## Acesso à hospedagem

Para publicar a Landing Page, preciso de acesso à hospedagem do site vicentboxmga.com.br.

Por favor, me informe:

27. Qual é o provedor de hospedagem? (Hostinger, GoDaddy, Locaweb, UOL Host, etc.)

28. Você tem acesso ao painel de controle? Se sim, qual e-mail está cadastrado?

29. Caso não tenha acesso, pode solicitar ao provedor que crie um usuário temporário com as seguintes permissões:
   - Painel de hospedagem
   - Gerenciador de arquivos (File Manager)
   - DNS (se necessário apontar domínio)
   - Banco de dados (se aplicável)

30. O domínio está no mesmo provedor da hospedagem?

31. Existe algo no site atual que precisamos preservar?

**Importante:** Não compartilhe senhas pessoais. Se possível, crie um usuário temporário com acesso limitado.

---

Aguardo suas respostas para darmos continuidade.

Qualquer dúvida, estou à disposição.

Abraço,

Vitorio"""


def copy_to_clipboard(text: str) -> bool:
    """Copia texto para a área de transferência."""
    try:
        # Tentar xclip
        process = subprocess.Popen(
            ["xclip", "-selection", "clipboard"],
            stdin=subprocess.PIPE
        )
        process.communicate(input=text.encode("utf-8"))
        return True
    except FileNotFoundError:
        pass
    
    try:
        # Tentar xsel
        process = subprocess.Popen(
            ["xsel", "--clipboard", "--input"],
            stdin=subprocess.PIPE
        )
        process.communicate(input=text.encode("utf-8"))
        return True
    except FileNotFoundError:
        pass
    
    return False


def open_gmail():
    """Abre o Gmail no navegador padrão."""
    import webbrowser
    webbrowser.open("https://mail.google.com")


def main():
    print("📧 Preparando draft para Fernando Serrano Vicentin...")
    print()
    
    # Copiar corpo do email para área de transferência
    if copy_to_clipboard(EMAIL_BODY):
        print("✅ Corpo do email copiado para a área de transferência!")
    else:
        print("⚠️  Não foi possível copiar para a área de transferência.")
        print("   O conteúdo está salvo em: ~/Documents/Onboarding/email-onboarding.md")
    
    # Abrir Gmail
    print("🌐 Abrindo Gmail...")
    open_gmail()
    
    print()
    print("📋 Instruções:")
    print("   1. Clique em 'Escrever'")
    print(f"   2. Para: {EMAIL_TO}")
    print(f"   3. Assunto: {EMAIL_SUBJECT}")
    print("   4. Cole o corpo do email (Ctrl+V)")
    print("   5. Salve como draft (Ctrl+D ou feche a janela)")
    print()
    print("✅ Draft será salvo automaticamente no Gmail!")


if __name__ == "__main__":
    main()
