#!/usr/bin/env python3
"""
WhatsApp Web - Mantém navegador aberto.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
import time
import signal
import sys

# CONFIGURAÇÃO
TELEFONE = "554499218147"
MENSAGEM = """Bom dia, Caio! ☀️

Tudo bem?

Aqui é o Vitorio, da FVS7 Growth.

Espero que esteja tendo uma ótima semana!

Abraço,
Vitorio"""

def signal_handler(sig, frame):
    print("\n👋 Fechando navegador...")
    sys.exit(0)

def main():
    # Tratar Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🚀 Abrindo WhatsApp Web...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    # Instalar ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Codificar mensagem para URL
        encoded_message = urllib.parse.quote(MENSAGEM)
        
        # Abrir WhatsApp com mensagem pré-preenchida
        url = f"https://web.whatsapp.com/send?phone={TELEFONE}&text={encoded_message}"
        driver.get(url)
        
        print("✅ WhatsApp Web aberto!")
        print(f"   Mensagem para: {TELEFONE}")
        print("   Aguarde o carregamento.")
        print("   Pressione Enter no navegador para enviar.")
        print("   Feche esta janela para encerrar.")
        
        # Manter aberto indefinidamente
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n👋 Fechando...")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
