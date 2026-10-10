"""
Scraper de conversas compartilhadas do ChatGPT com Playwright.
Renderiza as páginas de share e extrai as mensagens dos turnos (User e Assistant)
para recuperar os prompts e JSONs de ouro das Aulas 3 e 4.
"""
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_OUT = Path("influencer_pipeline/aulas_3_4_chats")
BASE_OUT.mkdir(parents=True, exist_ok=True)

URLS = [
    ("aula3_chat_principal", "https://chatgpt.com/share/69376156-98c4-8012-9a49-e4f722ea57a3"),
    ("aula4_chat_01", "https://chatgpt.com/share/6938e89e-3a80-8012-a65a-4bb580c3976a"),
    ("aula4_chat_02", "https://chatgpt.com/share/6938e9ce-ccf4-8012-b0f2-2c953390c4b4"),
    ("aula4_chat_03", "https://chatgpt.com/share/6938e9ec-4d80-8012-a9eb-c00914ac326f"),
    ("aula4_chat_04", "https://chatgpt.com/share/6938ea2a-6cc8-8012-900f-1f1714344324")
]

def scrape_share(page, name: str, url: str):
    print(f"\n[*] Acessando {name}: {url}")
    try:
        page.goto(url, wait_until="networkidle", timeout=45000)
    except Exception as e:
        print(f"[!] Timeout networkidle, tentando domcontentloaded: {e}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
    page.wait_for_timeout(4000)

    # Extrai o título da conversa
    title = page.title()

    # Extrai as mensagens do chat
    # Seletores comuns do ChatGPT compartilhado:
    # [data-message-author-role] ou .whitespace-pre-wrap ou artigos
    messages_data = page.evaluate("""
        () => {
            const results = [];
            const msgEls = document.querySelectorAll('[data-message-author-role]');
            if (msgEls.length > 0) {
                msgEls.forEach(el => {
                    const role = el.getAttribute('data-message-author-role');
                    const text = el.innerText;
                    results.push({ role, text });
                });
                return results;
            }
            
            // Fallback: busca por blocos de artigo ou conversas
            const articles = document.querySelectorAll('article');
            articles.forEach((art, idx) => {
                const text = art.innerText;
                results.push({ role: idx % 2 === 0 ? 'user' : 'assistant', text });
            });
            return results;
        }
    """)

    out_file = BASE_OUT / f"{name}.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# CONVERSA COMPARTILHADA: {name}\n")
        f.write(f"URL: {url}\n")
        f.write(f"Título: {title}\n\n---\n\n")
        
        if messages_data:
            for i, msg in enumerate(messages_data):
                role = msg.get("role", "unknown").upper()
                text = msg.get("text", "").strip()
                f.write(f"## [{i+1}] {role}\n\n{text}\n\n---\n\n")
        else:
            # Fallback geral do corpo da página
            body_text = page.inner_text("body")
            f.write(f"## CONTEÚDO BRUTO DA PÁGINA\n\n{body_text}\n")
            
    print(f"[+] Salvo em: {out_file} (Mensagens extraídas: {len(messages_data)})")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for name, url in URLS:
            try:
                scrape_share(page, name, url)
            except Exception as e:
                print(f"[!] Erro ao processar {name}: {e}")
                
        browser.close()

if __name__ == "__main__":
    main()
