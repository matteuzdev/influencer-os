"""
Google Flow Copilot // Sessão Interativa com Playwright
Abre o Chrome real na tela do usuário, aguarda o login com tranquilidade,
e fica pronto para gerar imagens e vídeos automaticamente.
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / ".chrome-influencer-profile"
FLOW_URL = "https://labs.google/fx/tools/image-fx"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_flow_session(prompt_to_generate: str = None, aspect_ratio: str = "9:16"):
    print("=" * 60)
    print("[*] GOOGLE FLOW COPILOT INICIADO")
    print(f"[*] Perfil: {PROFILE_DIR}")
    print("=" * 60)

    with sync_playwright() as p:
        # Lança o Google Chrome instalado nativamente no Windows
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                channel="chrome",
                viewport={"width": 1400, "height": 900},
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized"
                ]
            )
        except Exception as e:
            print(f"[!] Erro ao usar channel='chrome', tentando Chromium padrão: {e}")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                viewport={"width": 1400, "height": 900},
                args=["--disable-blink-features=AutomationControlled"]
            )

        page = context.pages[0] if context.pages else context.new_page()
        print(f"[*] Abrindo página: {FLOW_URL}...")
        page.goto(FLOW_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)

        # Loop de verificação de login
        logged_in = False
        print("\n[*] Monitorando estado da página no Chrome...")
        
        for i in range(120): # até 6 minutos para login com calma
            url = page.url
            title = page.title()
            
            # Detecta se está na tela de login
            is_login_screen = (
                "accounts.google.com" in url or 
                bool(page.query_selector("input[type='email'], input[name='identifier']"))
            )
            
            # Detecta se está na interface do ImageFX / Flow
            has_prompt_input = bool(page.query_selector(
                "textarea, input[placeholder*='prompt'], [contenteditable='true'], [aria-label*='prompt']"
            ))
            
            if has_prompt_input and not is_login_screen:
                logged_in = True
                print("\n" + "="*60)
                print("[+] SUCESSO: VOCÊ ESTÁ LOGADO NO GOOGLE FLOW / IMAGEFX!")
                print("="*60 + "\n")
                break
                
            if is_login_screen:
                if i % 5 == 0:
                    print(f"[*] [Aguardando Login] Por favor, insira seu email/senha na janela aberta do Chrome... ({i*3}s)")
            else:
                # Pode estar carregando termos de uso ou splash screen
                terms_btn = page.query_selector("button:has-text('I agree'), button:has-text('Concordo'), button:has-text('Aceitar'), button:has-text('Sign in')")
                if terms_btn and terms_btn.is_visible():
                    print("[*] Clicando em botão de confirmação/termos...")
                    terms_btn.click()
                    
            page.wait_for_timeout(3000)

        if not logged_in:
            print("[!] Tempo de espera esgotado ou login ainda não finalizado.")
            return False

        # Se houver prompt para gerar, executa agora!
        if prompt_to_generate:
            print(f"[*] Inserindo prompt mestre na interface...")
            prompt_input = page.query_selector(
                "textarea, input[placeholder*='prompt'], [contenteditable='true'], [aria-label*='prompt']"
            )
            if prompt_input:
                prompt_input.click()
                prompt_input.fill(prompt_to_generate)
                page.wait_for_timeout(1000)
                
                # Seleciona proporção vertical 9:16 se disponível
                ratio_btn = page.query_selector("button:has-text('9:16'), button:has-text('Vertical'), [aria-label*='9:16']")
                if ratio_btn:
                    print("[*] Selecionando proporção 9:16...")
                    ratio_btn.click()
                    page.wait_for_timeout(500)

                # Clica em Gerar
                gen_btn = page.query_selector("button:has-text('Generate'), button:has-text('Create'), button:has-text('Criar'), button[type='submit']")
                if gen_btn and gen_btn.is_enabled():
                    print("[+] Clicando no botão GERAR!")
                    gen_btn.click()
                else:
                    print("[*] Pressionando Enter para gerar...")
                    prompt_input.press("Enter")

                print("[*] Aguardando geração da imagem (15s)...")
                page.wait_for_timeout(15000)
                
                # Salva screenshot da tela como comprovação
                screenshot_path = OUTPUT_DIR / "flow_generation_live.png"
                page.screenshot(path=str(screenshot_path))
                print(f"[+] Screenshot da tela salvo em: {screenshot_path}")

        print("[*] Mantendo navegador aberto por mais 30 segundos para visualização...")
        page.wait_for_timeout(30000)
        context.close()
        return True

if __name__ == "__main__":
    import sys
    p_text = sys.argv[1] if len(sys.argv) > 1 else None
    run_flow_session(p_text)
