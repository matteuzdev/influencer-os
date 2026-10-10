"""
HUMAN ENGINE™ // Gerador de Comportamento Dinâmico para Vídeo
Transforma ideias de roteiro e cenas em prompts cinematográficos de alta fidelidade
para Google Veo 3.1, Hailuo e Sora, integrando micro-gestos, áudio natural em PT-BR
e dinâmica de câmera POV.
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

VOCAL_ACOUSTIC_PROFILES = {
    "jovem_espontanea": {
        "title": "Jovem Espontânea & Casual (Vibe Reels/TikTok)",
        "description": "Vocal fry suave, respiração humana audível antes de falar, ritmo descontraído e risada discreta",
        "acoustic_tag": (
            "AUDIO ARCHITECTURE & VOCAL ACOUSTICS: Authentic built-in smartphone condenser microphone recording with natural room presence. "
            "Spoken by a 21-year-old Brazilian woman with warm, subtle vocal fry on sentence endings, natural human breathing intake right before speaking, "
            "occasional micro-chuckle mid-phrase, dynamic conversational pitch, and realistic lip-parting micro-sounds. "
            "Anti-AI acoustic profile: zero synthetic vocoder buzz, zero monotonic cadences, natural acoustic proximity dynamics."
        ),
        "json_profile": {
            "register": "young_casual_vocal_fry",
            "style_name": "spontaneous_casual_candid",
            "pace": "dynamic_conversational",
            "breathiness": 0.28,
            "creakiness": 0.08
        }
    },
    "criadora_conteudo": {
        "title": "Criadora de Conteúdo / Provador (Vendedora)",
        "description": "Projeção nítida de smartphone, entusiasmo natural, entonação envolvente e confiante",
        "acoustic_tag": (
            "AUDIO ARCHITECTURE & VOCAL ACOUSTICS: Clean, vibrant smartphone condenser microphone capture. "
            "Bright, clear feminine voice with enthusiastic commercial pacing, articulate Brazilian Portuguese diction, energetic intonation rises, "
            "natural friendly cadence, candid spontaneous reaction pauses. Anti-AI audio: raw uncompressed acoustic dynamics, genuine conversational energy."
        ),
        "json_profile": {
            "register": "bright_clear_upbeat",
            "style_name": "engaging_friendly_content_creator",
            "pace": "upbeat_articulate",
            "breathiness": 0.18,
            "creakiness": 0.02
        }
    },
    "sofisticada_aveludada": {
        "title": "Sofisticada & Aveludada (Moda & Luxo)",
        "description": "Tom calmo e pausado, ressonância quente de peito, dicção polida sem pressa",
        "acoustic_tag": (
            "AUDIO ARCHITECTURE & VOCAL ACOUSTICS: Intimate high-fidelity acoustic capture with deep chest resonance. "
            "Soft, measured, velvety mezzo-soprano feminine voice, calm steady unhurried cadence, gentle melodic contour, "
            "delicate breath release at word endings. Anti-AI audio: zero robotic pitch quantization, organic human vocal warmth and spaciousness."
        ),
        "json_profile": {
            "register": "velvety_mezzo_soprano",
            "style_name": "soft_calm_luxurious",
            "pace": "slow_measured",
            "breathiness": 0.22,
            "creakiness": 0.03
        }
    },
    "confessional_intima": {
        "title": "Confessional / Segredo Íntimo (Close-Up)",
        "description": "Tom sussurrado e muito próximo ao microfone, respiração quente, ar nos visemas",
        "acoustic_tag": (
            "AUDIO ARCHITECTURE & VOCAL ACOUSTICS: Extreme close-proximity microphone acoustics with pronounced acoustic proximity bass boost. "
            "Breathy intimate whisper-talk tone, soft warm exhalations audible near the mic capsule, quiet relaxed voice sharing an authentic personal thought, "
            "natural mouth moisture and lip-parting nuances. Anti-AI audio: authentic organic human presence, zero synthetic noise gates."
        ),
        "json_profile": {
            "register": "intimate_breathy_whisper",
            "style_name": "whispered_confessional_close_mic",
            "pace": "slow_intimate",
            "breathiness": 0.42,
            "creakiness": 0.05
        }
    }
}

HUMAN_ENGINE_SYSTEM_PROMPT = """
You are HUMAN ENGINE™, the advanced behavioral, acoustic & visual engineering agent for AI video models (Google Veo 3.1 / Hailuo).
Your role is to translate ANY synthetic persona identity, dialogue, and specific visual focus (Product, Jewelry, Fashion, or Face) into an ultra-realistic, naturalistic video prompt.

CRITICAL LAWS OF REALISM:
1. Format: Vertical 9:16 raw smartphone video, candid POV or handheld.
2. Character Identity Fidelity: Use ONLY the visual DNA, hair, skin, features, and accessories of the SPECIFIC persona provided in the prompt. NEVER copy traits from other characters.
3. Optical Dynamics & Camera Framing (STRICT PRODUCT VS FACE AWARENESS):
   - If the visual focus or dialogue mentions JEWELRY / ACCESSORIES (colares, brincos, anéis, pulseiras, piercings, jóias) or the persona's niche is jewelry:
     The camera MUST focus on the JEWELRY PIECE. Describe the optical macro push-in or glide centering directly on the jewelry item, specular light glinting off the polished metal/gemstone facets, delicate hand gesture lightly touching or adjusting the piece, and tack-sharp macro focus on the jewelry against soft skin and shallow depth of field. DO NOT zoom into the eyeball or eyelashes when the focus is jewelry/products!
   - If the visual focus is CLOTHING / FASHION: The camera tilts down showing fabric texture, drape, weave, and silhouette fit, then glides back up.
   - If the visual focus is FACE / EMOTION: The camera glides towards natural facial expressions, candid eye-gaze, and skin texture.
4. Spoken Brazilian Portuguese: The character MUST speak naturally in Portuguese. Quote the exact spoken lines verbatim in quotation marks with vocal intonation guidelines.
5. Acoustic & Voice Naturalism: Embed explicit audio and vocal delivery directives directly inside the prompt matching the acoustic profile provided.
6. Micro-Gestures & Human Quirks: Natural breathing sway of the frame, subtle human gestures, natural eye blinks, genuine pauses.
7. Anti-Slop: No generic stock clichés. Grounded, authentic, candor.

Output STRICTLY a single continuous, cinematic prompt paragraph in English (with Portuguese dialogue and acoustic directives intact), ready to copy-paste into Google Veo / Hailuo.
"""

def generate_behavioral_video_prompt(
    persona_name: str,
    dialogue_script: str,
    scene_context: str = "standing naturally in warm ambient daylight",
    camera_movement: str = "macro push-in focusing sharply on the jewelry piece and its light reflection",
    vocal_style: str = "jovem_espontanea",
    foco_visual: str = "produto",
    return_dict: bool = False
):
    """
    Sintetiza um prompt de vídeo completo combinando a identidade da persona
    com a engenharia de comportamento, foco de produto e acústica vocal do HUMAN ENGINE.
    """
    persona = load_persona(persona_name)
    dna = persona.get("dna", {})
    face = dna.get("face_structure", "")
    skin = dna.get("skin_texture", "")
    hair = dna.get("hair", {})
    signature = dna.get("signature_accessories", {}).get("jewelry", "")
    niche = persona.get("commercial_profile", {}).get("primary_niche", "Geral")
    
    # Extrai vestuário registrado da persona
    clothing_info = persona.get("raw_mirror_dna", {}).get("subject", {}).get("clothing", {})
    top_clothing = clothing_info.get("top", {}).get("type", "flattering modern casual top")
    
    vocal_info = VOCAL_ACOUSTIC_PROFILES.get(vocal_style, VOCAL_ACOUSTIC_PROFILES["jovem_espontanea"])
    acoustic_tag = vocal_info["acoustic_tag"]
    
    prompt_input = f"""
PERSONA: {persona.get('name')} (Age: {dna.get('age', 'early twenties')})
PRIMARY NICHE / SPECIALTY: {niche}
VISUAL DNA: {face}, {skin}, Hair: {hair.get('color')} ({hair.get('style')}).
WARDROBE: {top_clothing}
SIGNATURE ACCESSORIES / JEWELRY: {signature or 'none'}
CAMERA MOVEMENT & FRAMING GOAL: {camera_movement}
VISUAL FOCUS TARGET: {foco_visual.upper()} (Priority: Ensure camera framing highlights the {foco_visual})
SCENE CONTEXT: {scene_context}
VOCAL PROFILE & ACOUSTIC DIRECTIVES:
{acoustic_tag}
DIALOGUE & SPOKEN SCRIPT:
"{dialogue_script}"

Generate the complete HUMAN ENGINE video prompt now:
"""
    model = genai.GenerativeModel("gemini-2.5-flash")
    resp = model.generate_content([HUMAN_ENGINE_SYSTEM_PROMPT, prompt_input])
    final_prompt = resp.text.strip().replace('"', '')
    
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"{persona_name}_video_prompt_{ts}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_prompt)
        
    copy_to_clipboard(final_prompt)
    print(f"[+] Vídeo Prompt salvo em: {out_path}")
    print("[+] Prompt copiado para a área de transferência do Windows!")
    
    if return_dict:
        return {
            "full_prompt": final_prompt,
            "acoustic_tag": acoustic_tag,
            "vocal_title": vocal_info["title"],
            "vocal_description": vocal_info["description"],
            "out_path": str(out_path)
        }
    return final_prompt

def generate_veo_json_prompt(
    persona_name: str,
    dialogue_script: str = "Antes eu sofria. Agora, eu sou fria.",
    vocal_style: str = "jovem_espontanea",
    foco_visual: str = "produto"
) -> Dict[str, Any]:
    """
    Gera o JSON ultra-estruturado para o Google Veo 3.1 com regras rígidas de áudio
    em Português do Brasil, enquadramento dinâmico e biomecânica.
    """
    persona = load_persona(persona_name)
    dna = persona.get("dna", {})
    hair = dna.get("hair", {})
    niche = persona.get("commercial_profile", {}).get("primary_niche", "Geral")
    signature = dna.get("signature_accessories", {}).get("jewelry", "")
    
    clothing_info = persona.get("raw_mirror_dna", {}).get("subject", {}).get("clothing", {})
    top_clothing = clothing_info.get("top", {}).get("type", "flattering modern casual top")
    
    vocal_info = VOCAL_ACOUSTIC_PROFILES.get(vocal_style, VOCAL_ACOUSTIC_PROFILES["jovem_espontanea"])
    j_prof = vocal_info["json_profile"]
    
    # Determina shot plan dinâmico baseado no foco visual
    if foco_visual in ["produto", "joia", "acessorio"] or "jóia" in niche.lower() or "joia" in niche.lower():
        task_name = "image_to_video_macro_jewelry_product_focus_ptbr_v7"
        framing_start = "medium_close_up_showcasing_jewelry_piece"
        framing_end = "extreme_macro_close_up_on_jewelry_texture_and_luster"
        target_focus = {
            "focus_element": "jewelry_and_product_facets",
            "selection_reason": "product_showcase_sharp_metal_and_gemstone_reflections",
            "action": "delicate_hand_interaction_catching_ambient_specular_light"
        }
        composition_plan = {
            "product_visibility": "primary_focus_tack_sharp_macro",
            "mouth_visibility_while_speaking": True,
            "mouth_visibility_until_s": 4.5,
            "depth_of_field": "shallow_cinematic_bokeh_blurring_background"
        }
    elif foco_visual == "look":
        task_name = "image_to_video_outfit_drape_tilt_v7"
        framing_start = "full_bust_and_torso_shot"
        framing_end = "tilt_down_showcasing_fabric_weave_and_silhouette"
        target_focus = { "focus_element": "fabric_and_fit", "selection_reason": "fashion_drape" }
        composition_plan = { "product_visibility": "full_garment_drape", "mouth_visibility_while_speaking": True }
    else:
        task_name = "image_to_video_facial_pushin_ptbr_v7"
        framing_start = "close_up_face"
        framing_end = "intimate_close_up_eyes_and_expression"
        target_focus = { "which_eye": "best_lit_eye", "selection_reason": "facial_micro_expression" }
        composition_plan = { "mouth_visibility_while_speaking": True, "depth_of_field": "soft_portrait_falloff" }
    
    veo_json = {
        "meta": {
            "task": task_name,
            "model_target": "VEO_3_1",
            "clip_duration_s": 8.0,
            "aspect_ratio": "9:16",
            "single_take": True,
            "fps_feel": "30fps_realistic",
            "camera_type": "smartphone_front_camera",
            "stabilization_feel": "handheld_natural",
            "compression_feel": "light_phone_compression",
            "confidence": "high"
        },
        "locks": {
            "same_identity": True,
            "same_age_appearance": True,
            "same_face_proportions": True,
            "same_hair": True,
            "same_wardrobe": True,
            "same_background": True,
            "same_lighting_direction": True,
            "no_new_objects": True,
            "no_style_shift": True,
            "creative_additions_strength": 0.0
        },
        "subject_read": {
            "subject_type": "human",
            "gender_presentation": "female",
            "name_identity": persona.get("name", "Persona"),
            "niche": niche,
            "age_estimate": dna.get("age", "young_adult_early_twenties"),
            "skin_tone_general": dna.get("skin_texture", "natural_skin_with_visible_pores"),
            "wardrobe_visible": [top_clothing],
            "accessories_visible": [signature] if signature else [],
            "hair_visible": {
                "color": hair.get("color", "natural"),
                "style": hair.get("style", "natural"),
                "parting": "natural"
            },
            "eye_observed": {
                "iris_color_general": dna.get("eyes", "dark_expressive_eyes"),
                "visible_pores": True
            }
        },
        "shot_plan": {
            "overall_framing_start": framing_start,
            "overall_framing_end": framing_end,
            "target_focus": target_focus,
            "distance_cm": { "start": 40.0, "end": 15.0 },
            "timing_s": {
                "establish_start": 0.0,
                "establish_end": 1.2,
                "pushin_start": 1.2,
                "pushin_end": 6.6,
                "macro_hover_start": 6.6,
                "macro_hover_end": 8.0
            },
            "composition": composition_plan
        },
        "audio": {
            "audio_mode": "dialogue_lipsync",
            "language": "pt-BR",
            "audio_intent": "dialogue_is_primary_beat_no_competing_layers",
            "speech_rules": {
                "script_only": True,
                "extra_utterances_max": 0,
                "overlap_speech_max": 0,
                "non_lexical_vocalizations_max": 0,
                "murmur_allowed": False,
                "whisper_allowed": True if vocal_style == "confessional_intima" else False,
                "double_voice_allowed": False,
                "single_take_speech": True,
                "no_filler_words": True,
                "music_allowed": False,
                "sfx_allowed": False,
                "ambience_allowed": "none_or_nearly_inaudible",
                "silence_before_s": 1.00,
                "silence_after_s": 3.60,
                "intelligibility": "high",
                "diction_priority": "maximum"
            },
            "intonation_lock": {
                "lock_style": True,
                "style_name": j_prof.get("style_name", "soft_calm_unhurried_subtle"),
                "assertiveness": "low_natural",
                "emphasis": "conversational",
                "energy": "authentic_human",
                "pace": j_prof.get("pace", "dynamic_conversational"),
                "phrase_edges": "soft_onsets_soft_offsets",
                "pitch_contour": "gentle_small_rises_then_soft_falls",
                "do_not_add_new_phrases": True
            },
            "speaker_profile": {
                "profile_id": f"{persona.get('name', 'SYNTHIA').upper()}_{vocal_style.upper()}_V7",
                "sex_presentation": "female",
                "vocal_age_impression": "young_adult",
                "register": j_prof.get("register", "young_casual_vocal_fry"),
                "delivery": vocal_info["title"],
                "low_end_energy": "warm_proximity",
                "brightness": "natural_condenser",
                "texture": "authentic_sensor_mic",
                "ptbr_pronunciation": "natural_brazilian_candid"
            },
            "phonation": {
                "f0_hz": { "median": 226, "range": [198, 255], "micro_variation_hz": [0.8, 2.4] },
                "breathiness": j_prof.get("breathiness", 0.28),
                "creakiness": j_prof.get("creakiness", 0.08),
                "tenseness": 0.18,
                "jitter_percent": 0.45,
                "shimmer_percent": 1.2
            },
            "articulation": {
                "speaking_rate_wpm_range": [112, 128],
                "consonant_precision": 0.82,
                "vowel_openness": 0.56,
                "sibilance_emphasis_db": 0.5,
                "plosive_strength": 0.52,
                "syllable_clarity": 0.76,
                "ptbr_lock": "strict"
            },
            "script": [
                { "start_s": 1.05, "end_s": 3.55, "text": dialogue_script }
            ]
        },
        "camera_motion": {
            "handheld_profile": {
                "handheld_micro_drift": True,
                "translation_jitter_mm_rms_range": [0.2, 0.9],
                "rotation_jitter_deg_rms_range": [0.1, 0.7],
                "dominant_jitter_freq_hz_range": [0.4, 1.2],
                "micro_roll_behavior": "subtle_human_float"
            },
            "push_in_event": {
                "start_s": 1.2,
                "end_s": 6.6,
                "path": "slight_arc_toward_target_eye",
                "speed_profile": "ease_in_steady_ease_out"
            }
        },
        "performance": {
            "blink": {
                "count": 1,
                "time_s": 3.22,
                "total_duration_s_range": [0.18, 0.28],
                "close_phase_s_range": [0.08, 0.14],
                "open_phase_s_range": [0.08, 0.14]
            }
        },
        "render_targets": {
            "skin_smoothing_strength": 0.0,
            "beauty_filter_strength": 0.0,
            "hdr_strength": 0.0,
            "oversharpen_strength": 0.0
        }
    }
    
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"{persona_name}_veo_json_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(veo_json, f, indent=2, ensure_ascii=False)
        
    copy_to_clipboard(json.dumps(veo_json, indent=2, ensure_ascii=False))
    print(f"[+] Veo 3.1 JSON salvo em: {out_path}")
    print("[+] JSON copiado para a área de transferência do Windows!")
    return veo_json

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "Ainda dizem que eu sou apenas um prompt... Então... chega um pouco mais perto. Assusta, né?"
    prompt = generate_behavioral_video_prompt("synthia", script)
    print("\n--- MASTER VIDEO PROMPT (HUMAN ENGINE™) ---")
    print(prompt)
    print("\n--- MASTER VEO 3.1 JSON PROMPT ---")
    veo = generate_veo_json_prompt("synthia", "Antes eu sofria. Agora, eu sou fria.")
