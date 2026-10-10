"""
Motor Comercial da Synthia: Provador Virtual & UGC para Lojas
Recebe a foto de uma peça de roupa/produto, extrai o DNA técnico 1:1,
faz a Synthia vestir o produto mantendo o rosto travado,
e gera o roteiro falado em PT-BR (HUMAN ENGINE™) para anúncios de lojas/e-commerce.
"""
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Configurações de diretório
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

from product_engine import extract_product_dna
from human_engine import generate_behavioral_video_prompt, generate_veo_json_prompt
from persona_engine import load_persona

def gerar_campanha_produto(
    product_image_path: str,
    nome_loja: str = "Boutique Parceira",
    tipo_cenario: str = "provador de boutique elegante com luz suave de espelho",
    persona_name: str = "synthia"
) -> Dict[str, Any]:
    # 1. Carrega o perfil oficial da persona selecionada
    persona = load_persona(persona_name)
    p_name = persona.get("name", persona_name.capitalize())
    niche = persona.get("commercial_profile", {}).get("primary_niche", "Moda & Beleza")
    dna = persona.get("dna", {})
    hair = dna.get("hair", {})
    hair_desc = f"{hair.get('color', 'natural')} {hair.get('style', 'hair cascading naturally')}"
    signature = dna.get("signature_accessories", {}).get("jewelry", "")
    skin = dna.get("skin_texture", "unedited natural skin texture, visible soft pores, realistic warm undertones, zero artificial smoothing")

    print("=" * 65)
    print(f"[*] INICIANDO CAMPANHA COMERCIAL: {p_name.upper()} x {nome_loja.upper()}")
    print(f"[+] Persona ativa: {p_name} ({niche})")
    print("=" * 65)
    
    # 2. Extrai o DNA de confecção 1:1 do produto via MIRR0R
    print(f"[*] Analisando DNA físico da peça em: {product_image_path}...")
    try:
        product_dna = extract_product_dna(product_image_path)
        print("[+] DNA do Produto extraído com sucesso pixel a pixel!")
    except Exception as e:
        print(f"[!] Erro ao analisar imagem: {e}. Usando template estruturado de produto.")
        product_dna = {
            "product_identity": {"category": "Vestido Midi Canelado Elegante"},
            "fabric_and_material_behavior": {"fabric_type": "Knit / Canelado premium encorpado", "drape": "Caimento ajustado ao corpo sem marcar"},
            "color_and_finish": {"base_color": "Terracota / Bege Quente", "finish": "Matte natural"}
        }

    # 3. Gera o MIRR0R JSON para o Google Flow (Persona vestindo a peça)
    print(f"\n[*] Gerando Prompt MIRR0R JSON para o Google Flow ({p_name})...")
    flow_json = {
        "subject": {
            "type": "person",
            "character_name": p_name,
            "face": {
                "preserve_original": True,
                "facial_identity": f"Strictly preserve exact facial identity and features from registered character {p_name}",
                "skin_texture": skin,
                "hair": hair_desc
            },
            "outfit_fitted_product": {
                "preserve_product_1to1": True,
                "product_dna": product_dna,
                "fit": "perfect natural compression and drape on female silhouette, exact seams and fabric texture"
            },
            "accessories": signature or "delicate minimalist accessories",
            "pose": "standing candid in fitting room, one hand lightly brushing the fabric to showcase the material texture, natural micro-smile"
        },
        "photography": {
            "camera_style": "candid smartphone front camera selfie / vertical 9:16 mirror shot",
            "aspect_ratio": "9:16 vertical portrait",
            "focal_length": "28mm equivalent",
            "texture": "authentic unedited smartphone sensor noise, authentic photorealism, zero plastic look"
        },
        "lighting": {
            "type": "warm soft boutique fitting room lighting, natural diffused fill, gentle catchlight in eyes"
        },
        "setting": f"{tipo_cenario}, minimalist neutral tones, soft reflection in boutique mirror"
    }
    
    # 4. Gera o Roteiro Falado em PT-BR para Anúncio de Loja (HUMAN ENGINE™)
    print(f"\n[*] Gerando Roteiro UGC Falado em PT-BR pelo HUMAN ENGINE™ para {p_name}...")
    script_dialogue = (
        f"Ainda dizem que provador de loja é tudo igual... "
        f"Gente, olhem o caimento dessa peça da {nome_loja}. "
        f"O tecido é surreal de confortável, abraça o corpo e não marca nada. "
        f"Vale cada centavo, apaixonada!"
    )
    
    video_prompt = generate_behavioral_video_prompt(
        persona_name=persona_name,
        dialogue_script=script_dialogue,
        scene_context=tipo_cenario,
        camera_movement="slow handheld sway, slight tilt showing the garment fit, push-in towards her smile and fabric texture",
        foco_visual="look"
    )
    
    # 5. Salva os arquivos da campanha
    import time
    ts = time.strftime("%Y%m%d_%H%M%S")
    campanha_dir = OUTPUT_DIR / f"campanha_{persona_name}_{ts}"
    campanha_dir.mkdir(parents=True, exist_ok=True)
    
    flow_file = campanha_dir / "01_prompt_flow_colecao.json"
    with open(flow_file, "w", encoding="utf-8") as f:
        json.dump(flow_json, f, indent=2, ensure_ascii=False)
        
    video_file = campanha_dir / "02_roteiro_video_human_engine.txt"
    with open(video_file, "w", encoding="utf-8") as f:
        f.write(video_prompt)
        
    collection_url = persona.get("commercial_profile", {}).get("collection_url", "https://flow.google.com")
    resumo = {
        "loja": nome_loja,
        "persona": p_name,
        "colecao_flow_url": collection_url,
        "pasta_saida": str(campanha_dir),
        "flow_prompt_json": flow_json,
        "video_prompt": video_prompt
    }
    
    print("\n" + "=" * 65)
    print(f"[+] PACOTE COMERCIAL DE UGC GERADO COM SUCESSO!")
    print(f"    Pasta: {campanha_dir}")
    print("=" * 65)
    return resumo

# Alias retrocompatível
gerar_campanha_produto_synthia = gerar_campanha_produto

if __name__ == "__main__":
    # Teste de demonstração
    gerar_campanha_produto_synthia(
        product_image_path="influencer_pipeline/inputs/clean_video_frame.png",
        nome_loja="Maison Elegance"
    )
