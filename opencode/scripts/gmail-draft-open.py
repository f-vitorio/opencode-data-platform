#!/usr/bin/env python3
"""
Script para abrir Gmail e preparar draft.
Copia o conteúdo do email para a área de transferência e abre o Gmail.
"""

import subprocess
import sys
import os

EMAIL_TO = "vicentbox71@gmail.com"
EMAIL_SUBJECT = "VicentBOX — acesso à hospedagem, fotos e reviews para publicar o site"
EMAIL_BODY = """Olá Fernando,

Tudo bem?

Aqui é o Vitorio, da FVS7 Growth.

O site da VicentBOX está pronto e na fase final de validação. Para publicar no ar e deixar a página com a cara real do seu studio, preciso de 3 coisas sua parte:

---

## 1) Acesso à hospedagem (Hostinger)

Para subir o site, preciso de acesso ao painel/File Manager da Hostinger onde o domínio vicentbox.com.br está hospedado.

Você pode me enviar:

- Hospedagem: host, usuário FTP e senha FTP
  (ou, se preferir, login do hPanel)

Caso não queira compartilhar uma senha pessoal:

- Crie um usuário FTP temporário no hPanel
  (hPanel > Arquivos > Conta FTP)
- Ou me envie um convite de acesso do hPanel para o meu e-mail

**Importante:** não envie a senha da sua conta principal do e-mail ou do banco. Se for criar um acesso dedicado, pode limitar as permissões ao diretório do site.

---

## 2) Fotos reais do studio

Hoje o site está com imagens ilustrativas (banco de imagens). Fotos reais do seu espaço aumentam muito a confiança e a taxa de conversão.

Ideal enviar de 8 a 12 fotos:

- Fachada / entrada do studio
- Ambiente de treino (equipamentos, espaço)
- Sessão em andamento (com autorização dos alunos, se possível)
- Detalhes que mostrem o cuidado (estacionamento, vestiário, recepção)

Formato: JPG ou PNG, horizontal, o mais nítida possível (mínimo ~1200px de largura).

Pode mandar por aqui mesmo ou me encaminhar um link (Google Fotos / Drive).

---

## 3) Prints das avaliações no WhatsApp

Para publicar depoimentos reais no site, me envie capturas de tela das avaliações que seus alunos deixam no WhatsApp.

Cada print deve mostrar:

- Nome (ou como o aluno se identifica)
- O texto do elogio
- A data, se possível

Se tiver também prints de comentários no Instagram ou Facebook, também ajuda.

---

## 2 confirmações rápidas

Para manter o conteúdo 100% correto antes de publicar:

1. **Domínio:** o endereço oficial do site é vicentbox.com.br, certo? (no contrato/onboarding anterior aparecia também vicentboxmga.com.br — só confirmar qual usamos)

2. **19 anos de mercado:** você mencionou "19 anos de atuação" no onboarding. Posso usar essa informação na página Sobre?

---

Com o acesso da hospedagem eu publico o site; com fotos e reviews eu troco as imagens ilustrativas e publico os depoimentos reais.

Qualquer dúvida, me chama no WhatsApp (44) 99921-8147 ou responde por aqui.

Abraço,

Vitorio
FVS7 Growth"""


def copy_to_clipboard(text: str) -> bool:
    """Copia texto para a área de transferência."""
    try:
        process = subprocess.Popen(
            ["xclip", "-selection", "clipboard"],
            stdin=subprocess.PIPE
        )
        process.communicate(input=text.encode("utf-8"))
        return True
    except FileNotFoundError:
        pass

    try:
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

    if copy_to_clipboard(EMAIL_BODY):
        print("✅ Corpo do email copiado para a área de transferência!")
    else:
        print("⚠️  Não foi possível copiar para a área de transferência.")

    print("🌐 Abrindo Gmail...")
    open_gmail()

    print()
    print("📋 Como finalizar o draft:")
    print(f"   1. Gmail abriu janela 'Nova mensagem' para {EMAIL_TO}")
    print(f"   2. Assunto: {EMAIL_SUBJECT}")
    print("   3. Corpo já preenchido (se vazio, cole com Ctrl+V — está no clipboard)")
    print("   4. Feche a janela de composição (Gmail salva automaticamente em Rascunhos)")
    print()


if __name__ == "__main__":
    main()
