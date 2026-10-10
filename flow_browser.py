"""
Flow Browser & Copilot // Controle Interativo do Google ImageFX / Flow
Abre o Chrome real na tela do usuário para login Google sem bloqueios
e permite ao Orion/Playwright controlar e gerar diretamente na tela.
"""
import os
import subprocess
import time
from pathlib import Path
from typing import Optional, List
import requests
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = Path.home() / ".chrome-influencer-profile"
CDP_PORT = 9222
CDP_URL = f"http://127.0.0.1:{CDP_PORT}"
FLOW_URL = "https://labs.google/fx/tools/image-fx"

def is_cdp_ready() -> bool:
    try:
        r = requests.get(f"{CDP_URL}/json/version", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

def launch_chrome_flow():
    """
    Abre o Google Chrome real visível na tela com perfil dedicado e porta de depuração.
    """
    if is_cdp_ready():
        print(f"[*] Chrome já está rodando e conectado na porta {CDP_PORT}!")
        return True

    print(f"[*] Iniciando Google Chrome em: {CHROME_PATH}")
    print(f"[*] Perfil: {PROFILE_DIR}")
    print(f"[*] URL: {FLOW_URL}")
    
    cmd = [
        CHROME_PATH,
        f"--user-data-dir={PROFILE_DIR}",
        f"--remote-debugging-port={CDP_PORT}",
        "--no-first-run",
        "--no-default-browser-check",
        FLOW_URL
    ]
    
    proc = subprocess.Popen(cmd)
    
    # Aguarda o CDP ficar pronto
    for _ in range(15):
        time.sleep(1)
        if is_cdp_ready():
            print("[+] Chrome iniciado e pronto para automação!")
            return True
            
    print("[!] Chrome iniciado, aguardando conexão CDP...")
    return True

def get_flow_status() -> dict:
    """
    Inspeciona a página aberta via Playwright CDP.
    """
    if not is_cdp_ready():
        return {"status": "closed", "message": "Chrome não está rodando na porta 9222."}
        
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
            context = browser.contexts[0]
            pages = context.pages
            
            flow_page = None
            for page in pages:
                if "labs.google" in page.url or "accounts.google" in page.url or "google.com" in page.url:
                    flow_page = page
                    break
                    
            if not flow_page:
                flow_page = pages[0] if pages else None
                
            if not flow_page:
                return {"status": "no_pages", "message": "Nenhuma aba encontrada."}
                
            url = flow_page.url
            title = flow_page.title()
            
            is_login = "accounts.google.com" in url or bool(flow_page.query_selector("input[type='email'], a[href*='accounts.google']"))
            is_flow_ready = "image-fx" in url and not is_login
            
            return {
                "status": "ready" if is_flow_ready else ("login_needed" if is_login else "loading"),
                "url": url,
                "title": title,
                "is_login": is_login,
                "is_flow_ready": is_flow_ready
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    launch_chrome_flow()
    time.sleep(2)
    status = get_flow_status()
    print("Status atual:", status)
