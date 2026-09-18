#!/usr/bin/env python3
"""
WhatsApp com Selenium - Versão simplificada.
Uso: python3 whatsapp-selenium.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# CONFIGURAÇÃO
CONTATO = "Caio Vitorio"
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
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Instalar ChromeDriver automaticamente
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Abrir WhatsApp Web
        driver.get("https://web.whatsapp.com")
        
        print("⏳ Aguardando carregamento (20s)...")
        time.sleep(20)
        
        # Verificar se precisa de QR Code
        try:
            driver.find_element(By.XPATH, '//*[@data-testid="qrcode"]')
            print("⚠️  Escaneie o QR Code!")
            input("   Pressione Enter após escanear...")
            time.sleep(15)
        except:
            print("✅ WhatsApp conectado!")
        
        # Buscar contato usando atalho
        print(f"🔍 Buscando {CONTATO}...")
        
        # Usar Ctrl+F para buscar
        search_input = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        search_input.click()
        time.sleep(1)
        
        # Digitar nome do contato
        search_input.send_keys(CONTATO)
        time.sleep(3)
        
        # Tentar encontrar e clicar no contato
        try:
            # Procurar por qualquer elemento com o nome do contato
            contact = driver.find_element(By.XPATH, f'//span[contains(text(), "{CONTATO}")]')
            contact.click()
            time.sleep(2)
        except:
            # Tentar outro seletor
            try:
                contact = driver.find_element(By.XPATH, f'//div[contains(@title, "{CONTATO}")]')
                contact.click()
                time.sleep(2)
            except:
                print(f"❌ Contato '{CONTATO}' não encontrado.")
                print("   Verifique se o nome está correto.")
                return
        
        # Encontrar caixa de mensagem
        print("✍️  Escrevendo mensagem...")
        
        # Procurar por div contenteditable que é a caixa de mensagem
        message_boxes = driver.find_elements(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
        if not message_boxes:
            message_boxes = driver.find_elements(By.XPATH, '//div[@contenteditable="true"][@role="textbox"]')
        
        if message_boxes:
            message_box = message_boxes[0]
            message_box.click()
            time.sleep(0.5)
            
            # Digicionar mensagem
            for line in MENSAGEM.split('\n'):
                message_box.send_keys(line)
                message_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            print("✅ Mensagem escrita!")
            print("   Revise no navegador e pressione Enter para enviar.")
        else:
            print("❌ Caixa de mensagem não encontrada.")
        
        # Manter aberto
        input("\nPressione Enter aqui para fechar o navegador...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
