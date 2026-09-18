#!/usr/bin/env python3
"""
Script para criar draft no Gmail usando Playwright.
Uso: python3 gmail-draft.py --to "email@exemplo.com" --subject "Assunto" --body "Corpo do email"
"""

import argparse
import sys
import time
from playwright.sync_api import sync_playwright


def create_draft(to: str, subject: str, body: str, headless: bool = False):
    """Cria um draft no Gmail."""
    
    with sync_playwright() as p:
        # Conectar ao Chrome existente ou lançar novo
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
            # Navegar para o Gmail
            print("Navegando para o Gmail...")
            page.goto("https://mail.google.com", wait_until="networkidle", timeout=30000)
            time.sleep(3)
            
            # Verificar se precisa fazer login
            if "accounts.google.com" in page.url:
                print("⚠️  Precisa fazer login no Gmail.")
                print("Por favor, faça login manualmente e pressione Enter quando estiver logado.")
                input("Pressione Enter após fazer login...")
                page.wait_for_url("**/mail.google.com/**", timeout=120000)
                time.sleep(3)
            
            print("✅ Logado no Gmail!")
            
            # Clicar no botão "Escrever"
            print("Criando novo e-mail...")
            
            # Tentar diferentes seletores para o botão de escrever
            compose_selectors = [
                'div[role="button"][gh="cm"]',
                'div[role="button"]:has-text("Escrever")',
                'div[role="button"]:has-text("Compose")',
                '.T-I.T-I-KE.L3',
                'div[aria-label="Escrever um novo e-mail"]',
                'div[aria-label="Compose a new email"]',
            ]
            
            compose_clicked = False
            for selector in compose_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        compose_clicked = True
                        print("✅ Janela de composição aberta!")
                        break
                except:
                    continue
            
            if not compose_clicked:
                # Tentar atalho de teclado
                page.keyboard.press("c")
                time.sleep(2)
            
            time.sleep(2)
            
            # Preencher campo "Para"
            to_selectors = [
                'input[aria-label="Para"]',
                'input[aria-label="To"]',
                'input[name="to"]',
                'textarea[name="to"]',
                'input[aria-label="Destinatários"]',
            ]
            
            for selector in to_selectors:
                try:
                    field = page.locator(selector).first
                    if field.is_visible(timeout=2000):
                        field.click()
                        field.fill(to)
                        time.sleep(1)
                        # Pressionar Tab para confirmar o destinatário
                        page.keyboard.press("Tab")
                        time.sleep(0.5)
                        break
                except:
                    continue
            
            # Preencher campo "Assunto"
            subject_selectors = [
                'input[name="subjectbox"]',
                'input[aria-label="Assunto"]',
                'input[aria-label="Subject"]',
                'input[aria-label="Assunto do e-mail"]',
            ]
            
            for selector in subject_selectors:
                try:
                    field = page.locator(selector).first
                    if field.is_visible(timeout=2000):
                        field.click()
                        field.fill(subject)
                        break
                except:
                    continue
            
            # Preencher corpo do email
            body_selectors = [
                'div[aria-label="Corpo da mensagem"]',
                'div[aria-label="Message Body"]',
                'div[role="textbox"][aria-label*="body"]',
                'div[role="textbox"][aria-label*="mensagem"]',
                'div.nH .nH .no .Ar.Au',
                'div.editable',
            ]
            
            for selector in body_selectors:
                try:
                    field = page.locator(selector).first
                    if field.is_visible(timeout=2000):
                        field.click()
                        # Usar paste para preservar formatação
                        page.keyboard.press("Control+Shift+V")
                        # Inserir texto
                        field.fill(body)
                        break
                except:
                    continue
            
            time.sleep(1)
            
            # Salvar como draft (Ctrl+D ou fechar a janela)
            print("Salvando como draft...")
            
            # Tentar fechar a janela (salva automaticamente como draft)
            close_selectors = [
                'div[aria-label="Salvar e fechar"]',
                'div[aria-label="Save & Close"]',
                'img[aria-label="Salvar e fechar"]',
                'div[role="button"][aria-label="Fechar"]',
            ]
            
            draft_saved = False
            for selector in close_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        draft_saved = True
                        break
                except:
                    continue
            
            if not draft_saved:
                # Usar Escape para fechar (salva como draft)
                page.keyboard.press("Escape")
            
            time.sleep(2)
            
            print("✅ Draft criado com sucesso!")
            print(f"   Para: {to}")
            print(f"   Assunto: {subject}")
            print(f"   Corpo: {body[:50]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
            
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="Criar draft no Gmail")
    parser.add_argument("--to", required=True, help="E-mail do destinatário")
    parser.add_argument("--subject", required=True, help="Assunto do e-mail")
    parser.add_argument("--body", required=True, help="Corpo do e-mail")
    parser.add_argument("--headless", action="store_true", help="Rodar em modo headless")
    
    args = parser.parse_args()
    
    success = create_draft(
        to=args.to,
        subject=args.subject,
        body=args.body,
        headless=args.headless
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
