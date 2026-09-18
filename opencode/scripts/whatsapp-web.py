#!/usr/bin/env python3
"""
Script para enviar mensagens no WhatsApp Web.
Permite enviar mensagens para contatos do WhatsApp ou do CRM.

Uso:
  # Enviar para um contato específico
  python3 whatsapp-web.py --to "Caio Vitorio" --message "Olá, tudo bem?"
  
  # Listar contatos recentes do WhatsApp
  python3 whatsapp-web.py --list-contacts
  
  # Enviar mensagem personalizada de onboarding
  python3 whatsapp-web.py --to "Fernando" --template "onboarding"
"""

import argparse
import sys
import time
import subprocess
import urllib.parse
import json
import os
from pathlib import Path
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


def load_templates():
    """Carrega templates de mensagens."""
    templates_dir = Path.home() / ".config" / "opencode" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    templates = {
        "onboarding": """Olá {nome}!

Meu nome é Vitorio, da equipe FVS7 Growth.

{mensagem}

Se tiver alguma dúvida, é só me chamar!

Abraço,
Vitorio""",
        
        "followup": """Olá {nome}!

Aqui é o Vitorio da FVS7 Growth.

{mensagem}

Fico no aguardo!

Abraço,
Vitorio""",
        
        "proposta": """Olá {nome}!

Segue a proposta conforme combinamos.

{mensagem}

Qualquer dúvida, estou à disposição!

Abraço,
Vitorio""",
    }
    
    # Carregar templates customizados
    for template_file in templates_dir.glob("*.txt"):
        templates[template_file.stem] = template_file.read_text(encoding="utf-8")
    
    return templates


def send_whatsapp_message(phone: str, message: str, contact_name: str = "", headless: bool = False):
    """Envia mensagem no WhatsApp Web."""
    
    # Limpar número
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
            
            print(f"📱 Enviando mensagem para {contact_name or phone}...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            
            # Verificar se precisa escanear QR Code
            if page.locator('[data-testid="qrcode"]').count() > 0:
                print("⚠️  Precisa escanear o QR Code do WhatsApp.")
                print("   Abra o WhatsApp no celular → Configurações → Dispositivos conectados → Conectar dispositivo")
                input("   Pressione Enter após escanear...")
                time.sleep(10)
            
            # Verificar se a mensagem está pré-preenchida
            message_box = page.locator('[data-testid="conversation-compose-box-input"]')
            if message_box.count() > 0:
                print("✅ Mensagem pré-preenchida!")
                print("   Pressione Enter para enviar ou feche a janela.")
            else:
                print("⚠️  Caixa de mensagem não encontrada.")
            
            # Manter navegador aberto
            if not headless:
                time.sleep(300)  # Manter por 5 minutos
            
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="Enviar mensagem no WhatsApp Web")
    parser.add_argument("--to", help="Nome ou número do contato")
    parser.add_argument("--phone", help="Número de telefone (override)")
    parser.add_argument("--message", help="Mensagem a enviar")
    parser.add_argument("--template", help="Nome do template para usar")
    parser.add_argument("--nome", help="Nome do contato para templates")
    parser.add_argument("--list-templates", action="store_true", help="Listar templates disponíveis")
    
    args = parser.parse_args()
    
    # Listar templates
    if args.list_templates:
        templates = load_templates()
        print("📋 Templates disponíveis:")
        for name, content in templates.items():
            print(f"\n--- {name} ---")
            print(content[:100] + "..." if len(content) > 100 else content)
        return
    
    if not args.to and not args.phone:
        parser.error("Especifique --to ou --phone")
    
    # Carregar templates
    templates = load_templates()
    
    # Preparar mensagem
    message = args.message
    if args.template and args.template in templates:
        message = templates[args.template]
        if args.nome:
            message = message.replace("{nome}", args.nome)
    
    if not message:
        parser.error("Especifique --message ou --template")
    
    # Número do contato
    phone = args.phone or args.to
    
    # Enviar mensagem
    success = send_whatsapp_message(
        phone=phone,
        message=message,
        contact_name=args.to,
        headless=False
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
