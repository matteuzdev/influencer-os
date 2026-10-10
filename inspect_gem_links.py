"""
Script para inspecionar os links compartilhados do Gemini Gems:
- MIRR0R v.2
- HUMAN ENGINE
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

LINKS = [
    ("gemini_mirror_v2", "https://gemini.google.com/gem/1U777vVbjD036U4LxTwppXmINe1Ds7pEX?usp=sharing"),
    ("gemini_human_engine", "https://gemini.google.com/gem/1nFh09DtvAxj1SZ7dyY1ZiOItydvugzK4?usp=sharing")
]

OUT_DIR = Path("influencer_pipeline/aulas_3_4_chats")
OUT_DIR.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    page = context.new_page()

    for name, url in LINKS:
        print(f"[*] Acessando {name}: {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)
            
            title = page.title()
            body_text = page.inner_text("body")
            
            out_file = OUT_DIR / f"{name}.md"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(f"# GEMINI GEM: {name}\nURL: {url}\nTítulo: {title}\n\n---\n\n")
                f.write(body_text)
                
            print(f"[+] Salvo em: {out_file} (Tamanho: {len(body_text)} caracteres)")
        except Exception as e:
            print(f"[!] Erro ao acessar {name}: {e}")

    browser.close()
