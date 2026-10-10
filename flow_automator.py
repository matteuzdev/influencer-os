"""
Automação de Geração de Imagens via Playwright no Google ImageFX / Flow.
Permite executar a geração em proporção 9:16 mantendo a sessão persistente do usuário.
"""
import subprocess
import time
from pathlib import Path
from typing import List, Optional
from config import CHROME_PROFILE_DIR, IMAGE_FX_URL, OUTPUT_DIR

def copy_to_clipboard(text: str) -> None:
    """
    Copia o texto para a área de transferência usando o clip.exe nativo do Windows.
    """
    try:
        subprocess.run(
            ["clip.exe"],
            input=text.encode("utf-8", errors="ignore"),
            check=True,
            timeout=3
        )
        print("[+] Prompt copiado para a área de transferência do Windows!")
    except Exception as e:
        print(f"[!] Não foi possível copiar para o clipboard: {e}")

def run_imagefx_automation(
    prompt_text: str,
    aspect_ratio: str = "9:16",
    headless: bool = False,
    timeout_sec: int = 60
) -> List[Path]:
    """
    Inicia o navegador com perfil persistente para acessar o Google ImageFX,
    insere o prompt, seleciona a proporção vertical (9:16) e dispara a geração.
    """
    print("\n" + "="*60)
    print("[*] INICIANDO AUTOMAÇÃO NO GOOGLE IMAGEFX / FLOW")
    print(f"[*] Perfil persistente: {CHROME_PROFILE_DIR}")
    print("="*60)

    # Copia o prompt para facilitar caso o usuário queira colar manualmente
    copy_to_clipboard(prompt_text)
    saved_images: List[Path] = []

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        # Lança Chromium com o perfil persistente para reter o login Google
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE_DIR),
            headless=headless,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        print(f"[*] Acessando {IMAGE_FX_URL}...")
        page.goto(IMAGE_FX_URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(3000)

        # Verifica se caiu em tela de login
        if "accounts.google.com" in page.url or page.query_selector("a[href*='accounts.google.com'], button:has-text('Sign in')"):
            print("\n[!] ATENÇÃO: É necessário fazer login na sua conta Google.")
            print("[!] A janela do navegador está aberta na sua tela. Faça o login para prosseguir.")
            print("[!] Suas credenciais ficarão salvas neste perfil para as próximas gerações automáticas.\n")
            
            # Aguarda o login completar até voltar para a URL do labs
            page.wait_for_url("**/fx/**", timeout=120000)
            print("[+] Login detectado com sucesso!")
            page.wait_for_timeout(3000)

        # Procura campo de entrada de prompt (textarea ou input de texto do ImageFX)
        prompt_selectors = [
            "textarea",
            "input[type='text']",
            "[contenteditable='true']",
            "[placeholder*='prompt']",
            "[aria-label*='prompt']"
        ]
        
        input_el = None
        for sel in prompt_selectors:
            el = page.query_selector(sel)
            if el and el.is_visible():
                input_el = el
                break

        if input_el:
            print("[*] Preenchendo prompt mestre gerado pelo MIRR0R...")
            input_el.click()
            input_el.fill(prompt_text)
            page.wait_for_timeout(1000)
            
            # Tenta selecionar aspect ratio se houver botão (ex: 9:16 ou vertical)
            aspect_btn = page.query_selector("button:has-text('9:16'), button:has-text('Vertical'), [aria-label*='9:16']")
            if aspect_btn:
                print("[*] Configurando proporção para 9:16...")
                aspect_btn.click()
                page.wait_for_timeout(500)

            # Procura botão de gerar (Create / Generate / Gerar)
            gen_btn = page.query_selector("button:has-text('Generate'), button:has-text('Create'), button:has-text('Criar'), button[type='submit']")
            if gen_btn and gen_btn.is_enabled():
                print("[+] Clicando no botão de gerar...")
                gen_btn.click()
            else:
                print("[*] Pressionando Enter para iniciar geração...")
                input_el.press("Enter")
                
            print("[*] Aguardando imagens serem geradas pelo Imagen 3...")
            # Aguarda as imagens renderizarem na tela
            page.wait_for_timeout(15000)
            
            # Localiza imagens geradas
            generated_imgs = page.query_selector_all("img[src*='blob:'], img[src*='lh3.googleusercontent.com'], img[alt*='generated']")
            print(f"[+] Imagens encontradas na galeria: {len(generated_imgs)}")
            
            from datetime import datetime
            for idx, img in enumerate(generated_imgs[:4]):
                img_path = OUTPUT_DIR / f"generated_influencer_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx+1}.png"
                img.screenshot(path=str(img_path))
                saved_images.append(img_path)
                print(f"[+] Imagem {idx+1} salva em: {img_path}")
        else:
            print("[!] Não foi possível identificar o campo de prompt automaticamente.")
            print("[*] A janela permanecerá aberta e o prompt já foi copiado para seu Ctrl+V.")
            page.wait_for_timeout(15000)

        context.close()
        
    return saved_images

if __name__ == "__main__":
    import sys
    test_p = sys.argv[1] if len(sys.argv) > 1 else (
        "A candid smartphone selfie of a 22-year-old woman smiling naturally, vertical 9:16, unedited natural skin texture with visible pores, soft natural daylight from a window, subtle catchlight in pupils, wearing a cozy oversized ribbed cream sweater."
    )
    imgs = run_imagefx_automation(test_p, headless=False)
    print(f"Total de imagens salvas: {len(imgs)}")
