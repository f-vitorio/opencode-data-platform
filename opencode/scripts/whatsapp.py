#!/usr/bin/env python3
"""
WhatsApp Web - Script completo com parâmetros.
Uso: python3 whatsapp.py --phone "4499218147" --message "Olá!"
"""

import argparse
import sys
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def main():
    parser = argparse.ArgumentParser(description="Enviar mensagem no WhatsApp Web")
    parser.add_argument("--phone", "-p", required=True, help="Número com DDD (ex: 4499218147)")
    parser.add_argument("--message", "-m", help="Mensagem a enviar")
    parser.add_argument("--file", "-f", help="Arquivo com a mensagem")
    parser.add_argument("--template", "-t", help="Nome do template (onboarding, proposta, followup)")
    parser.add_argument("--nome", "-n", help="Nome do contato (para templates)")
    
    args = parser.parse_args()
    
    # Carregar mensagem
    message = args.message
    
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            message = f.read()
    
    if args.template:
        templates = {
            "onboarding": """Olá {nome}!

Meu nome é Vitorio, da FVS7 Growth.

{mensagem}

Se tiver alguma dúvida, é só me chamar!

Abraço,
Vitorio""",
            
            "proposta": """Olá {nome}!

Segue a proposta conforme combinamos.

{mensagem}

Qualquer dúvida, estou à disposição!

Abraço,
Vitorio""",
            
            "followup": """Olá {nome}!

Aqui é o Vitorio da FVS7 Growth.

{mensagem}

Fico no aguardo!

Abraço,
Vitorio""",
        }
        
        if args.template in templates:
            message = templates[args.template]
            if args.nome:
                message = message.replace("{nome}", args.nome)
        else:
            print(f"❌ Template '{args.template}' não encontrado.")
            print(f"   Templates disponíveis: {', '.join(templates.keys())}")
            sys.exit(1)
    
    if not message:
        print("❌ Especifique --message, --file ou --template")
        sys.exit(1)
    
    # Formatar telefone
    phone = ''.join(filter(str.isdigit, args.phone))
    if len(phone) <= 11:
        phone = '55' + phone
    
    print(f"📱 Enviando mensagem para {phone}...")
    print(f"   Mensagem: {message[:50]}...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    # Instalar ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Codificar mensagem para URL
        encoded_message = urllib.parse.quote(message)
        
        # Abrir WhatsApp com mensagem pré-preenchida
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        driver.get(url)
        
        print("✅ WhatsApp Web aberto!")
        print("   Aguarde o carregamento.")
        print("   Pressione Enter no navegador para enviar.")
        
        # Manter aberto
        input("\nPressione Enter aqui para fechar...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
