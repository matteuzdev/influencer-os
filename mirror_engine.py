"""
Motor de Engenharia Reversa Visual (MIRR0R™ Engine PRO v2)
Analisa imagens de referência utilizando visão multimodal no Gemini
e gera o DNA visual estruturado em JSON com a Matriz de Fidelidade Absoluta,
incorporando tratamento avançado de oclusões, reflexos ópticos (mirror_rules),
acessórios categorizados e micro-elementos ambientais.
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, Union
from PIL import Image
import google.generativeai as genai
from config import GEMINI_API_KEY, OUTPUT_DIR

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")

genai.configure(api_key=GEMINI_API_KEY)

MIRROR_SYSTEM_PROMPT = """
You are MIRR0R™, the industry-leading visual reverse-engineering system for hyper-realistic diffusion models (Imagen 3 / Flux.1 / Midjourney).
You analyze reference images with absolute physical, optical, and anatomical fidelity.

CORE OPERATIONAL LAWS:
1. Absolute Physical Grounding: Choose hyper-specific over generic. Describe only what is physically captured within the frame.
2. Explicit Occlusion Handling: If hair, eyes, ears, skin, or jewelry are covered by clothing, hats, shadows, or angle, explicitly state "Not visible under [garment/shadow]" rather than guessing or interpolating.
3. Optical & Surface Realism: Detail material physics (leather grain, matte cotton twill, heathered sweatpants knit, water droplet refraction, vehicle warning labels, metal reflections).
4. Ban Vague AI Buzzwords: NEVER use 'beautiful', 'cute', 'perfect skin', 'hyperrealistic', '4k', 'stunning'. Use concrete descriptors of geometry, texture, luminance, and optics.
5. Mirror & Glass Physics (mirror_rules): Define how reflections, windows, and mirrors behave (softened exterior scenery, upright text/logos, absence of reversed artifacts).
6. Output Format: Output STRICTLY a valid JSON object matching the detailed schema below, with all descriptions in natural, technical photographic English.

REQUIRED JSON SCHEMA:
{
  "subject": {
    "description": "Comprehensive physical description of posture, orientation, head tilt, hand placement, and activity.",
    "mirror_rules": "Specific rules for window/mirror reflections, logo orientations, and wet glass diffusion.",
    "age": "Apparent visual age bracket (e.g. young adult, 18-25 years old).",
    "expression": "Visible lower/upper facial expression, jaw tension, lips, gaze direction, or occlusion.",
    "hair": {
      "color": "Exact color or 'Not visible under [cover]'",
      "style": "Cut/styling or 'Not visible under [cover]'"
    },
    "clothing": {
      "top": {
        "type": "Specific garment type (e.g. layered hoodie under jacket)",
        "color": "Exact matte/gloss shade",
        "details": "Fabric weave, thickness, seams, fit around shoulders/wrists, hood position"
      },
      "bottom": {
        "type": "Specific garment type (e.g. casual sweatpants)",
        "color": "Exact shade and fabric tone",
        "details": "Fabric texture, folds/bunching at knees, silhouette"
      }
    },
    "face": {
      "preserve_original": true,
      "makeup": "Visible cosmetic details or explicit note of unedited natural skin texture with smooth matte finish and zero cosmetics."
    }
  },
  "accessories": {
    "headwear": {
      "type": "Cap/beanie/hat type or 'None'",
      "details": "Material, brim curve, how low it sits over brow, logos"
    },
    "jewelry": {
      "earrings": "Description or 'Not visible / None'",
      "necklace": "Description or 'Not visible / None'",
      "wrist": "Watch/bracelet material, metallic tone, highlights, or 'None'",
      "rings": "Description or 'No rings visible on fingers'"
    },
    "device": {
      "type": "Smartphone, cup, book, or product held",
      "details": "Form factor, orientation, how hands and thumbs are positioned"
    }
  },
  "photography": {
    "camera_style": "e.g. Clean modern smartphone camera photo with soft natural contrast, subtle sensor grain in dark tones.",
    "angle": "Precise camera height and diagonal angle relative to subject torso/face.",
    "shot_type": "Exact framing (e.g. Medium shot from upper thighs to head, candid vertical portrait).",
    "aspect_ratio": "vertical frame, 9:16 or 4:5",
    "texture": "Lighting distribution, soft natural contrast, noise/grain in shadows, ambient surface textures."
  },
  "background": {
    "setting": "Precise environment (e.g. Modern vehicle interior, bedroom corner, minimalist cafe).",
    "wall_color": "Dominant background surface tones or 'No walls present'.",
    "elements": [
      "Granular list of 4-7 specific micro-elements (e.g. leather seat stitching, steering wheel logo, rain droplets on glass, sun visor warning sticker, door handle sheen)"
    ],
    "atmosphere": "Atmospheric mood (e.g. Calm, enclosed, moody overcast day).",
    "lighting": "Direction, source (window daylight, overhead sky), falloff, and specular highlights."
  },
  "weather": {
    "condition": "Overcast daylight / rainy / indoor warm lamp / golden hour",
    "details": "Physical manifestations (droplets on glass, soft diffuse ambient light, wet surfaces)"
  },
  "setting_specifics": {
    "category": "Contextual details (e.g. car interior specifics, cafe furniture, room layout)",
    "materials": "Mix of upholstery, trims, plastics, fabrics"
  },
  "master_prompt_en": "A unified, single-paragraph master diffusion prompt synthesizing the complete composition seamlessly for Imagen 3 / Flux.1."
}
"""

def extract_visual_dna(image_input: Union[str, Path, Image.Image]) -> Dict[str, Any]:
    """
    Executa a engenharia reversa visual de alta fidelidade usando Gemini Vision.
    Retorna o dicionário completo com o DNA visual e o master prompt.
    """
    if isinstance(image_input, (str, Path)):
        img_path = Path(image_input)
        if not img_path.exists():
            raise FileNotFoundError(f"Imagem não encontrada: {img_path}")
        image = Image.open(img_path)
    elif isinstance(image_input, Image.Image):
        image = image_input
    else:
        raise ValueError("Entrada inválida. Forneça o caminho do arquivo ou objeto PIL.Image.")

    model = genai.GenerativeModel("gemini-2.5-flash")
    
    response = model.generate_content(
        [
            MIRROR_SYSTEM_PROMPT,
            "Analyze this reference image now and return ONLY the JSON object with visual reverse engineering:",
            image
        ],
        generation_config={"response_mime_type": "application/json"}
    )
    
    raw_text = response.text.strip()
    
    # Extrai bloco JSON caso venha com markdown
    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if json_match:
        data = json.loads(json_match.group(0))
    else:
        data = json.loads(raw_text)
        
    return data

def save_dna_artifacts(dna_data: Dict[str, Any], prefix: str = "influencer") -> tuple[Path, Path]:
    """
    Salva os artefatos de DNA visual em JSON e o prompt mestre em TXT na pasta de outputs.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_path = OUTPUT_DIR / f"{prefix}_dna_{timestamp}.json"
    prompt_path = OUTPUT_DIR / f"{prefix}_prompt_{timestamp}.txt"
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dna_data, f, indent=2, ensure_ascii=False)
        
    master_prompt = dna_data.get("master_prompt_en", "")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(master_prompt)
        
    return json_path, prompt_path

if __name__ == "__main__":
    import sys
    test_img = sys.argv[1] if len(sys.argv) > 1 else None
    if test_img:
        print(f"[*] Analisando imagem de referência (MIRR0R PRO v2): {test_img}")
        dna = extract_visual_dna(test_img)
        j_path, p_path = save_dna_artifacts(dna)
        print(f"[+] DNA salvo em: {j_path}")
        print(f"[+] Master Prompt salvo em: {p_path}")
        print("\n--- MASTER PROMPT ---")
        print(dna.get("master_prompt_en"))
    else:
        print("Uso: python mirror_engine.py <caminho_da_imagem>")
