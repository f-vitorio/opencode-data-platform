#!/usr/bin/env python3
"""
Script para enviar mensagem no WhatsApp Web para o Caio Vitorio.
"""

import subprocess
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


def main():
    # Contato
    CONTACT = "Caio Vitorio"
    PHONE = "55"  # Adicionar número do Caio aqui
    
    # Mensagem de teste
    MESSAGE = f"""Olá Caio!

Meu nome é Vitorio, da FVS7 Growth.

Estou entrando em contato para apresentar nossos serviços de marketing digital.

Podemos conversar quando puder?

Abraço,
Vitorio"""
    
    print(f"📱 Preparando mensagem para {CONTACT}...")
    print()
    
    # Copiar mensagem para área de transferência
    if copy_to_clipboard(MESSAGE):
        print("✅ Mensagem copiada para a área de transferência!")
    else:
        print("⚠️  Não foi possível copiar para a área de transferência.")
    
    # Abrir WhatsApp Web
    print("🌐 Abrindo WhatsApp Web...")
    
    # Limpar número
    phone = ''.join(filter(str.isdigit, PHONE))
    if len(phone) <= 11:
        phone = '55' + phone
    
    encoded_message = urllib.parse.quote(MESSAGE)
    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
    webbrowser.open(url)
    
    print()
    print("📋 Instruções:")
    print("   1. Escaneie o QR Code se necessário")
    print("   2. Selecione o contato Caio Vitorio")
    print("   3. A mensagem já está pré-preenchida")
    print("   4. Pressione Enter para enviar")
    print()
    print("✅ Pronto!")


if __name__ == "__main__":
    main()
