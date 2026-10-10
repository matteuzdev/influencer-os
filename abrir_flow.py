"""
Abrir Google Flow / Labs no Chrome Real para Login e Geração Automática
Executa o Chrome oficial na sua tela com o perfil dedicado e suporte ao Copiloto.
"""
import sys
import subprocess
import time
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = Path.home() / ".chrome-influencer-profile"
FLOW_URL = "https://labs.google/fx/tools/image-fx"
CDP_PORT = 9222

def main():
    print("=" * 60, flush=True)
    print("[*] INICIANDO GOOGLE CHROME PARA FLOW COPILOT", flush=True)
    print(f"[*] Perfil: {PROFILE_DIR}", flush=True)
    print("=" * 60, flush=True)
    
    cmd = [
        CHROME_PATH,
        f"--user-data-dir={PROFILE_DIR}",
        f"--remote-debugging-port={CDP_PORT}",
        "--no-first-run",
        "--no-default-browser-check",
        FLOW_URL
    ]
    
    print("[*] Abrindo a janela do Chrome na sua tela...", flush=True)
    proc = subprocess.Popen(cmd)
    
    # Mantém o processo vivo monitorando
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        
    print("[+] Sessão finalizada.", flush=True)

if __name__ == "__main__":
    main()
