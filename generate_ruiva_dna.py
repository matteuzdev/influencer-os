"""
Execução da Engenharia Reversa Visual MIRR0R PRO v2
sobre o frame limpo do Pinterest com a modificação:
Cabelo Ruivo Acobreado Natural (Redhead / Copper Auburn).
"""
import json
import re
from pathlib import Path
from PIL import Image
import google.generativeai as genai
from config import GEMINI_API_KEY, OUTPUT_DIR
from flow_automator import copy_to_clipboard

genai.configure(api_key=GEMINI_API_KEY)

USER_PROMPT_WITH_MODIFICATION = """
Vou te enviar uma imagem para servir como referência-mãe.

Use o SEU fluxo normal de análise visual e engenharia reversa, mas com estas prioridades explícitas:

1. Fidelidade visual absoluta
- Sempre que tiver escolha entre ser genérico ou específico, escolha o específico.
- Descreva o que você vê, não o que você supõe.
- Não tente “embelezar” ou otimizar a cena; o objetivo é capturar com máxima precisão como a imagem realmente é.

2. Detalhamento máximo onde houver informação
- Se a imagem te permite ver textura, nuance de cor, microdetalhes de pele, tecido, reflexo, expressão ou cenário, você deve levar isso em conta nas descrições internas.
- Evite termos vagos como “nice”, “cool”, “beautiful” e prefira descrições concretas de forma, cor, material, luz e expressão.

3. Zero extrapolação de contexto
- Não invente história, localização, marca, época, profissão, relação entre pessoas ou narrativa.
- Trabalhe apenas com o que está visualmente presente no quadro.

4. Idioma da saída
- Mesmo que este comando esteja em português, todas as descrições de texto que você gerar dentro do seu formato de saída padrão devem estar em inglês natural, como se fossem prompts prontos para modelos de geração de imagem.

5. Formato de resposta
- Não me envie explicações em prosa nem comentários.
- Depois de aplicar essas prioridades no seu processamento interno, devolva apenas o seu objeto de saída padrão (o JSON estruturado completo), já ajustado a essas instruções, com todo o conteúdo descritivo em inglês.

MODIFICAÇÃO PRIORITÁRIA SOLICITADA PELO DIRETOR VISUAL:
- A modelo na imagem original tem cabelo loiro, mas você DEVE alterar a característica do cabelo para que ela seja RUIVA (natural vibrant copper-red / warm ginger-auburn hair with realistic undertones, natural hair strands, and subtle flyaways), mantendo o comprimento longo, corte em camadas, textura natural e caimento sobre os ombros exatamente como na referência.
"""

def process_ruiva():
    img_path = Path("influencer_pipeline/inputs/clean_video_frame.png")
    image = Image.open(img_path)
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    print("[*] Enviando imagem de referência e prompt MIRR0R para o Gemini Vision...")
    response = model.generate_content(
        [
            USER_PROMPT_WITH_MODIFICATION,
            image
        ],
        generation_config={"response_mime_type": "application/json"}
    )
    
    raw_text = response.text.strip()
    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if json_match:
        dna_data = json.loads(json_match.group(0))
    else:
        dna_data = json.loads(raw_text)
        
    out_json = OUTPUT_DIR / "influencer_ruiva_dna.json"
    out_txt = OUTPUT_DIR / "influencer_ruiva_prompt.txt"
    
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(dna_data, f, indent=2, ensure_ascii=False)
        
    # Extrai o master prompt ou compila se necessário
    master_prompt = dna_data.get("master_prompt_en")
    if not master_prompt:
        # Compila a partir dos nós se vier no schema aninhado
        subj = dna_data.get("subject", {})
        photo = dna_data.get("photography", {})
        acc = dna_data.get("accessories", {})
        bg = dna_data.get("background", {})
        
        master_prompt = (
            f"{photo.get('camera_style', 'Candid smartphone portrait')}, {photo.get('aspect_ratio', 'vertical 9:16')}. "
            f"{subj.get('description', '')}. "
            f"Hair: {subj.get('hair', {}).get('color', 'copper red')} {subj.get('hair', {}).get('style', '')}. "
            f"Face and skin: {subj.get('face', {}).get('makeup', 'natural unedited skin with visible pores')}. "
            f"Outfit: {subj.get('clothing', {}).get('top', {}).get('details', '')}. "
            f"Jewelry: pearl necklace {acc.get('jewelry', {}).get('necklace', '')}. "
            f"Lighting and setting: {bg.get('lighting', '')}, {bg.get('setting', '')}. "
            f"{photo.get('texture', 'subtle sensor noise, authentic mobile camera capture')}."
        )
        dna_data["master_prompt_en"] = master_prompt
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(dna_data, f, indent=2, ensure_ascii=False)
            
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(master_prompt)
        
    copy_to_clipboard(master_prompt)
    
    print("\n" + "="*60)
    print("[+] DNA VISUAL (MODELO RUIVA) GERADO COM SUCESSO!")
    print("="*60)
    print(json.dumps(dna_data, indent=2, ensure_ascii=False))
    print("\n" + "="*60)
    print("[+] MASTER PROMPT COMPILADO (JÁ COPIADO NO SEU CTRL+V):")
    print(f"\"{master_prompt}\"")
    print("="*60)
    print(f"[+] JSON salvo em: {out_json}")
    print(f"[+] Prompt salvo em: {out_txt}")

if __name__ == "__main__":
    process_ruiva()
