#!/usr/bin/env python3
"""
Script para preparar mensagem no WhatsApp.
Copia a mensagem e abre o WhatsApp Web com o contato.
"""

import subprocess
import sys
import os
import webbrowser
import urllib.parse


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
    return False


def open_whatsapp(phone: str, message: str):
    """Abre WhatsApp Web com mensagem pré-preenchida."""
    # Limpar número
    phone = ''.join(filter(str.isdigit, phone))
    
    # Adicionar código do país se não tiver
    if len(phone) <= 11:
        phone = '55' + phone
    
    encoded_message = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
    webbrowser.open(url)


def main():
    # Mensagem para o Fernando
    PHONE = "554499218147"  # Número do Fernando
    
    MESSAGE = """Olá Fernando!

Meu nome é Vitorio, da equipe que está criando sua Landing Page.

Para darmos continuidade, preciso de algumas informações sobre o seu trabalho. Enviei um e-mail com todas as perguntas (vicentbox71@gmail.com).

Você pode responder por aqui mesmo ou pelo e-mail, como preferir!

Abraço,
Vitorio"""
    
    print("📱 Preparando mensagem para Fernando Serrano Vicentin...")
    print()
    
    # Copiar mensagem para área de transferência
    if copy_to_clipboard(MESSAGE):
        print("✅ Mensagem copiada para a área de transferência!")
    else:
        print("⚠️  Não foi possível copiar para a área de transferência.")
    
    # Abrir WhatsApp Web
    print("🌐 Abrindo WhatsApp Web...")
    open_whatsapp(PHONE, MESSAGE)
    
    print()
    print("📋 Instruções:")
    print("   1. Escaneie o QR Code se necessário")
    print("   2. A mensagem já está pré-preenchida")
    print("   3. Pressione Enter para enviar")
    print()
    print("✅ Pronto!")


if __name__ == "__main__":
    main()
