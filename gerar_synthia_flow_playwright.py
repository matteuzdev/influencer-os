"""
Copiloto Automático da Synthia no Google Flow / ImageFX
Abre o Playwright oficial com Chrome real visível na tela do usuário,
mantém o perfil salvo e executa a geração automática do prompt da Synthia em 9:16.
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(line_buffering=True)

# Diretórios
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

USER_DATA_DIR = Path.home() / ".flow_synthia_profile"
FLOW_URL = "https://flow.google.com/project/8f2818a1-af39-4697-ad1f-c892ee61f3c2/collection/74c8281d-2e25-4983-8576-194c7dd9e74c"

import json

SYNTHIA_MIRROR_JSON = {
  "subject": {
    "type": "person",
    "character_name": "Synthia",
    "face": {
      "preserve_original": True,
      "facial_identity": "Strictly preserve exact facial identity and features from registered character",
      "skin_texture": "unedited natural skin texture, visible soft pores, realistic warm undertones, zero artificial smoothing",
      "eyes": "dark expressive eyes, direct confident gaze into lens, natural window catchlight",
      "mouth": "soft natural pink lips slightly parted, relaxed candid expression"
    },
    "hair": {
      "color": "natural vibrant copper-red and warm ginger-auburn with realistic undertones",
      "style": "long layered cut cascading naturally over both shoulders, delicate flyaways framing face"
    },
    "accessories": {
      "necklace": "delicate pearl choker necklace with central silver celestial orb-and-ring pendant"
    },
    "clothing": "form-fitting candid indoor lounge top"
  },
  "photography": {
    "camera_style": "candid smartphone front camera selfie",
    "aspect_ratio": "9:16 vertical portrait",
    "focal_length": "35mm perspective",
    "texture": "raw mobile camera sensor texture, authentic micro-details, authentic photorealism, zero plastic look"
  },
  "lighting": {
    "type": "soft diffused morning window light from the side",
    "shadows": "gentle and natural, creating realistic facial depth",
    "catchlight": "natural reflections in pupils"
  },
  "setting": "relaxed indoor bedroom setting with cream bedding and soft morning light"
}

SYNTHIA_MASTER_PROMPT = json.dumps(SYNTHIA_MIRROR_JSON, indent=2)

def run():
    print("=" * 65, flush=True)
    print("      COPILOTO AUTOMÁTICO SYNTHIA // GOOGLE FLOW (IMAGEFX)", flush=True)
    print("=" * 65, flush=True)
    print(f"[*] Perfil persistente: {USER_DATA_DIR}", flush=True)
    print("[*] Abrindo Google Chrome via Playwright na sua tela...", flush=True)
    
    with sync_playwright() as p:
        # Abre o Chrome oficial com o perfil persistente na tela em modo Stealth (sem flag de teste/automacao)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            channel="chrome",
            headless=False,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-first-run",
                "--no-default-browser-check"
            ]
        )
        
        # Mascara o navigator.webdriver para a conta Google nao detectar
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.pages[0] if context.pages else context.new_page()
        
        print(f"[*] Acessando Google Flow: {FLOW_URL}...", flush=True)
        page.goto(FLOW_URL)
        
        print("\n" + "-" * 65, flush=True)
        print("[*] Aguardando a interface inicial carregar...", flush=True)
        print("-" * 65 + "\n", flush=True)
        time.sleep(3)
        
        # 1. Verifica se precisa clicar em 'Novo projeto' (Interface do Google Flow)
        novo_projeto_selectors = [
            "button:has-text('Novo projeto')",
            "button:has-text('Novo Projeto')",
            "button:has-text('New project')",
            "button:has-text('New Project')",
            "div[role='button']:has-text('Novo projeto')",
            "div[role='button']:has-text('Novo Projeto')",
            "div[role='button']:has-text('New project')",
            "a:has-text('Novo projeto')",
            "a:has-text('Novo Projeto')",
            "[aria-label*='Novo projeto']",
            "[aria-label*='New project']",
            "button:has-text('Criar projeto')",
            "button:has-text('+ Novo')"
        ]
        
        selector_prompt = "textarea, input[placeholder*='prompt'], [contenteditable='true'], [aria-label*='prompt'], [role='textbox']"
        
        # Se o campo de prompt ainda não está visível, procura o botão 'Novo projeto'
        if not page.query_selector(selector_prompt):
            print("[*] Procurando botão 'Novo projeto' na dashboard...", flush=True)
            for sel in novo_projeto_selectors:
                try:
                    btn = page.query_selector(sel)
                    if btn and btn.is_visible():
                        print(f"[+] Botão 'Novo projeto' encontrado! Clicando...", flush=True)
                        btn.click()
                        time.sleep(3)
                        break
                except Exception:
                    pass
        
        # 2. Aguarda até o campo de prompt aparecer
        print("[*] Aguardando área de trabalho do projeto carregar o campo de prompt...", flush=True)
        try:
            page.wait_for_selector(selector_prompt, timeout=60000)
            print("[+] Interface do projeto pronta para receber o prompt!", flush=True)
        except Exception as e:
            print(f"[!] Dica: Se a tela abriu na dashboard, clique manualmente em 'Novo projeto'.", flush=True)
            print("[*] Aguardando o campo de prompt por mais 60 segundos...", flush=True)
            try:
                page.wait_for_selector(selector_prompt, timeout=60000)
                print("[+] Interface detectada com sucesso!", flush=True)
            except Exception:
                print("[!] Não foi possível detectar o campo de prompt a tempo.", flush=True)
                input("\nPressione ENTER para fechar...")
                context.close()
                return
            
        time.sleep(1)
        
        # 3. Seleção da Personagem Cadastrada (Face Lock Nativo do Flow - Aula 4)
        print("\n[*] Conectando à Personagem da Synthia no Google Flow para Face Lock...", flush=True)
        
        # Método A: Tentar clicar na aba lateral 'Personagens'
        try:
            personagens_menu = page.locator("text='Personagens'").first
            if personagens_menu.is_visible():
                print("[+] Clicando na aba lateral 'Personagens'...", flush=True)
                personagens_menu.click()
                time.sleep(2)
                
                # Clica no card da Synthia na lista de personagens
                char_card = page.locator("div:has-text('Synthia'), img[alt*='Synthia'], div[role='gridcell'] img, div[data-item-index='0']").first
                if char_card.is_visible():
                    print("[+] Personagem Synthia encontrada! Clicando para anexar à cena...", flush=True)
                    char_card.click()
                    time.sleep(1.5)
        except Exception as e:
            print(f"[*] Detalhe seleção aba Personagens: {e}", flush=True)
            
        # Método B: Se não selecionou, tentar clicar no botão '+' da barra de prompt
        try:
            plus_btn = page.locator("button:has-text('+'), div[role='button']:has-text('+'), [aria-label*='Adicionar']").first
            if plus_btn.is_visible():
                print("[+] Clicando no botão '+' da barra de prompt...", flush=True)
                plus_btn.click()
                time.sleep(1.5)
                # No popup, seleciona a Synthia ou Personagens
                item = page.locator("text='Synthia', text='Personagens'").first
                if item.is_visible():
                    item.click()
                    time.sleep(1.5)
        except Exception as e:
            print(f"[*] Detalhe botão '+': {e}", flush=True)
        
        # 4. Preenchimento do Prompt Oficial em Formato JSON do MIRR0R
        print("\n[*] Injetando o Prompt Estruturado em Formato JSON Oficial do MIRR0R...", flush=True)
        prompt_selectors = [
            "[placeholder*='O que você quer criar']",
            "textarea",
            "[contenteditable='true']",
            "[role='textbox']",
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
            input_el.click()
            time.sleep(0.5)
            # Limpa qualquer texto antigo
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            time.sleep(0.3)
            
            # Digita o JSON oficial do MIRR0R
            try:
                input_el.fill(SYNTHIA_MASTER_PROMPT)
            except Exception:
                page.keyboard.type(SYNTHIA_MASTER_PROMPT, delay=1)
                
            print("[+] JSON do MIRR0R inserido com sucesso na caixa de criação!", flush=True)
            time.sleep(1)
            
            # Ajuste de proporção para 9:16 se botão existir
            ratio_btn = page.query_selector("button:has-text('9:16'), button:has-text('Vertical'), [aria-label*='9:16']")
            if ratio_btn and ratio_btn.is_visible():
                print("[*] Ajustando proporção para 9:16 vertical...", flush=True)
                ratio_btn.click()
                time.sleep(1)
                
            # Clique no botão Gerar (seta ➔ ou botão Criar)
            gen_btn = page.query_selector("button:has-text('➔'), button[aria-label*='Gerar'], button[aria-label*='Criar'], button:has-text('Generate'), button:has-text('Criar'), button[type='submit']")
            if gen_btn and gen_btn.is_enabled():
                print("[+] Clicando no botão de gerar (➔) do Google Flow...", flush=True)
                gen_btn.click()
            else:
                print("[*] Pressionando Enter para disparar a geração no Nano Banana...", flush=True)
                input_el.press("Enter")
                
            print("\n[*] Geração em andamento pelo Nano Banana 2.1 / Flow!", flush=True)
            print("[*] Aguardando renderização das 4 fotos (25 segundos)...", flush=True)
            time.sleep(25)
            
            # Salvar resultados
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = OUTPUT_DIR / f"synthia_flow_screenshot_{ts}.png"
            page.screenshot(path=str(screenshot_path))
            print(f"\n[+] Print da tela de resultados salvo em:\n    {screenshot_path}", flush=True)
            
            # Buscar e salvar as imagens individuais
            imgs = page.query_selector_all("img[src*='blob:'], img[src*='lh3.googleusercontent.com']")
            salvas = 0
            for idx, img in enumerate(imgs):
                # Ignora avatares pequenos
                box = img.bounding_box()
                if box and box['width'] > 150:
                    salvas += 1
                    img_path = OUTPUT_DIR / f"synthia_flow_{ts}_{salvas}.png"
                    img.screenshot(path=str(img_path))
                    print(f"  -> Foto {salvas} salva em: {img_path.name}", flush=True)
                    if salvas >= 4:
                        break
                        
            print("\n" + "=" * 65, flush=True)
            print(f"[+] SUCESSO! {salvas} fotos da Synthia salvas em:", flush=True)
            print(f"    {OUTPUT_DIR}", flush=True)
            print("=" * 65 + "\n", flush=True)
            
        print("[*] Automação concluída!")
        input("Pressione ENTER para encerrar a janela...")
        context.close()

if __name__ == "__main__":
    run()
