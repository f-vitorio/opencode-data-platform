#!/usr/bin/env python3
"""
Script para enviar mensagem no WhatsApp Web.
Uso: python3 whatsapp-send.py --phone "5511999999999" --message "Mensagem"
"""

import argparse
import sys
import time
import subprocess
import urllib.parse
from playwright.sync_api import sync_playwright


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


def send_whatsapp(phone: str, message: str, headless: bool = False, send: bool = False):
    """Envia mensagem no WhatsApp Web."""
    
    # Limpar número (apenas dígitos)
    phone = ''.join(filter(str.isdigit, phone))
    
    # Adicionar código do país se não tiver
    if len(phone) <= 11:
        phone = '55' + phone
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        
        try:
            # Navegar para WhatsApp Web com mensagem pré-preenchida
            encoded_message = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            
            print(f"Navegando para WhatsApp Web...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            
            # Verificar se precisa escanear QR Code
            if "web.whatsapp.com" in page.url and page.locator('[data-testid="qrcode"]').count() > 0:
                print("⚠️  Precisa escanear o QR Code do WhatsApp.")
                print("   Abra o WhatsApp no celular → Configurações → Dispositivos conectados → Conectar dispositivo")
                print("   Escaneie o QR Code exibido na tela.")
                input("   Pressione Enter após escanear...")
                time.sleep(10)
            
            print("✅ WhatsApp Web conectado!")
            
            # Aguardar carregamento do chat
            time.sleep(3)
            
            # Verificar se a mensagem está pré-preenchida
            message_box = page.locator('[data-testid="conversation-compose-box-input"]')
            if message_box.count() > 0:
                print("✅ Mensagem pré-preenchida!")
                
                if send:
                    # Clicar no botão enviar
                    send_btn = page.locator('[data-testid="send"]')
                    if send_btn.count() > 0:
                        send_btn.click()
                        print("✅ Mensagem enviada!")
                    else:
                        print("⚠️  Botão de envio não encontrado. Envie manualmente com Enter.")
                else:
                    print("📋 Mensagem pronta. Pressione Enter para enviar ou feche a janela.")
            else:
                print("⚠️  Caixa de mensagem não encontrada.")
            
            # Manter navegador aberto
            if not headless:
                print("\n⏳ Navegador aberto. Feche manualmente quando terminar.")
                time.sleep(300)  # Manter por 5 minutos
            
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="Enviar mensagem no WhatsApp Web")
    parser.add_argument("--phone", required=True, help="Número de telefone com código do país")
    parser.add_argument("--message", required=True, help="Mensagem a enviar")
    parser.add_argument("--headless", action="store_true", help="Rodar em modo headless")
    parser.add_argument("--send", action="store_true", help="Enviar automaticamente")
    
    args = parser.parse_args()
    
    success = send_whatsapp(
        phone=args.phone,
        message=args.message,
        headless=args.headless,
        send=args.send
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
