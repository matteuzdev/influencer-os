from playwright.sync_api import sync_playwright

url = 'https://br.pinterest.com/pin/1141029255597093828/'
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1080, 'height': 1920})
    page.goto(url, wait_until='domcontentloaded')
    page.wait_for_timeout(3500)
    
    # 1. Remove all modals, dialogs, backdrops
    js_cleanup = """
    () => {
        const dialogs = document.querySelectorAll('[role="dialog"], [data-test-id*="signup"], [data-test-id*="modal"], [data-test-id*="unauth"]');
        dialogs.forEach(e => e.remove());
        const allFixed = document.querySelectorAll('div');
        allFixed.forEach(d => {
            const style = window.getComputedStyle(d);
            if (style.position === 'fixed' && parseInt(style.zIndex || '0') > 50) {
                d.remove();
            }
        });
        document.body.style.overflow = 'auto';
    }
    """
    page.evaluate(js_cleanup)
    page.wait_for_timeout(1000)
    
    # 2. Check video element
    v = page.query_selector('video')
    if v:
        # Seek to 1.5s for a clear, crisp frame
        page.evaluate("(el) => { el.currentTime = 1.5; el.pause(); }", v)
        page.wait_for_timeout(1500)
        v.screenshot(path='influencer_pipeline/inputs/clean_video_frame.png')
        print("[+] Clean frame successfully saved to influencer_pipeline/inputs/clean_video_frame.png")
    else:
        print("[!] Video not found.")
        
    browser.close()
