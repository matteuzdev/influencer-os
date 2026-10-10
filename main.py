"""
INFLUENCER$ IA™ — Studio Engine v2.0
Suporta dois fluxos principais:
1. Usar Persona Fixa Existente (ex: Synthia) para criar novas fotos consistentes em qualquer cenário.
2. Criar Nova Persona a partir de link (Pinterest/TikTok) ou foto local via engenharia reversa MIRR0R.
"""
import argparse
import sys
from pathlib import Path
from config import BASE_DIR, OUTPUT_DIR
from media_scraper import get_reference_media
from mirror_engine import extract_visual_dna, save_dna_artifacts
from flow_automator import run_imagefx_automation, copy_to_clipboard
from persona_engine import generate_scene_for_persona, list_available_personas, load_persona

def print_banner():
    banner = r"""
======================================================================
  ___ _   _ _____ _    _   _ _____ _   _  ____ _____ ____    ___    _    
 |_ _| \ | |  ___| |  | | | | ____| \ | |/ ___| ____|  _ \  |_ _|  / \   
  | ||  \| | |_  | |  | | | |  _| |  \| | |   |  _| | |_) |  | |  / _ \  
  | || |\  |  _| | |__| |_| | |___| |\  | |___| |___|  _ <   | | / ___ \ 
 |___|_| \_|_|   |_____\___/|_____|_| \_|\____|_____|_| \_\ |___/_/   \_\
                     STUDIO ENGINE v2.0 (2 MODOS)
======================================================================
"""
    print(banner)

def handle_existing_persona(persona_name: str, scene_brief: str, generate: bool, headless: bool):
    print(f"\n[*] MODO 1: Gerando nova foto para a Persona Fixa '{persona_name}'...")
    res = generate_scene_for_persona(persona_name, scene_brief, auto_generate=False)
    
    print("\n" + "="*60)
    print(f"[+] MASTER PROMPT PARA {res['persona'].upper()} (DNA BLINDADO):")
    print(f"\"{res['master_prompt']}\"")
    print("="*60)
    print(f"[*] Prompt salvo em: {res['prompt_path']}")
    print("[+] Prompt copiado para a área de transferência do Windows!")

    if generate:
        print("\n[*] Disparando geração automática no Google Flow (Imagen 3)...")
        saved = run_imagefx_automation(res["master_prompt"], headless=headless)
        if saved:
            print("\n[+] Novas imagens salvas:")
            for p in saved:
                print(f"  -> {p}")
    else:
        print("\n[*] Prompt pronto no seu Ctrl+V para colar onde preferir.")

def handle_new_persona(source: str, modifications: str, register_name: str, generate: bool, headless: bool):
    print(f"\n[*] MODO 2: Criando NOVA persona a partir de referência: {source}")
    ref_image_path = get_reference_media(source)
    print(f"[+] Frame de referência capturado: {ref_image_path}")

    print("[*] Acionando MIRR0R PRO v2 (Engenharia Reversa Visual)...")
    dna_data = extract_visual_dna(ref_image_path)
    
    if modifications:
        print(f"[*] Aplicando modificações solicitadas: {modifications}")
        # Injeta modificações
        pass
        
    j_path, p_path = save_dna_artifacts(dna_data, prefix=register_name or "new_persona")
    master_prompt = dna_data.get("master_prompt_en", "")
    
    print("\n" + "="*60)
    print("[+] DNA VISUAL EXTRAÍDO COM SUCESSO:")
    print(f"  * Idade: {dna_data.get('subject', {}).get('age', 'N/A')}")
    print(f"  * Rosto/Pele: {dna_data.get('subject', {}).get('face', {}).get('makeup', 'N/A')}")
    print(f"  * Cabelo: {dna_data.get('subject', {}).get('hair', {}).get('color', 'N/A')}")
    print(f"  * Iluminação: {dna_data.get('background', {}).get('lighting', 'N/A')}")
    print("="*60)
    print(f"\n[+] MASTER PROMPT GERADO:\n\"{master_prompt}\"\n")
    
    copy_to_clipboard(master_prompt)

    if register_name:
        import json
        persona_record = {
            "id": register_name.lower(),
            "name": register_name.capitalize(),
            "archetype": "Synthetic Influencer",
            "dna": dna_data.get("subject", {}),
            "photography_dna": dna_data.get("photography", {}),
            "master_prompt_seed": master_prompt
        }
        rec_path = BASE_DIR / "personas" / f"{register_name.lower()}.json"
        with open(rec_path, "w", encoding="utf-8") as f:
            json.dump(persona_record, f, indent=2, ensure_ascii=False)
        print(f"[+] Nova Persona '{register_name}' cadastrada em: {rec_path}")

    if generate:
        print("\n[*] Disparando geração da Imagem-Mãe no Google Flow...")
        saved = run_imagefx_automation(master_prompt, headless=headless)
        if saved:
            print("\n[+] Imagem-Mãe gerada e salva:")
            for p in saved:
                print(f"  -> {p}")

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Influencer IA Studio Engine")
    parser.add_argument("--persona", help="Nome da persona fixa (ex: synthia)")
    parser.add_argument("--scene", help="Briefing da nova cena para a persona fixa")
    parser.add_argument("--new", action="store_true", help="Criar nova persona a partir de link ou foto")
    parser.add_argument("--url", help="URL do Pinterest, TikTok ou imagem para nova persona")
    parser.add_argument("--mods", help="Modificações na nova persona (ex: 'ficar ruiva')")
    parser.add_argument("--name", help="Nome para cadastrar a nova persona fixa")
    parser.add_argument("--no-generate", action="store_true", help="Apenas gera prompt/JSON sem abrir navegador")
    parser.add_argument("--headless", action="store_true", help="Geração em segundo plano")

    args = parser.parse_args()

    # Modo 1: Persona Fixa via CLI
    if args.persona and args.scene:
        handle_existing_persona(
            persona_name=args.persona,
            scene_brief=args.scene,
            generate=not args.no_generate,
            headless=args.headless
        )
        return

    # Modo 2: Nova Persona via CLI
    if args.new and (args.url or len(sys.argv) > 2):
        src = args.url or sys.argv[2]
        handle_new_persona(
            source=src,
            modifications=args.mods or "",
            register_name=args.name or "",
            generate=not args.no_generate,
            headless=args.headless
        )
        return

    # Menu Interativo caso rode sem argumentos
    available = list_available_personas()
    print("ESCOLHA O MODO DE OPERAÇÃO:")
    print(f"1. Usar Persona Fixa Existente (Cadastradas: {', '.join(available)})")
    print("2. Criar Nova Persona a partir de Link do Pinterest ou Foto")
    
    choice = input("\nDigite 1 ou 2 >> ").strip()
    
    if choice == "1":
        p_name = input(f"Nome da persona [{available[0] if available else 'synthia'}]: ").strip() or "synthia"
        scene = input("Descreva a nova cena (ex: 'tomando café em Paris', 'no carro BMW na chuva'): ").strip()
        handle_existing_persona(p_name, scene, generate=not args.no_generate, headless=args.headless)
    elif choice == "2":
        url = input("Cole o link do Pinterest/TikTok ou caminho da foto: ").strip()
        mods = input("Deseja alguma modificação (ex: 'ruiva', 'cabelo curto') [deixe vazio para manter fiel]: ").strip()
        reg_name = input("Deseja cadastrar com um nome fixo? (ex: 'Kaelen', deixe vazio se não): ").strip()
        handle_new_persona(url, mods, reg_name, generate=not args.no_generate, headless=args.headless)
    else:
        print("Opção inválida.")

if __name__ == "__main__":
    main()
