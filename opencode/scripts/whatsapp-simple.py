#!/usr/bin/env python3
"""
WhatsApp Simples - Abre com mensagem pré-preenchida.
Não precisa interagir com a página.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
import time

# CONFIGURAÇÃO
TELEFONE = "554499218147"  # Número do Caio
MENSAGEM = """Bom dia, Caio! ☀️

Tudo bem?

Aqui é o Vitorio, da FVS7 Growth.

Espero que esteja tendo uma ótima semana!

Abraço,
Vitorio"""

def main():
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
        print("   Aguarde o carregamento e pressione Enter no navegador para enviar.")
        
        # Manter aberto
        input("\nPressione Enter aqui para fechar...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
