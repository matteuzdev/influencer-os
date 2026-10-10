"""
Módulo de Extração e Download de Mídia (Playwright + Requests)
Capaz de baixar imagens diretas ou extrair o frame em alta resolução de páginas
do Pinterest, Instagram, TikTok ou qualquer página web.
"""
import io
import re
import urllib.parse
from pathlib import Path
from typing import Optional
import requests
from PIL import Image
from playwright.sync_api import sync_playwright
from config import INPUT_DIR

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def download_image_from_url(url: str, filename_prefix: str = "ref_image") -> Path:
    """
    Baixa uma imagem direta via HTTP request.
    """
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    
    # Valida formato com Pillow
    img = Image.open(io.BytesIO(resp.content))
    ext = img.format.lower() if img.format else "jpg"
    if ext == "jpeg":
        ext = "jpg"
        
    out_path = INPUT_DIR / f"{filename_prefix}_{int(Image.MAX_IMAGE_PIXELS or 1)}.{ext}"
    from datetime import datetime
    out_path = INPUT_DIR / f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    
    with open(out_path, "wb") as f:
        f.write(resp.content)
        
    return out_path

def capture_media_with_playwright(url: str, output_prefix: str = "web_frame") -> Path:
    """
    Navega até uma página (Pinterest, TikTok, Instagram ou qualquer site) com Playwright
    e extrai a imagem principal ou o frame de vídeo em alta resolução.
    """
    from datetime import datetime
    out_path = INPUT_DIR / f"{output_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1080, "height": 1920}, # Proporção vertical
            user_agent=HEADERS["User-Agent"]
        )
        page = context.new_page()
        
        print(f"[*] Navegando para: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=35000)
        page.wait_for_timeout(3500) # Aguarda renderização de scripts dinâmicos
        
        # Remove modais, popups de login e backdrops do Pinterest/TikTok
        js_cleanup = """
        () => {
            const dialogs = document.querySelectorAll('[role="dialog"], [data-test-id*="signup"], [data-test-id*="modal"], [data-test-id*="unauth"]');
            dialogs.forEach(e => e.remove());
            const allFixed = document.querySelectorAll('div');
            allFixed.forEach(d => {
                const style = window.getComputedStyle(d);
                if (style.position === 'fixed' && parseInt(style.zIndex || '0') > 30) {
                    d.remove();
                }
            });
            document.body.style.overflow = 'auto';
        }
        """
        page.evaluate(js_cleanup)
        page.wait_for_timeout(1000)

        # 1. Tenta encontrar elemento de vídeo para extrair o frame (o hack da aula)
        video_el = page.query_selector("video")
        if video_el:
            print("[+] Vídeo detectado na página! Capturando frame de alta resolução...")
            # Avança para 1.5s para capturar um frame limpo e nítido
            page.evaluate("""
                (v) => {
                    if (v) { v.currentTime = 1.5; v.pause(); }
                }
            """, video_el)
            page.wait_for_timeout(1500)
            video_el.screenshot(path=str(out_path))
            browser.close()
            return out_path
            
        # 2. Se for Pinterest ou página de imagem, busca a imagem principal
        main_img = page.query_selector("div[data-test-id='pin-image-wrapper'] img, img[srcset], main img, img")
        if main_img:
            src = main_img.get_attribute("src")
            print(f"[+] Imagem detectada na página ({src[:50] if src else ''}... )")
            main_img.screenshot(path=str(out_path))
            browser.close()
            return out_path
            
        # 3. Fallback: Captura da tela
        print("[*] Capturando snapshot central da página...")
        page.screenshot(path=str(out_path))
        browser.close()
        return out_path

def get_reference_media(source: str) -> Path:
    """
    Determina se a fonte é um arquivo local, link direto ou URL de página
    e devolve o caminho do arquivo local pronto para o MIRR0R.
    """
    local_path = Path(source)
    if local_path.exists() and local_path.is_file():
        return local_path
        
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in ("http", "https"):
        # Se terminar com extensão de imagem comum
        if any(parsed.path.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            print("[*] Link direto de imagem detectado.")
            return download_image_from_url(source)
        else:
            print("[*] URL web detectada. Acionando Playwright...")
            return capture_media_with_playwright(source)
            
    raise FileNotFoundError(f"Não foi possível processar a entrada: {source}")

if __name__ == "__main__":
    import sys
    test_src = sys.argv[1] if len(sys.argv) > 1 else "https://picsum.photos/1080/1920"
    res = get_reference_media(test_src)
    print(f"[+] Mídia salva em: {res}")
