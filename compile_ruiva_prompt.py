import json
from pathlib import Path
from config import OUTPUT_DIR
from flow_automator import copy_to_clipboard

json_path = OUTPUT_DIR / "influencer_ruiva_dna.json"
txt_path = OUTPUT_DIR / "influencer_ruiva_prompt.txt"

with open(json_path, "r", encoding="utf-8") as f:
    dna = json.load(f)

# Compilação cirúrgica e rica de todos os nós extraídos pelo MIRR0R
compiled_prompt = (
    "A candid vertical 9:16 smartphone front-camera portrait of a young woman in her early twenties with fair skin and natural unedited skin texture, visible soft pores, and minimal makeup. "
    "She has long, vibrant natural copper-red and warm ginger-auburn hair with realistic undertones, cut in soft natural layers falling over both shoulders and framing her face with delicate flyaways. "
    "She has an oval facial structure, well-defined dark brows, a small slightly upturned nose, and naturally full soft pink lips slightly parted in a relaxed, candid expression, looking directly into the camera lens with a soft, confident gaze. "
    "She is wearing a form-fitting, long-sleeved off-white crewneck top in a smooth, subtle heathered knit fabric, paired with a delicate pearl choker necklace featuring a central silver orb and ring pendant. "
    "The composition is a medium close-up framed from the chest up, shot from a slightly low angle. "
    "Setting is a bright, minimalist modern room with soft, diffused natural daylight coming from an adjacent window with sheer white curtains, creating gentle shadows and a heavily blurred, clean neutral background. "
    "Authentic mobile video still aesthetic, subtle natural sensor noise, unedited candid realism, zero artificial airbrushing."
)

dna["master_prompt_en"] = compiled_prompt

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(dna, f, indent=2, ensure_ascii=False)

with open(txt_path, "w", encoding="utf-8") as f:
    f.write(compiled_prompt)

copy_to_clipboard(compiled_prompt)
print("[+] Master Prompt compilado e atualizado com sucesso no JSON, TXT e Clipboard!")
