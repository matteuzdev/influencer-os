"""
Geração Automática no Google ImageFX / Flow via Playwright (CDP ou Perfil Persistente)
Preenche o prompt, seleciona 9:16, clica em gerar e baixa os resultados.
"""
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from playwright.sync_api import sync_playwright
import requests

PROFILE_DIR = Path.home() / ".chrome-influencer-profile"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CDP_URL = "http://127.0.0.1:9222"

def is_cdp_online() -> bool:
    try:
        r = requests.get(f"{CDP_URL}/json/version", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

def generate_image_on_flow(prompt_text: str, aspect_ratio: str = "9:16") -> List[Path]:
    print("\n" + "="*60)
    print("[*] DISPARANDO GERAÇÃO AUTOMÁTICA NO GOOGLE FLOW")
    print("="*60)
    
    saved_files: List[Path] = []
    
    with sync_playwright() as p:
        if is_cdp_online():
            print("[+] Conectando à janela do Chrome já aberta na sua tela (porta 9222)...")
            browser = p.chromium.connect_over_cdp(CDP_URL)
            context = browser.contexts[0]
            # Encontra a aba do ImageFX / Labs
            page = None
            for pg in context.pages:
                if "labs.google" in pg.url or "image-fx" in pg.url:
                    page = pg
                    break
            if not page:
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://labs.google/fx/tools/image-fx", wait_until="domcontentloaded")
        else:
            print("[*] Chrome não detectado na porta 9222. Abrindo navegador com perfil salvo...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                channel="chrome",
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://labs.google/fx/tools/image-fx", wait_until="domcontentloaded")

        page.wait_for_timeout(3000)
        
        # Verifica se está deslogado
        if "accounts.google.com" in page.url or page.query_selector("input[type='email']"):
            print("[!] É necessário fazer o login no Google primeiro.")
            return []

        # Localiza o campo de prompt
        print("[*] Inserindo o prompt...")
        prompt_selectors = [
            "textarea",
            "input[placeholder*='prompt']",
            "[contenteditable='true']",
            "[aria-label*='prompt']"
        ]
        input_el = None
        for sel in prompt_selectors:
            el = page.query_selector(sel)
            if el and el.is_visible():
                input_el = el
                break

        if not input_el:
            print("[!] Campo de prompt não encontrado. Salvando print da tela para análise...")
            err_shot = OUTPUT_DIR / "debug_page_view.png"
            page.screenshot(path=str(err_shot))
            print(f"[!] Print salvo em: {err_shot}")
            return []

        # Limpa e digita o prompt
        input_el.click()
        try:
            input_el.fill(prompt_text)
        except Exception:
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.type(prompt_text, delay=10)
            
        page.wait_for_timeout(1000)

        # Seleciona 9:16 se botão existir
        ratio_btn = page.query_selector("button:has-text('9:16'), button:has-text('Vertical'), [aria-label*='9:16']")
        if ratio_btn:
            print("[*] Selecionando proporção 9:16...")
            ratio_btn.click()
            page.wait_for_timeout(500)

        # Clica em Gerar
        gen_btn = page.query_selector("button:has-text('Generate'), button:has-text('Create'), button:has-text('Criar'), button[type='submit']")
        if gen_btn and gen_btn.is_enabled():
            print("[+] Clicando em Gerar...")
            gen_btn.click()
        else:
            print("[*] Enviando Enter para disparar geração...")
            input_el.press("Enter")

        print("[*] Aguardando o Imagen 3 processar as imagens (20s)...")
        page.wait_for_timeout(20000)

        # Captura screenshot do resultado na interface
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shot_path = OUTPUT_DIR / f"flow_result_{ts}.png"
        page.screenshot(path=str(shot_path))
        saved_files.append(shot_path)
        print(f"[+] Tela com os resultados salva em: {shot_path}")

        # Tenta salvar os elementos de imagem individuais
        imgs = page.query_selector_all("img[src*='blob:'], img[src*='lh3.googleusercontent.com']")
        for idx, img in enumerate(imgs[:4]):
            img_path = OUTPUT_DIR / f"flow_image_{ts}_{idx+1}.png"
            try:
                img.screenshot(path=str(img_path))
                saved_files.append(img_path)
                print(f"[+] Imagem {idx+1} salva individualmente em: {img_path}")
            except Exception:
                pass

        return saved_files

if __name__ == "__main__":
    import sys
    prompt = sys.argv[1] if len(sys.argv) > 1 else (
        "A candid smartphone selfie of a 22-year-old woman smiling naturally, vertical 9:16, unedited natural skin texture with visible pores, soft natural daylight from a window, subtle catchlight in pupils, wearing a cozy oversized ribbed cream sweater."
    )
    res = generate_image_on_flow(prompt)
    print("Arquivos gerados:", res)
