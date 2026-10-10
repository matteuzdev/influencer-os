"""
PRODUCT ENGINE™ // Extração de DNA de Produtos Físicos & Repose para Influenciadoras IA
Implementa as diretrizes das Aulas 7 a 11:
1. Extração de DNA 1:1 para fabricação digital (sem estilização ou alucinação).
2. Repose & Lookbook: Coloca a persona vestindo o produto com preservação absoluta.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import google.generativeai as genai
from config import BASE_DIR, GEMINI_API_KEY, OUTPUT_DIR
from flow_automator import copy_to_clipboard
from persona_engine import load_persona

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

PRODUCT_DNA_SYSTEM_PROMPT = """
You are PRODUCT MIRR0R™, the technical reverse-engineering agent for physical products and garments.
Your task is NOT to redesign, interpret, stylize, improve, or adapt the product.
Your task is to extract the complete visual DNA of the product shown, treating it as a physical object that must be reproduced with 1:1 fidelity in downstream image generation.

Ignore the model, pose, facial features, body type, lighting style, environment, and artistic intent.
The product is the only priority.

OUTPUT STRICTLY A VALID JSON with keys:
- product_identity (category, subtype, fit_type, rigidity)
- silhouette_and_geometry (exact profile, vertical_proportions, cut_logic, neckline, sleeves, hemline)
- fabric_and_material_behavior (fabric_type, density, stretch_zones, drape, macro_micro_texture, light_interaction)
- color_and_finish (base_color, undertones, finish_matte_satin_gloss)
- construction_details (seams, stitches, panels, reinforcements, zippers, closures)
- fit_logic (body_adaptation, compression_points, natural_tension)
"""

def extract_product_dna(image_path: str) -> Dict[str, Any]:
    """
    Submete a imagem do produto ao Gemini 2.5 Flash Vision para extrair o DNA físico em JSON.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

    from PIL import Image
    img = Image.open(path)

    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content([
        PRODUCT_DNA_SYSTEM_PROMPT,
        "Analyze this product with 1:1 physical manufacturing fidelity. Output JSON:",
        img
    ])

    text = resp.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    data = json.loads(text)
    out_file = OUTPUT_DIR / f"product_dna_{path.stem}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[+] DNA do produto salvo em: {out_file}")
    return data

def generate_repose_prompt(
    product_dna: Dict[str, Any],
    persona_name: str = "synthia",
    pose_type: str = "standing fashion lookbook, weight shift to one leg"
) -> str:
    """
    Gera o prompt final de imagem para o Google Flow / Imagen 3 Pro
    mantendo o produto blindado no corpo da persona escolhida.
    """
    persona = load_persona(persona_name)
    dna = persona.get("dna", {})
    hair = dna.get("hair", {})
    
    prompt = (
        f"A professional fashion catalog photograph, vertical 9:16. "
        f"{persona.get('name')}, a young woman in her early twenties with {dna.get('ethnicity')}, "
        f"long vibrant {hair.get('color')} hair, natural skin texture with visible pores, "
        f"posing in a {pose_type} in a warmly lit modern interior studio with decorative framed artwork and a plant in the background, positioned at least 1 meter away from the wall. "
        f"She is wearing the exact product: {product_dna.get('product_identity', {}).get('category', 'garment')}, "
        f"made of {product_dna.get('fabric_and_material_behavior', {}).get('fabric_type', 'fabric')}, "
        f"color {product_dna.get('color_and_finish', {}).get('base_color', 'monochrome')}, "
        f"with exact silhouette: {product_dna.get('silhouette_and_geometry', {}).get('exact_profile', 'structured')}, "
        f"featuring {product_dna.get('construction_details', {}).get('seams', 'fine stitching')}. "
        f"Natural realistic lighting, no studio glare, 35mm lens perspective, crisp authentic fabric folds, zero plastic skin."
    )
    
    copy_to_clipboard(prompt)
    print("\n[+] Prompt de Repose gerado e copiado para a Área de Transferência!")
    return prompt

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        dna = extract_product_dna(sys.argv[1])
        prompt = generate_repose_prompt(dna)
        print("\n--- PROMPT GERADO ---")
        print(prompt)
    else:
        print("Uso: python product_engine.py <caminho_da_imagem_do_produto>")
