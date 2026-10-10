"""
Automação Completa da Synthia no Google Flow / ImageFX
Conecta ao Chrome aberto na sua tela, aguarda o login ser concluído,
injeta o prompt oficial da Synthia, configura 9:16 e salva as imagens.
"""
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests

sys.stdout.reconfigure(line_buffering=True)

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CDP_URL = "http://127.0.0.1:9222"

SYNTHIA_MASTER_PROMPT = (
    "A candid smartphone selfie of Synthia, early twenties, vertical 9:16 portrait. "
    "Fair skin with natural unedited pores and subtle warm undertones, oval face, "
    "well-defined natural brows, small nose, soft natural pink lips. "
    "Vibrant copper-red and warm ginger-auburn long hair with natural waves cascading over shoulders. "
    "Wearing a delicate pearl choker necklace with a central silver orb-and-ring pendant. "
    "Relaxed indoor bedroom setting with cream bedding and soft morning window light from the side, "
    "natural catchlight in eyes. Shot on smartphone front camera, 35mm perspective, authentic photorealism, zero plastic look."
)

def monitor_and_generate(prompt: str = SYNTHIA_MASTER_PROMPT):
    print("=" * 60, flush=True)
    print("[*] INICIANDO COPILOTO AUTOMÁTICO DA SYNTHIA", flush=True)
    print("=" * 60, flush=True)

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"[!] Não foi possível conectar na porta 9222: {e}", flush=True)
            return False

        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        print("[*] Conectado à sua janela do Chrome!", flush=True)
        print("[*] Aguardando você concluir o login na conta Google...", flush=True)

        # Espera o login ser concluído
        logged_in = False
        for i in range(120): # até 6 minutos
            url = page.url
            # Se saiu de accounts.google.com e está no flow ou imagefx
            if "accounts.google.com" not in url and ("flow.google" in url or "image-fx" in url or "labs.google" in url):
                # Verifica se há campo de prompt na tela
                has_input = page.query_selector("textarea, input[placeholder*='prompt'], [contenteditable='true'], [aria-label*='prompt']")
                if has_input:
                    logged_in = True
                    print("\n[+] LOGIN DETECTADO! Interface do Google Flow pronta!", flush=True)
                    break
            
            if i % 10 == 0:
                print(f"[*] [Status] Aguardando login... ({i*3}s)", flush=True)
            page.wait_for_timeout(3000)

        if not logged_in:
            print("[!] Tempo de espera limite atingido. Faça o login e execute novamente.", flush=True)
            return False

        # Injeta o prompt
        print("\n[*] Preenchendo o prompt oficial da Synthia...", flush=True)
        input_el = page.query_selector("textarea, input[placeholder*='prompt'], [contenteditable='true'], [aria-label*='prompt']")
        if input_el:
            input_el.click()
            try:
                input_el.fill(prompt)
            except Exception:
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(prompt, delay=5)
            page.wait_for_timeout(1000)

            # Tenta selecionar 9:16
            ratio_btn = page.query_selector("button:has-text('9:16'), button:has-text('Vertical'), [aria-label*='9:16']")
            if ratio_btn:
                print("[*] Ajustando proporção para 9:16 vertical...", flush=True)
                ratio_btn.click()
                page.wait_for_timeout(500)

            # Clica em Gerar
            gen_btn = page.query_selector("button:has-text('Generate'), button:has-text('Create'), button:has-text('Criar'), button[type='submit']")
            if gen_btn and gen_btn.is_enabled():
                print("[+] Clicando no botão GERAR...", flush=True)
                gen_btn.click()
            else:
                print("[*] Pressionando Enter para iniciar a geração...", flush=True)
                input_el.press("Enter")

            print("\n[*] Geração em andamento! Aguardando o Imagen 3 renderizar as imagens (25s)...", flush=True)
            page.wait_for_timeout(25000)

            # Captura a tela de resultados
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            screen_shot = OUTPUT_DIR / f"synthia_flow_live_{ts}.png"
            page.screenshot(path=str(screen_shot))
            print(f"[+] Print ao vivo da geração salvo em: {screen_shot}", flush=True)

            # Salva imagens geradas individuais
            imgs = page.query_selector_all("img[src*='blob:'], img[src*='lh3.googleusercontent.com']")
            print(f"[+] Total de imagens renderizadas encontradas: {len(imgs)}", flush=True)
            for idx, img in enumerate(imgs[:4]):
                img_path = OUTPUT_DIR / f"synthia_flow_{ts}_{idx+1}.png"
                try:
                    img.screenshot(path=str(img_path))
                    print(f"  -> Foto {idx+1} salva em: {img_path}", flush=True)
                except Exception as e:
                    pass

            print("\n" + "=" * 60, flush=True)
            print("[+] PROCESSO CONCLUÍDO COM SUCESSO!", flush=True)
            print("=" * 60, flush=True)
            return True

if __name__ == "__main__":
    monitor_and_generate()
