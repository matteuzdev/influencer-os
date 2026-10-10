"""
Motor de Variação de Cenas para Personagens Fixas (Persona Engine)
Permite gerar novas fotos para uma influenciadora existente mantendo 100% da identidade
facial e visual travada, alterando apenas cenário, roupa, pose e iluminação.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import google.generativeai as genai
from config import BASE_DIR, GEMINI_API_KEY, OUTPUT_DIR
from flow_automator import copy_to_clipboard

import os
import tempfile

IS_VERCEL = os.environ.get("VERCEL") == "1"
PERSONAS_DIR = BASE_DIR / "personas"
PERSONAS_TMP_DIR = Path(tempfile.gettempdir()) / "personas" if IS_VERCEL else None

try:
    PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
    if PERSONAS_TMP_DIR:
        PERSONAS_TMP_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def load_persona(persona_name: str = "synthia") -> Dict[str, Any]:
    """Carrega o registro JSON de uma persona pelo nome/id."""
    clean_name = persona_name.lower().strip()
    persona_file = PERSONAS_DIR / f"{clean_name}.json"
    if not persona_file.exists() and PERSONAS_TMP_DIR:
        persona_file = PERSONAS_TMP_DIR / f"{clean_name}.json"
    if not persona_file.exists():
        available = [p.stem for p in PERSONAS_DIR.glob("*.json")]
        if PERSONAS_TMP_DIR and PERSONAS_TMP_DIR.exists():
            available.extend([p.stem for p in PERSONAS_TMP_DIR.glob("*.json")])
        raise FileNotFoundError(
            f"Persona '{persona_name}' não encontrada. Personagens disponíveis: {available}"
        )
    with open(persona_file, "r", encoding="utf-8") as f:
        return json.load(f)

def list_available_personas() -> list[str]:
    """Retorna lista de nomes de personas cadastradas."""
    names = [p.stem for p in PERSONAS_DIR.glob("*.json")]
    if PERSONAS_TMP_DIR and PERSONAS_TMP_DIR.exists():
        names.extend([p.stem for p in PERSONAS_TMP_DIR.glob("*.json")])
    return sorted(list(set(names)))

def build_persona_scene_prompt(
    persona_data: Dict[str, Any],
    scene_brief: str,
    aspect_ratio: str = "9:16"
) -> str:
    """
    Usa o Gemini para sintetizar o novo prompt da cena, blindando a consistência
    do rosto, cabelo e assinatura visual da persona.
    """
    dna = persona_data.get("dna", {})
    face = dna.get("face_structure", "")
    skin = dna.get("skin_texture", "")
    hair = dna.get("hair", {})
    hair_desc = f"{hair.get('color', '')}, {hair.get('style', '')}"
    signature = dna.get("signature_accessories", {}).get("jewelry", "")
    cam = dna.get("photography_dna", {}).get("camera", "smartphone front camera")
    tex = dna.get("photography_dna", {}).get("texture", "subtle sensor noise")

    system_instruction = f"""
You are the Identity Guardian for the synthetic influencer '{persona_data.get('name', 'Synthia')}'.
Your goal is to generate a master diffusion prompt for a NEW photo scene while strictly locking her facial and physical identity.

LOCKED IDENTITY (DO NOT CHANGE):
- Apparent Age: {dna.get('age', 'early twenties')}
- Facial Structure: {face}
- Skin: {skin}
- Hair: {hair_desc}
- Eyes: {dna.get('eyes', 'dark candid eyes')}
- Signature Jewelry (Include unless explicitly stated otherwise): {signature}
- Camera Simulation: {cam}, vertical {aspect_ratio}, {tex}

NEW SCENE BRIEF FROM USER:
"{scene_brief}"

INSTRUCTIONS:
1. Synthesize a single, continuous, fluent paragraph in English photography terms for Imagen 3 / Flux.1.
2. Integrate the new requested outfit, activity, setting, and lighting from the user brief.
3. Keep the locked identity attributes 100% intact.
4. Ban AI buzzwords (never write 'beautiful', 'hyperrealistic', '4k').
5. Output ONLY the compiled prompt paragraph, no quotes, no conversational filler.
"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content(system_instruction)
    prompt = resp.text.strip().replace('"', '')
    return prompt

def build_persona_continuity_package(
    persona_name: str,
    scene_brief: str,
    aspect_ratio: str = "9:16",
    lighting: str = "luz natural suave"
) -> Dict[str, Any]:
    """
    CAMINHO 1: Gera o pacote completo de continuidade para uma persona existente.
    Trava 100% da identidade facial, gerando:
    1. Prompt MIRR0R JSON para a Coleção no Google Flow
    2. Master Prompt Contínuo em Inglês (Imagen 3 / Flux.1)
    3. Roteiro Comportamental para Veo 3.1 (HUMAN ENGINE™)
    """
    persona = load_persona(persona_name)
    dna = persona.get("dna", {})
    name = persona.get("name", "Synthia")
    
    hair = dna.get("hair", {})
    hair_desc = f"{hair.get('color', 'copper red')}, {hair.get('style', 'long layered')}"
    signature = dna.get("signature_accessories", {}).get("jewelry", "")
    
    # 1. Prompt em JSON estruturado para a Coleção do Flow
    flow_json = {
        "subject": {
            "type": "person",
            "character_name": name,
            "face": {
                "preserve_original": True,
                "facial_identity": f"Strictly maintain facial structure and facial identity of {name}",
                "facial_features": dna.get("face_structure", "oval face, delicate jawline"),
                "skin_texture": dna.get("skin_texture", "natural skin texture with visible soft pores, unedited"),
                "eyes": dna.get("eyes", "dark expressive eyes, natural catchlight"),
                "hair": hair_desc
            },
            "scene_action": scene_brief,
            "signature_accessories": signature or "none",
            "expression": "candid, natural, relaxed and confident gaze into camera lens"
        },
        "photography": {
            "camera_style": "candid smartphone photo / high-end mobile capture",
            "aspect_ratio": f"{aspect_ratio} vertical portrait" if "9:16" in aspect_ratio else f"{aspect_ratio} format",
            "focal_length": "28mm equivalent",
            "texture": "subtle sensor noise, authentic unedited photographic realism, zero airbrushing"
        },
        "lighting": {
            "type": lighting,
            "quality": "soft natural shadows, organic light falloff, gentle highlights"
        },
        "setting": scene_brief
    }
    
    # 2. Master Prompt Fotográfico em Inglês
    master_prompt = build_persona_scene_prompt(persona, scene_brief, aspect_ratio)
    
    # 3. Roteiro Comportamental Veo 3.1
    from human_engine import generate_behavioral_video_prompt
    veo_prompt = generate_behavioral_video_prompt(
        persona_name=persona_name,
        dialogue_script=f"Oi gente! Mostrando aqui em primeira mão esse momento especial. O que vocês acharam dessa composição?",
        scene_context=scene_brief,
        camera_movement="slow push-in gliding towards her face, capturing natural micro-expressions and eye blink"
    )
    
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cena_dir = OUTPUT_DIR / f"cena_{persona_name}_{ts}"
    cena_dir.mkdir(parents=True, exist_ok=True)
    
    with open(cena_dir / "01_prompt_flow_colecao.json", "w", encoding="utf-8") as f:
        json.dump(flow_json, f, indent=2, ensure_ascii=False)
        
    with open(cena_dir / "02_master_prompt_imagem.txt", "w", encoding="utf-8") as f:
        f.write(master_prompt)
        
    with open(cena_dir / "03_roteiro_veo_humano.txt", "w", encoding="utf-8") as f:
        f.write(veo_prompt)
        
    copy_to_clipboard(json.dumps(flow_json, indent=2))
    
    return {
        "status": "success",
        "persona_id": persona_name,
        "persona_name": name,
        "collection_url": persona.get("commercial_profile", {}).get("collection_url", ""),
        "flow_json": flow_json,
        "master_prompt": master_prompt,
        "veo_prompt": veo_prompt,
        "output_dir": str(cena_dir)
    }

def create_new_persona_pipeline(
    name: str,
    niche: str,
    reference_image_path: str,
    signature_accessory: str = ""
) -> Dict[str, Any]:
    """
    CAMINHO 2: Cold Start - Criação de Nova Persona do Zero (Aulas 1 a 4).
    1. Executa análise de DNA visual no Gemini Vision via MIRR0R Engine
    2. Gera o Prompt da Imagem Matriz (Ground Truth 9:16)
    3. Gera o Prompt do Face Board Collage 16:9 (painel multi-ângulo para registrar Face Lock no Flow)
    4. Cria o arquivo personas/{slug}.json automaticamente
    """
    import re
    from datetime import datetime
    from mirror_engine import extract_visual_dna
    
    clean_name = name.strip()
    slug = re.sub(r'[^a-z0-9_]', '', clean_name.lower().replace(' ', '_'))
    if not slug:
        slug = "nova_persona"
        
    ref_path = Path(reference_image_path)
    if not ref_path.exists():
        raise FileNotFoundError(f"Imagem de referência não encontrada: {reference_image_path}")
        
    print(f"[*] CAMINHO 2: Analisando imagem de referência para nova persona '{clean_name}'...")
    dna_raw = extract_visual_dna(ref_path)
    
    subj = dna_raw.get("subject", {})
    photo = dna_raw.get("photography", {})
    acc = dna_raw.get("accessories", {})
    bg = dna_raw.get("background", {})
    
    hair = subj.get("hair", {})
    hair_color = hair.get("color", "natural tone")
    hair_style = hair.get("style", "long layered hair")
    
    face_structure = subj.get("description", "harmonious facial symmetry, expressive features")
    skin_texture = subj.get("face", {}).get("makeup", "natural unedited skin with visible fine pores, soft authentic dermal glow")
    age_str = subj.get("age", "young adult in early twenties")
    
    sig_jewelry = signature_accessory.strip() if signature_accessory else (acc.get("jewelry", {}).get("necklace") or acc.get("jewelry", {}).get("earrings") or "delicate minimalist jewelry")
    
    # 1. Master Prompt Ground Truth (9:16)
    master_prompt = (
        f"A candid vertical 9:16 smartphone front-camera portrait of a young woman ({age_str}) named {clean_name}. "
        f"{face_structure}. "
        f"Hair: {hair_color}, {hair_style} framing the face naturally. "
        f"Skin: {skin_texture}. "
        f"Wearing signature accessory: {sig_jewelry}. "
        f"Setting: {bg.get('setting', 'bright modern space with soft natural daylight')}. "
        f"Authentic unedited smartphone photo aesthetic, subtle sensor texture, natural eye catchlight, zero airbrushing or plastic smoothing."
    )
    
    # 2. Face Board Collage 16:9 Prompt (O segredo da Aula 4 para treinar o Flow)
    face_board_prompt = (
        f"A 16:9 high-resolution photographic multi-panel character reference board and face collage showcasing the EXACT SAME woman ({clean_name}, {age_str}) from 9 distinct camera angles and candid facial expressions: "
        f"Panel 1 centered front portrait smiling softly; "
        f"Panel 2 three-quarter left angle candid laughing; "
        f"Panel 3 three-quarter right angle looking thoughtfully; "
        f"Panel 4 clean side profile showcasing jawline and nose silhouette; "
        f"Panel 5 looking down candidly with relaxed eyelids; "
        f"Panel 6 macro extreme close-up on natural skin texture, visible soft pores, and dark expressive eyes; "
        f"Panel 7 speaking candidly with parted lips; "
        f"Panel 8 upper bust framing showing hair drape; "
        f"Panel 9 confident direct eye contact. "
        f"LOCKED TRAITS ACROSS ALL PANELS: {hair_color} hair in {hair_style}, identical facial bone structure, {skin_texture}, and wearing {sig_jewelry}. "
        f"Seamless neutral off-white studio background, uniform diffuse daylight illumination, 100% facial and physical identity consistency across every single panel. "
        f"Authentic unedited camera capture, zero artificial airbrushing, photorealistic fidelity."
    )
    
    persona_dict = {
        "id": slug,
        "name": clean_name,
        "archetype": f"Influenciadora Digital IA // {niche}",
        "concept": f"Persona virtual autônoma criada para o nicho de {niche}, com fidelidade visual e Face Lock registrado.",
        "commercial_profile": {
            "primary_niche": niche,
            "target_clients": f"Marcas, lojas e marcas parceiras de {niche}",
            "positioning": f"Embaixadora virtual hiper-realista para campanhas de {niche}, provadores e vídeos falados",
            "collection_url": "",
            "deliverables": [
                "Provador Virtual (OOTD) em proporção 9:16",
                "Demonstração Técnica de Produto 1:1",
                "Vídeos de Avaliação UGC Falados (HUMAN ENGINE™ em PT-BR)",
                "Motion Transfer de Ação Real (RunningHub ComfyUI)"
            ]
        },
        "ground_truth_image": str(ref_path),
        "face_board_prompt": face_board_prompt,
        "dna": {
            "age": age_str,
            "face_structure": face_structure,
            "skin_texture": skin_texture,
            "eyes": "dark expressive eyes, candid direct gaze with natural light reflection",
            "hair": {
                "color": hair_color,
                "style": hair_style,
                "texture": "natural authentic strands with realistic physics"
            },
            "signature_accessories": {
                "jewelry": sig_jewelry
            },
            "photography_dna": {
                "camera": photo.get("camera_style", "candid modern smartphone photo"),
                "texture": photo.get("texture", "subtle natural sensor noise, unedited daylight capture")
            }
        },
        "raw_mirror_dna": dna_raw,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Salva personas/{slug}.json
    persona_file = PERSONAS_DIR / f"{slug}.json"
    try:
        with open(persona_file, "w", encoding="utf-8") as f:
            json.dump(persona_dict, f, indent=2, ensure_ascii=False)
    except Exception:
        if PERSONAS_TMP_DIR:
            persona_file = PERSONAS_TMP_DIR / f"{slug}.json"
            with open(persona_file, "w", encoding="utf-8") as f:
                json.dump(persona_dict, f, indent=2, ensure_ascii=False)
        
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUT_DIR / f"nova_persona_{slug}_{ts}"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / "01_dna_completo.json", "w", encoding="utf-8") as f:
            json.dump(persona_dict, f, indent=2, ensure_ascii=False)
        with open(out_dir / "02_prompt_matriz_ground_truth.txt", "w", encoding="utf-8") as f:
            f.write(master_prompt)
        with open(out_dir / "03_prompt_face_board_collage_16x9.txt", "w", encoding="utf-8") as f:
            f.write(face_board_prompt)
    except Exception:
        pass
        
    copy_to_clipboard(face_board_prompt)
    
    return {
        "status": "success",
        "persona": persona_dict,
        "slug": slug,
        "master_prompt": master_prompt,
        "face_board_prompt": face_board_prompt,
        "persona_file": str(persona_file),
        "output_dir": str(out_dir)
    }

def generate_scene_for_persona(
    persona_name: str,
    scene_brief: str,
    auto_generate: bool = False
) -> Dict[str, Any]:
    """
    Gera o prompt para a cena de uma persona fixa e opcionalmente dispara a geração.
    """
    return build_persona_continuity_package(persona_name, scene_brief)

if __name__ == "__main__":
    import sys
    brief = sys.argv[1] if len(sys.argv) > 1 else "sitting at an outdoor Parisian cafe table drinking an iced matcha latte on a sunny morning"
    res = generate_scene_for_persona("synthia", brief, auto_generate=False)
    print("\n--- MASTER PROMPT PARA SYNTHIA ---")
    print(res["master_prompt"])

