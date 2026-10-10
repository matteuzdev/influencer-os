"""
INFLUENCER STUDIO AI™ // Servidor Central & Dashboard Completo (Aulas 1 a 11)
Interface web visual e 100% automatizada cobrindo:
- Aulas 1 a 4: Curadoria, MIRR0R DNA e Face Lock da Synthia
- Aulas 5 e 6: HUMAN ENGINE™ & Vídeos Falados para Veo 3.1
- Aulas 7 e 8: Provador Virtual de Produtos para Lojas & E-commerce
- Aulas 9 a 11: Motion Transfer (RunningHub) e Color Grading CapCut
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import tempfile

BASE_DIR = Path(__file__).resolve().parent
IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    temp_dir = Path(tempfile.gettempdir())
    OUTPUT_DIR = temp_dir / "outputs"
    INPUTS_DIR = temp_dir / "inputs"
    PERSONAS_TMP_DIR = temp_dir / "personas"
else:
    OUTPUT_DIR = BASE_DIR / "outputs"
    INPUTS_DIR = BASE_DIR / "inputs"
    PERSONAS_TMP_DIR = None

PERSONAS_DIR = BASE_DIR / "personas"

try:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
    if PERSONAS_TMP_DIR:
        PERSONAS_TMP_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass

# Motores
from persona_engine import list_available_personas, load_persona, build_persona_continuity_package, create_new_persona_pipeline
from provar_produto_synthia import gerar_campanha_produto, gerar_campanha_produto_synthia
from human_engine import generate_behavioral_video_prompt, generate_veo_json_prompt

app = FastAPI(title="Influencer Studio AI", version="1.0.0")

app.mount("/static_outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")
app.mount("/static_inputs", StaticFiles(directory=str(INPUTS_DIR)), name="inputs")

@app.get("/api/personas")
def get_personas():
    personas = []
    seen = set()
    dirs_to_scan = [PERSONAS_DIR]
    if PERSONAS_TMP_DIR and PERSONAS_TMP_DIR.exists():
        dirs_to_scan.append(PERSONAS_TMP_DIR)
    for pdir in dirs_to_scan:
        for f in pdir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    pid = data.get("id") or f.stem
                    if pid not in seen:
                        seen.add(pid)
                        personas.append(data)
            except Exception:
                pass
    return personas

@app.post("/api/persona/gerar-cena")
async def gerar_cena_persona_endpoint(
    persona_id: str = Form("synthia"),
    cenario: str = Form(...),
    proporcao: str = Form("9:16"),
    estilo_luz: str = Form("luz natural suave de janela")
):
    """Caminho 1: Gera nova cena com Face Lock para persona existente"""
    try:
        resultado = build_persona_continuity_package(
            persona_name=persona_id,
            scene_brief=cenario,
            aspect_ratio=proporcao,
            lighting=estilo_luz
        )
        return resultado
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/persona/criar")
async def criar_nova_persona_endpoint(
    nome: str = Form(...),
    nicho: str = Form(...),
    acessorio: str = Form(""),
    imagem: UploadFile = File(...)
):
    """Caminho 2: Cria nova persona do zero a partir de imagem de referência (Aulas 1 a 4)"""
    try:
        file_ext = Path(imagem.filename).suffix or ".png"
        import time
        ts = time.strftime("%Y%m%d_%H%M%S")
        saved_img_path = INPUTS_DIR / f"ref_persona_{nome.lower().replace(' ', '_')}_{ts}{file_ext}"
        
        with open(saved_img_path, "wb") as buffer:
            shutil.copyfileobj(imagem.file, buffer)
            
        resultado = create_new_persona_pipeline(
            name=nome,
            niche=nicho,
            reference_image_path=str(saved_img_path),
            signature_accessory=acessorio
        )
        return resultado
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/campanha")
async def criar_campanha(
    loja: str = Form(...),
    persona_id: str = Form("synthia"),
    cenario: str = Form("provador de boutique elegante com luz suave de espelho"),
    imagem: UploadFile = File(...)
):
    try:
        file_ext = Path(imagem.filename).suffix or ".png"
        import time
        ts = time.strftime("%Y%m%d_%H%M%S")
        saved_img_path = INPUTS_DIR / f"produto_{loja.replace(' ', '_')}_{ts}{file_ext}"
        
        with open(saved_img_path, "wb") as buffer:
            shutil.copyfileobj(imagem.file, buffer)
            
        resultado = gerar_campanha_produto(
            product_image_path=str(saved_img_path),
            nome_loja=loja,
            tipo_cenario=cenario,
            persona_name=persona_id
        )
        return {"status": "success", "campanha": resultado}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video-humano")
async def gerar_video_humano_endpoint(
    fala: str = Form(...),
    cenario: str = Form("lying comfortably on bed against cream pillows, soft diffuse morning window light from the left"),
    camera: str = Form("slow smooth zoom gliding physically towards her face, extreme close-up on eyes and pores"),
    persona_id: str = Form("synthia"),
    vocal_style: str = Form("jovem_espontanea"),
    foco_visual: str = Form("produto")
):
    try:
        res_prompt = generate_behavioral_video_prompt(
            persona_name=persona_id,
            dialogue_script=fala,
            scene_context=cenario,
            camera_movement=camera,
            vocal_style=vocal_style,
            foco_visual=foco_visual,
            return_dict=True
        )
        veo_json = generate_veo_json_prompt(
            persona_name=persona_id,
            dialogue_script=fala,
            vocal_style=vocal_style,
            foco_visual=foco_visual
        )
        return {
            "status": "success",
            "video_prompt": res_prompt["full_prompt"] if isinstance(res_prompt, dict) else res_prompt,
            "acoustic_tag": res_prompt.get("acoustic_tag", "") if isinstance(res_prompt, dict) else "",
            "vocal_title": res_prompt.get("vocal_title", "") if isinstance(res_prompt, dict) else "",
            "vocal_description": res_prompt.get("vocal_description", "") if isinstance(res_prompt, dict) else "",
            "veo_json": veo_json
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/video/gerar-fala")
async def gerar_fala_ia_endpoint(
    tema: str = Form("vestido elegante"),
    tom: str = Form("provador")
):
    """Gera uma fala falada de 8 a 10 segundos em PT-BR para a influenciadora."""
    try:
        import google.generativeai as genai
        from config import GEMINI_API_KEY
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        
        prompt_ia = f"""
Você é o roteirista de vídeos curtos (Reels/TikTok) de uma influenciadora digital brasileira jovem e carismática chamada Synthia.
Crie UMA única fala curta falada em primeira pessoa (cerca de 2 a 3 frases, máxima duração de 8 a 10 segundos ao falar em voz alta).

TEMA/PRODUTO: {tema}
TOM/OBJETIVO: {tom}

REGRAS:
1. Deve soar 100% como uma pessoa real gravando com o celular na mão (nada de texto comercial formal ou brega).
2. Use linguagem falada brasileira natural, com pausas, ganchos magnéticos ou perguntas envolventes para a audiência.
3. Não use hashtags ou introduções como "Synthia diz:". Retorne APENAS a fala exata.
"""
        model = genai.GenerativeModel("gemini-2.5-flash")
        resp = model.generate_content(prompt_ia)
        fala_gerada = resp.text.strip().replace('"', '').replace("'", "")
        return {"status": "success", "fala": fala_gerada}
    except Exception as e:
        fallbacks = {
            "provador": "Gente, para tudo... olhem o caimento dessa peça no corpo. O tecido é levíssimo e modela sem marcar nada. Vocês usariam?",
            "viral": "Ainda dizem por aí que eu sou apenas um prompt... Então chega um pouco mais perto. Assusta o quanto parece real, né?",
            "beleza": "Vocês vivem me perguntando o que eu passo na pele de manhã... vou contar meu segredo agora, mas não espalha pra ninguém, tá?",
            "publi": "Consegui um cupom exclusivo de 20% pra vocês nessa coleção da loja! Mas corre no link da bio porque o estoque tá voando...",
            "sofisticada": "Tem dias em que menos é mais. Uma peça bem cortada muda completamente a sua presença sem você precisar dizer nada."
        }
        return {"status": "success", "fala": fallbacks.get(tom, fallbacks["provador"])}

@app.get("/api/campanhas")
def listar_campanhas():
    campanhas = []
    for pasta in sorted(OUTPUT_DIR.glob("campanha_*"), reverse=True):
        if pasta.is_dir():
            flow_json = pasta / "01_prompt_flow_colecao.json"
            video_txt = pasta / "02_roteiro_video_human_engine.txt"
            
            c_data = {"id": pasta.name, "timestamp": pasta.name.replace("campanha_synthia_", "")}
            if flow_json.exists():
                try:
                    with open(flow_json, "r", encoding="utf-8") as f:
                        c_data["flow_json"] = json.load(f)
                except Exception:
                    pass
            if video_txt.exists():
                try:
                    with open(video_txt, "r", encoding="utf-8") as f:
                        c_data["video_script"] = f.read()
                except Exception:
                    pass
            campanhas.append(c_data)
    return campanhas

@app.get("/api/pos-producao/video-recente")
def get_video_recente():
    """Detecta o vídeo mais recente gerado na Área de Trabalho ou pasta de inputs"""
    desktop = Path.home() / "Desktop"
    recents = sorted(desktop.glob("*.mp4"), key=os.path.getmtime, reverse=True)
    if recents:
        latest = recents[0]
        return {
            "exists": True,
            "filename": latest.name,
            "size_mb": round(latest.stat().st_size / (1024 * 1024), 2),
            "path": str(latest)
        }
    return {"exists": False}

@app.get("/api/pos-producao/ultimo-calibrado")
def ultimo_calibrado_endpoint():
    desktop = Path.home() / "Desktop"
    calibrado = desktop / "SYNTHIA_CALIBRADA_ANTI_IA.mp4"
    split = desktop / "SYNTHIA_COMPARATIVO_SPLIT_SCREEN.mp4"
    
    out_splits = sorted(OUTPUT_DIR.glob("*split*.mp4"), key=os.path.getmtime, reverse=True)
    out_cals = sorted(OUTPUT_DIR.glob("*calibrado*.mp4"), key=os.path.getmtime, reverse=True)
    in_raws = sorted(INPUTS_DIR.glob("*raw*.mp4"), key=os.path.getmtime, reverse=True)

    if calibrado.exists() or out_cals:
        split_url = f"/static_outputs/{out_splits[0].name}" if out_splits else "/static_outputs/synthia_split_screen.mp4"
        cal_url = f"/static_outputs/{out_cals[0].name}" if out_cals else "/static_outputs/calibrado_anti_ia_20261009_131522.mp4"
        raw_url = f"/static_inputs/{in_raws[0].name}" if in_raws else "/static_inputs/raw_veo_original.mp4"
        
        return {
            "has_calibrated": True,
            "video_url": cal_url,
            "split_url": split_url,
            "raw_url": raw_url,
            "filename": "SYNTHIA_CALIBRADA_ANTI_IA.mp4",
            "split_filename": "SYNTHIA_COMPARATIVO_SPLIT_SCREEN.mp4"
        }
    return {"has_calibrated": False}

@app.post("/api/pos-producao/calibrar")
async def calibrar_video_endpoint(
    video: Optional[UploadFile] = File(None),
    usar_recente: bool = Form(False)
):
    """
    Etapa 4: Aplica Color Grading Anti-IA automático via FFmpeg em 1 clique:
    - Redução cirúrgica de realces (-29%) para eliminar brilho plástico de IA
    - Elevação suave de sombras (+10%) para revelar microdetalhes do tecido
    - Correção de exposição (-3%)
    - Injeção de ruído orgânico de sensor de smartphone (3%)
    - Padronização em 1080p vertical MP4
    - Geração automática de vídeo comparativo Split-Screen (Antes vs Depois)
    """
    try:
        import time
        ts = time.strftime("%Y%m%d_%H%M%S")
        input_video_path = None
        
        if usar_recente:
            desktop = Path.home() / "Desktop"
            recents = [
                f for f in desktop.glob("*.mp4")
                if not f.name.startswith("SYNTHIA_CALIBRADA") and not f.name.startswith("SYNTHIA_COMPARATIVO")
            ]
            recents = sorted(recents, key=os.path.getmtime, reverse=True)
            if recents:
                input_video_path = recents[0]
            else:
                raise HTTPException(status_code=400, detail="Nenhum vídeo MP4 bruto encontrado na Área de Trabalho.")
        elif video and video.filename:
            file_ext = Path(video.filename).suffix or ".mp4"
            saved_path = INPUTS_DIR / f"raw_video_{ts}{file_ext}"
            with open(saved_path, "wb") as buffer:
                shutil.copyfileobj(video.file, buffer)
            input_video_path = saved_path
        else:
            raise HTTPException(status_code=400, detail="Por favor, selecione um arquivo de vídeo ou use o vídeo recente.")

        # Copia raw para inputs/ para servir via static_inputs se ainda não estiver
        raw_filename = f"raw_video_{ts}{Path(input_video_path).suffix or '.mp4'}"
        raw_saved_path = INPUTS_DIR / raw_filename
        if not raw_saved_path.exists():
            shutil.copy2(input_video_path, raw_saved_path)
            
        output_filename = f"calibrado_anti_ia_{ts}.mp4"
        output_path = OUTPUT_DIR / output_filename
        
        # 1. Calibração Anti-IA
        if not shutil.which("ffmpeg"):
            raise HTTPException(
                status_code=501,
                detail="FFmpeg não encontrado no servidor de nuvem. A renderização pesada de vídeo deve ser executada localmente no Desktop."
            )

        cmd = [
            "ffmpeg", "-i", str(input_video_path),
            "-vf", "curves=all='0/0.02 0.2/0.23 0.7/0.64 1/0.94',noise=alls=3:allf=t+u,scale=-2:1920,format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-c:a", "copy",
            str(output_path), "-y"
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Erro ao processar vídeo no FFmpeg: {proc.stderr[:300]}")
            
        # Salva cópia na Área de Trabalho
        try:
            desktop_copy = Path.home() / "Desktop" / "SYNTHIA_CALIBRADA_ANTI_IA.mp4"
            shutil.copy2(output_path, desktop_copy)
        except Exception:
            pass

        # 2. Renderiza vídeo split-screen comparativo
        split_filename = f"split_comparativo_{ts}.mp4"
        split_path = OUTPUT_DIR / split_filename
        cmd_split = [
            "ffmpeg", "-i", str(input_video_path), "-i", str(output_path),
            "-filter_complex",
            "[0:v]scale=1080:1920,crop=540:1920:0:0[left];"
            "[1:v]crop=540:1920:540:0[right];"
            "[left][right]hstack[split];"
            "[split]drawbox=x=538:y=0:w=4:h=1920:color=white@0.8:t=fill[with_line];"
            "[with_line]drawtext=text='ANTES (BRUTO)':x=60:y=120:fontsize=44:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=10,"
            "drawtext=text='DEPOIS (ANTI-IA)':x=600:y=120:fontsize=44:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=10[v]",
            "-map", "[v]", "-map", "1:a?",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(split_path), "-y"
        ]
        subprocess.run(cmd_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        try:
            desktop_split = Path.home() / "Desktop" / "SYNTHIA_COMPARATIVO_SPLIT_SCREEN.mp4"
            shutil.copy2(split_path, desktop_split)
        except Exception:
            pass

        return {
            "status": "success",
            "video_url": f"/static_outputs/{output_filename}",
            "split_url": f"/static_outputs/{split_filename}",
            "raw_url": f"/static_inputs/{raw_filename}",
            "filename": output_filename,
            "split_filename": split_filename,
            "origem": str(input_video_path.name)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>INFLUENCER STUDIO PRO™ // Enterprise Operating System</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    code, pre { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body class="bg-[#0b0f17] text-gray-100 min-h-screen">

  <!-- Header Enterprise -->
  <header class="border-b border-gray-800 bg-[#111622]/90 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-rose-500 to-amber-500 flex items-center justify-center font-extrabold text-white text-base shadow-lg shadow-indigo-500/20">
        PRO
      </div>
      <div>
        <h1 class="font-bold text-lg text-white flex items-center gap-2">
          INFLUENCER STUDIO PRO™
          <span class="text-[10px] font-semibold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full">Enterprise Edition v2.0</span>
        </h1>
        <p class="text-xs text-gray-400">Plataforma Operacional de Influenciadoras Virtuais, Provador de Marcas & Vídeos UGC</p>
      </div>
    </div>
    
    <div class="flex items-center space-x-3">
      <a href="https://flow.google.com/project/8f2818a1-af39-4697-ad1f-c892ee61f3c2/collection/74c8281d-2e25-4983-8576-194c7dd9e74c" target="_blank" class="text-xs bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/30 px-3 py-2 rounded-lg transition flex items-center gap-1.5 font-medium">
        <span>Abrir Coleção da Synthia no Flow ↗</span>
      </a>
      <div class="h-4 w-px bg-gray-800"></div>
      <span class="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1.5 rounded-lg">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        Google Flow PRO Vinculado
      </span>
    </div>
  </header>

  <!-- Navegação por Etapas do Processo -->
  <div class="bg-[#0f1420] border-b border-gray-800 px-6">
    <div class="max-w-7xl mx-auto flex space-x-2">
      <button onclick="switchTab('tabPersonas')" id="btnTabPersonas" class="tab-btn px-4 py-3 text-xs font-bold border-b-2 border-indigo-500 text-indigo-400 flex items-center gap-2">
        <span>🧬</span> Etapa 1: Identidade & Face Lock
      </button>
      <button onclick="switchTab('tabVideo')" id="btnTabVideo" class="tab-btn px-4 py-3 text-xs font-semibold border-b-2 border-transparent text-gray-400 hover:text-gray-200 flex items-center gap-2">
        <span>🎬</span> Etapa 2: Roteirista Comportamental (HUMAN ENGINE™)
      </button>
      <button onclick="switchTab('tabEcommerce')" id="btnTabEcommerce" class="tab-btn px-4 py-3 text-xs font-semibold border-b-2 border-transparent text-gray-400 hover:text-gray-200 flex items-center gap-2">
        <span>🛍️</span> Etapa 3: Provador Virtual de Marcas & E-commerce
      </button>
      <button onclick="switchTab('tabPosProducao')" id="btnTabPosProducao" class="tab-btn px-4 py-3 text-xs font-semibold border-b-2 border-transparent text-gray-400 hover:text-gray-200 flex items-center gap-2">
        <span>⚡</span> Etapa 4: Pós-Produção Anti-IA (FFmpeg) & Motion
      </button>
    </div>
  </div>

  <!-- Container Principal -->
  <main class="max-w-7xl mx-auto px-6 py-8">
    
    <!-- ======================================================== -->
    <!-- ETAPA 3: PROVADOR VIRTUAL DE MARCAS & E-COMMERCE (UGC)   -->
    <!-- ======================================================== -->
    <div id="tabEcommerce" class="tab-content hidden grid grid-cols-1 lg:grid-cols-12 gap-8">
      
      <!-- Esquerda: Formulário de Produto -->
      <div class="lg:col-span-5 space-y-6">
        <div class="bg-[#131926] border border-gray-800 rounded-2xl p-5">
          <div class="flex items-center space-x-3 mb-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-rose-600 flex items-center justify-center font-bold text-white text-sm">
              SYN
            </div>
            <div>
              <h3 class="font-bold text-white text-sm flex items-center gap-1.5">
                Synthia
                <span class="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20 font-semibold">Face ID Ativo</span>
              </h3>
              <p class="text-xs text-amber-400">Embaixadora Oficial de Moda Feminina & Joias</p>
            </div>
          </div>
          <p class="text-xs text-gray-400">Coleção no Flow vinculada para vestir qualquer peça física com 1:1 de precisão e caimento natural.</p>
        </div>

        <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h2 class="text-base font-bold text-white mb-1 flex items-center gap-2">
            <span>✨</span> Novo Provador / Anúncio de Loja
          </h2>
          <p class="text-xs text-gray-400 mb-5">Envie a foto da roupa da loja para gerar o JSON do Flow e o roteiro falado do Veo 3.1.</p>

          <form id="campanhaForm" onsubmit="enviarCampanha(event)" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Selecionar Persona</label>
              <select id="lojaPersonaId" class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
                <option value="synthia">Synthia (Coleção Ativa)</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Nome da Loja / Cliente</label>
              <input type="text" id="loja" required placeholder="Ex: Boutique Elegance, Zara, etc." 
                     class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition">
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Cenário</label>
              <select id="cenario" class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 transition">
                <option value="provador de boutique elegante com luz suave de espelho">Provador de Boutique Chic (Luz de Espelho)</option>
                <option value="quarto moderno iluminado por luz matinal de janela">Quarto Minimalista / Luz de Janela</option>
                <option value="rua charmosa de cafeteria moderna em Milão">Lifestyle Urbano / Cafeteria</option>
                <option value="estúdio comercial clean com fundo neutro">Estúdio Clean</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Foto do Produto (Vestido, Top, Jaqueta, etc.)</label>
              <div id="dropzone" class="border-2 border-dashed border-gray-700 hover:border-indigo-500 rounded-xl p-5 text-center cursor-pointer bg-[#0b0f17]/50 transition">
                <input type="file" id="imagem" required accept="image/*" class="hidden" onchange="previewImage(this)">
                <div id="dropText">
                  <div class="text-2xl mb-1">📸</div>
                  <p class="text-xs font-medium text-gray-300">Clique para selecionar ou arraste a imagem</p>
                  <p class="text-[11px] text-gray-500 mt-1">PNG, JPG até 10MB</p>
                </div>
                <div id="previewContainer" class="hidden">
                  <img id="imgPreview" class="max-h-36 mx-auto rounded-lg object-contain mb-2">
                  <p id="fileName" class="text-xs text-indigo-400 font-mono"></p>
                </div>
              </div>
            </div>

            <button type="submit" id="btnSubmit" class="w-full bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:opacity-95 text-white font-bold text-sm py-3.5 px-4 rounded-xl shadow-lg shadow-rose-500/20 transition flex items-center justify-center gap-2">
              <span>⚡</span>
              <span id="btnText">Gerar Campanha Completa (DNA + Flow + Veo 3.1)</span>
            </button>
          </form>

          <div id="loading" class="hidden mt-4 p-4 bg-indigo-950/30 border border-indigo-800/40 rounded-xl">
            <div class="flex items-center space-x-3">
              <div class="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
              <p class="text-xs text-indigo-300 font-medium">Extraindo DNA da peça no MIRR0R e gerando roteiro...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Direita: Resultados Gerados -->
      <div class="lg:col-span-7 space-y-6">
        <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 min-h-[580px]">
          <div class="flex items-center justify-between border-b border-gray-800 pb-4 mb-5">
            <div>
              <h2 class="text-base font-bold text-white flex items-center gap-2">
                <span>📦</span> Pacote Comercial da Campanha
              </h2>
              <p class="text-xs text-gray-400">Pronto para rodar na Coleção do Flow e no Veo 3.1.</p>
            </div>
            <div id="statusBadge" class="hidden">
              <span class="text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full">Gerado com Sucesso</span>
            </div>
          </div>

          <div id="emptyState" class="py-24 text-center">
            <div class="text-5xl mb-3 opacity-30">👗</div>
            <h3 class="text-sm font-semibold text-gray-300">Nenhum produto processado ainda</h3>
            <p class="text-xs text-gray-500 max-w-sm mx-auto mt-1">Preencha os dados da loja ao lado para ver a Synthia vestindo a peça com 100% de fidelidade de tecido.</p>
          </div>

          <div id="resultContent" class="hidden space-y-5">
            <!-- 1. Flow Prompt -->
            <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                  <span>🍌</span> 1. Prompt MIRR0R JSON (Coleção da Synthia no Flow)
                </span>
                <button onclick="copiarTexto('promptFlowCode', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar JSON</button>
              </div>
              <pre id="promptFlowCode" class="text-xs text-gray-300 bg-[#070a10] p-3 rounded-lg overflow-x-auto max-h-52 leading-relaxed border border-gray-900"></pre>
            </div>

            <!-- 2. Video Script -->
            <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                  <span>🎬</span> 2. Roteiro de Vídeo Falado em PT-BR (HUMAN ENGINE™ / Veo 3.1)
                </span>
                <button onclick="copiarTexto('videoScriptCode', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar Roteiro</button>
              </div>
              <div id="videoScriptCode" class="text-xs text-gray-200 bg-[#070a10] p-3 rounded-lg max-h-48 overflow-y-auto leading-relaxed border border-gray-900"></div>
            </div>

            <!-- 3. CapCut Settings -->
            <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
              <span class="text-xs font-bold text-indigo-400 flex items-center gap-1.5 mb-2">
                <span>🎨</span> 3. Parâmetros CapCut (Pós-Produção Anti-IA)
              </span>
              <div class="grid grid-cols-4 gap-2 text-center text-xs">
                <div class="bg-gray-900/60 p-2 rounded-lg border border-gray-800"><div class="text-[10px] text-gray-400">Exposição</div><div class="font-bold text-white">-3</div></div>
                <div class="bg-gray-900/60 p-2 rounded-lg border border-gray-800"><div class="text-[10px] text-gray-400">Highlights</div><div class="font-bold text-white">-29</div></div>
                <div class="bg-gray-900/60 p-2 rounded-lg border border-gray-800"><div class="text-[10px] text-gray-400">Shadows</div><div class="font-bold text-white">+10</div></div>
                <div class="bg-gray-900/60 p-2 rounded-lg border border-gray-800"><div class="text-[10px] text-gray-400">Exportação</div><div class="font-bold text-white">1080p MP4</div></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- ETAPA 2: ROTEIRISTA COMPORTAMENTAL (HUMAN ENGINE™)       -->
    <!-- ======================================================== -->
    <div id="tabVideo" class="tab-content hidden grid grid-cols-1 lg:grid-cols-12 gap-8">
      <div class="lg:col-span-5 space-y-6">
        <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 shadow-xl">
          <h2 class="text-base font-bold text-white mb-1 flex items-center gap-2">
            <span>🎬</span> HUMAN ENGINE™ // Roteirista & Acústica Vocal
          </h2>
          <p class="text-xs text-gray-400 mb-5">
            Sintetiza prompts para o Google Veo 3.1 com micro-expressões faciais e <strong>DNA acústico anti-IA embutido</strong> (respiração humana, vocal fry e proximidade física de microfone).
          </p>

          <form onsubmit="gerarVideoHumano(event)" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Selecionar Persona</label>
              <select id="videoPersonaId" class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
                <option value="synthia">Synthia (Coleção Ativa)</option>
              </select>
            </div>

            <!-- BANCO DE ROTEIROS PRONTOS EM 1 CLIQUE & ASSISTENTE IA -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <label class="block text-xs font-semibold text-gray-300">Fala da Persona em Português</label>
                <span class="text-[10px] text-indigo-400 font-medium">⚡ 1-Clique para preencher:</span>
              </div>
              
              <!-- Chips de Presets Prontos -->
              <div class="flex flex-wrap gap-1.5 pb-1">
                <button type="button" onclick="aplicarPresetFala('joia')" class="text-[11px] bg-[#0b0f17] hover:bg-cyan-950/60 border border-gray-800 hover:border-cyan-500 text-cyan-300 hover:text-white px-2.5 py-1 rounded-lg transition font-medium flex items-center gap-1 shadow-sm">
                  <span>💎</span> Jóias / Luxo
                </button>
                <button type="button" onclick="aplicarPresetFala('provador')" class="text-[11px] bg-[#0b0f17] hover:bg-indigo-950/60 border border-gray-800 hover:border-indigo-500 text-gray-300 hover:text-white px-2.5 py-1 rounded-lg transition font-medium flex items-center gap-1 shadow-sm">
                  <span>👗</span> Provador Loja
                </button>
                <button type="button" onclick="aplicarPresetFala('viral')" class="text-[11px] bg-[#0b0f17] hover:bg-rose-950/60 border border-gray-800 hover:border-rose-500 text-gray-300 hover:text-white px-2.5 py-1 rounded-lg transition font-medium flex items-center gap-1 shadow-sm">
                  <span>🔥</span> Sou IA? (Viral)
                </button>
                <button type="button" onclick="aplicarPresetFala('beleza')" class="text-[11px] bg-[#0b0f17] hover:bg-emerald-950/60 border border-gray-800 hover:border-emerald-500 text-gray-300 hover:text-white px-2.5 py-1 rounded-lg transition font-medium flex items-center gap-1 shadow-sm">
                  <span>💄</span> Skincare / Segredo
                </button>
                <button type="button" onclick="aplicarPresetFala('publi')" class="text-[11px] bg-[#0b0f17] hover:bg-amber-950/60 border border-gray-800 hover:border-amber-500 text-gray-300 hover:text-white px-2.5 py-1 rounded-lg transition font-medium flex items-center gap-1 shadow-sm">
                  <span>🏷️</span> Cupom / Promo
                </button>
                <button type="button" onclick="aplicarPresetFala('sofisticada')" class="text-[11px] bg-[#0b0f17] hover:bg-purple-950/60 border border-gray-800 hover:border-purple-500 text-gray-300 hover:text-white px-2.5 py-1 rounded-lg transition font-medium flex items-center gap-1 shadow-sm">
                  <span>✨</span> Elegância / Luxo
                </button>
              </div>

              <!-- Gerador Automático de Fala com IA por Palavra-Chave -->
              <div class="p-2.5 bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-[#0b0f17] border border-indigo-900/40 rounded-xl flex items-center gap-2">
                <input id="inputTemaIa" type="text" placeholder="Sem ideias? Digite o tema (ex: anel de ouro, vestido de linho, tênis)..." 
                       class="flex-1 bg-[#0b0f17] border border-gray-800 rounded-lg px-2.5 py-1.5 text-[11px] text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition">
                <button type="button" onclick="gerarFalaAutomaticaIa()" id="btnGerarFalaIa" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-[11px] font-bold transition flex items-center gap-1 shrink-0 shadow-md">
                  <span>✨</span> Criar Fala IA
                </button>
              </div>

              <textarea id="videoFala" rows="3" required class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl p-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition leading-relaxed" placeholder="Selecione um botão acima ou digite o tema para a IA escrever a fala por você..."></textarea>
            </div>

            <!-- NOVO CAMPO: FOCO VISUAL & ENQUADRAMENTO DA CÂMERA -->
            <div>
              <label class="block text-xs font-semibold text-indigo-400 mb-1.5 flex items-center gap-1.5">
                <span>🎯</span> Foco Visual & Enquadramento da Câmera
              </label>
              <select id="videoFocoVisual" class="w-full bg-[#0b0f17] border border-indigo-900/60 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
                <option value="produto" selected>💎 Jóia / Acessório / Produto (Macro nos reflexos do produto, mão delicada, sem zoom nos olhos)</option>
                <option value="look">👗 Look Completo & Caimento (Tilt vertical destacando corte e movimento do tecido)</option>
                <option value="rosto">💄 Rosto & Expressão (Micro-expressões labiais, olhar e poros da pele)</option>
                <option value="vlog">📱 POV Casual / Vlog (Balanço de respiração natural com celular na mão)</option>
              </select>
              <p class="text-[10px] text-gray-500 mt-1">Define o alvo prioritário da lente: para onde a câmera viaja e o que ganha nitidez no Veo.</p>
            </div>

            <!-- NOVO CAMPO: DNA VOCAL & ACÚSTICA ANTI-IA -->
            <div>
              <label class="block text-xs font-semibold text-emerald-400 mb-1.5 flex items-center gap-1.5">
                <span>🎙️</span> DNA Vocal & Acústica Anti-IA (Áudio Integrado)
              </label>
              <select id="videoVoz" class="w-full bg-[#0b0f17] border border-emerald-900/60 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 transition">
                <option value="jovem_espontanea" selected>🌟 Jovem Espontânea & Casual (Vocal fry, respiração audível, ritmo dinâmico)</option>
                <option value="criadora_conteudo">🛍️ Criadora de Conteúdo / Provador (Projeção nítida, entusiasmo natural de vendas)</option>
                <option value="sofisticada_aveludada">✨ Sofisticada & Aveludada (Tom calmo, ressonância profunda de peito, luxo)</option>
                <option value="confessional_intima">🎧 Confessional / Segredo Íntimo (Tom sussurrado, proximidade acústica extrema)</option>
              </select>
              <p class="text-[10px] text-gray-500 mt-1">Gera instruções acústicas de microfone de smartphone real para o Veo não usar a voz robótica padrão.</p>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Movimento de Câmera</label>
              <select id="videoCamera" class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
                <option value="macro push-in focusing sharply on the jewelry piece and its light reflection" selected>Push-In Macro no Produto / Jóia (Foco cravado no acessório, bokeh suave)</option>
                <option value="slow smooth zoom gliding physically towards her face, extreme close-up on eyes and pores">Push-In Lento no Rosto (Zoom Macro nos Olhos & Poros com Proximidade Acústica)</option>
                <option value="gentle breathing sway of handheld smartphone frame, relaxed and intimate">Breathing Sway (Câmera com Balanço da Respiração)</option>
                <option value="tilt down showing the full outfit drape, then returning to her smiling eyes">Tilt de Corpo (Mostra Caimento da Roupa e Rosto)</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-gray-300 mb-1.5">Cenário / Iluminação</label>
              <input id="videoCenario" type="text" value="lying comfortably on bed against cream pillows, soft diffuse morning window light from the left" class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
            </div>

            <button type="submit" id="btnSubmitVideo" class="w-full bg-gradient-to-r from-rose-500 via-indigo-600 to-emerald-600 hover:opacity-95 text-white font-bold text-xs py-3.5 px-4 rounded-xl shadow-lg transition flex items-center justify-center gap-2">
              <span>⚡</span>
              <span id="btnTextVideo">Sintetizar Prompt Comportamental & Acústico (Veo 3.1)</span>
            </button>
          </form>
        </div>
      </div>

      <div class="lg:col-span-7 space-y-6">
        <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 min-h-[500px]">
          <h2 class="text-base font-bold text-white mb-2 flex items-center gap-2">
            <span>🎞️</span> Prompt Cinematográfico + Acústica Pronta para o Veo 3.1
          </h2>
          <p class="text-xs text-gray-400 mb-5">Roteiro audiovisual completo formatado com pausas, acústica física do microfone e visemas labiais.</p>

          <div id="videoResultBox" class="space-y-4">
            <!-- Box 1: Prompt Principal -->
            <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                  <span>🎬</span> Prompt Completo para o Google Veo 3.1 (Vídeo + Voz Anti-IA)
                </span>
                <button onclick="copiarTexto('videoPromptOutput', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar</button>
              </div>
              <div id="videoPromptOutput" class="text-xs text-gray-200 bg-[#070a10] p-3 rounded-lg leading-relaxed border border-gray-900 max-h-60 overflow-y-auto">
                Preencha os campos ao lado e clique em Sintetizar para gerar o prompt comportamental com voz anti-IA.
              </div>
            </div>

            <!-- Box 2: Diretriz Acústica Isolada -->
            <div id="boxAudioTag" class="hidden bg-[#0b0f17] border border-emerald-950/60 rounded-xl p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                  <span>🎙️</span> Diretriz Acústica & Fisiológica da Voz (Audio Architecture)
                </span>
                <button onclick="copiarTexto('audioTagOutput', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar Áudio</button>
              </div>
              <div id="audioTagOutput" class="text-xs text-emerald-300 bg-[#070a10] p-3 rounded-lg leading-relaxed border border-gray-900 max-h-36 overflow-y-auto"></div>
            </div>

            <!-- Box 3: JSON Veo -->
            <div id="boxVeoJson" class="hidden bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-bold text-indigo-400 flex items-center gap-1.5">
                  <span>⚡</span> JSON Estruturado (Veo 3.1 Promptbook 6.3)
                </span>
                <button onclick="copiarTexto('veoJsonOutput', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar JSON</button>
              </div>
              <pre id="veoJsonOutput" class="text-xs text-gray-300 bg-[#070a10] p-3 rounded-lg overflow-x-auto max-h-48 leading-relaxed border border-gray-900"></pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- ETAPA 1: IDENTIDADE & FACE LOCK                          -->
    <!-- ======================================================== -->
    <div id="tabPersonas" class="tab-content space-y-6">
      
      <!-- Sub-Barra de Navegação dos Dois Caminhos -->
      <div class="bg-[#131926] border border-gray-800 rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <span>🧬</span> Identidade & Face Lock da Influenciadora
          </h2>
          <p class="text-xs text-gray-400">Escolha o modo de operação da inteligência visual:</p>
        </div>
        <div class="flex items-center bg-[#0b0f17] p-1.5 rounded-xl border border-gray-800">
          <button type="button" onclick="switchPersonaSubTrack('trackExistente')" id="btnSubTrackExistente" class="px-4 py-2 text-xs font-bold rounded-lg bg-indigo-600 text-white transition flex items-center gap-2">
            <span>🌟</span> Caminho 1: Persona Existente (Synthia)
          </button>
          <button type="button" onclick="switchPersonaSubTrack('trackNova')" id="btnSubTrackNova" class="px-4 py-2 text-xs font-semibold rounded-lg text-gray-400 hover:text-white transition flex items-center gap-2">
            <span>➕</span> Caminho 2: Criar Nova Persona do Zero
          </button>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- CAMINHO 1: USAR PERSONA EXISTENTE (EX: SYNTHIA) -->
      <!-- ============================================== -->
      <div id="subTrackExistente" class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- Esquerda: Formulário de Nova Cena -->
        <div class="lg:col-span-5 space-y-6">
          <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 shadow-xl">
            <h3 class="text-base font-bold text-white mb-1 flex items-center gap-2">
              <span>🎬</span> Nova Cena com Face Lock Travado
            </h3>
            <p class="text-xs text-gray-400 mb-5">Gera novas fotos/cenas da persona existente blindando o rosto e criando o JSON para o Google Flow.</p>

            <form onsubmit="enviarCenaPersona(event)" class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-gray-300 mb-1.5">Selecionar Persona</label>
                <select id="cenaPersonaId" class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 transition">
                  <option value="synthia">Synthia (Face Lock 100% // Coleção Ativa)</option>
                </select>
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-300 mb-1.5">Nova Cena / Ação / Look Desejado</label>
                <textarea id="cenaDescricao" rows="4" required placeholder="Ex: Sentada em um café moderno em Milão em manhã ensolarada, vestindo blazer de linho bege claro, segurando xícara de café com as duas mãos e sorrindo sutilmente para a lente..." 
                          class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl p-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition leading-relaxed"></textarea>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-semibold text-gray-300 mb-1.5">Proporção</label>
                  <select id="cenaProporcao" class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
                    <option value="9:16">9:16 Vertical (Reels / TikTok / Stories)</option>
                    <option value="16:9">16:9 Horizontal (YouTube / Banners)</option>
                    <option value="1:1">1:1 Quadrado (Feed)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-300 mb-1.5">Iluminação</label>
                  <select id="cenaLuz" class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
                    <option value="luz natural suave de janela com sombra difusa">Luz Natural de Janela</option>
                    <option value="golden hour quente de fim de tarde">Golden Hour (Pôr do Sol)</option>
                    <option value="estúdio clean contemporâneo">Estúdio Clean</option>
                    <option value="moody noturno com luzes bokeh da cidade">Moody Noturno Urbano</option>
                  </select>
                </div>
              </div>

              <button type="submit" id="btnSubmitCena" class="w-full bg-gradient-to-r from-indigo-600 to-rose-600 hover:opacity-95 text-white font-bold text-xs py-3.5 px-4 rounded-xl shadow-lg transition flex items-center justify-center gap-2">
                <span>⚡</span>
                <span id="btnTextCena">Gerar Pacote de Cena (MIRR0R JSON + Veo 3.1)</span>
              </button>
            </form>
          </div>
        </div>

        <!-- Direita: Resultados Caminho 1 -->
        <div class="lg:col-span-7 space-y-6">
          <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 min-h-[500px]">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4 mb-5">
              <div>
                <h3 class="text-base font-bold text-white flex items-center gap-2">
                  <span>📦</span> Pacote de Continuidade de Cena
                </h3>
                <p class="text-xs text-gray-400">Prompts gerados com identidade facial travada 100%.</p>
              </div>
              <a id="cenaFlowLink" href="https://flow.google.com/project/8f2818a1-af39-4697-ad1f-c892ee61f3c2/collection/74c8281d-2e25-4983-8576-194c7dd9e74c" target="_blank" class="text-xs bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/30 px-3 py-1.5 rounded-lg transition font-medium flex items-center gap-1.5">
                <span>Abrir Coleção no Flow ↗</span>
              </a>
            </div>

            <div id="cenaEmptyState" class="py-20 text-center">
              <div class="text-5xl mb-3 opacity-30">📸</div>
              <h4 class="text-sm font-semibold text-gray-300">Nenhuma nova cena gerada ainda</h4>
              <p class="text-xs text-gray-500 max-w-sm mx-auto mt-1">Descreva o novo cenário ao lado para ver a Synthia na nova pose mantendo seu rosto 100% fiel.</p>
            </div>

            <div id="cenaResultBox" class="hidden space-y-4">
              <!-- 1. Flow Prompt -->
              <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                    <span>🍌</span> 1. Prompt MIRR0R JSON (Coleção do Google Flow)
                  </span>
                  <button onclick="copiarTexto('cenaFlowCode', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar JSON</button>
                </div>
                <pre id="cenaFlowCode" class="text-xs text-gray-300 bg-[#070a10] p-3 rounded-lg overflow-x-auto max-h-48 leading-relaxed border border-gray-900"></pre>
              </div>

              <!-- 2. Master Diffusion Prompt -->
              <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-bold text-indigo-400 flex items-center gap-1.5">
                    <span>🎨</span> 2. Master Diffusion Prompt em Inglês (Imagen 3 / Flux.1)
                  </span>
                  <button onclick="copiarTexto('cenaMasterCode', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar</button>
                </div>
                <div id="cenaMasterCode" class="text-xs text-gray-200 bg-[#070a10] p-3 rounded-lg max-h-40 overflow-y-auto leading-relaxed border border-gray-900"></div>
              </div>

              <!-- 3. Roteiro Veo 3.1 -->
              <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                    <span>🎬</span> 3. Roteiro Comportamental para Veo 3.1 (HUMAN ENGINE™)
                  </span>
                  <button onclick="copiarTexto('cenaVeoCode', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar</button>
                </div>
                <div id="cenaVeoCode" class="text-xs text-gray-200 bg-[#070a10] p-3 rounded-lg max-h-40 overflow-y-auto leading-relaxed border border-gray-900"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ============================================== -->
      <!-- CAMINHO 2: CRIAR NOVA PERSONA DO ZERO          -->
      <!-- ============================================== -->
      <div id="subTrackNova" class="hidden grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- Esquerda: Formulário Cold Start -->
        <div class="lg:col-span-5 space-y-6">
          <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 shadow-xl">
            <h3 class="text-base font-bold text-white mb-1 flex items-center gap-2">
              <span>🧬</span> Criar Nova Persona do Zero (Cold Start)
            </h3>
            <p class="text-xs text-gray-400 mb-5">Suba a imagem de referência do Pinterest/web. O MIRR0R™ extrai o DNA completo e gera o Face Board Collage 16:9.</p>

            <form onsubmit="enviarCriarPersona(event)" class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-gray-300 mb-1.5">Nome da Nova Persona</label>
                <input type="text" id="novaNome" required placeholder="Ex: Valéria, Maya, Luna, Elena" 
                       class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition">
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-300 mb-1.5">Nicho Comercial / Arquétipo</label>
                <input type="text" id="novaNicho" required placeholder="Ex: Fitness & Treino, Moda Streetwear, Tech, etc." 
                       class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition">
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-300 mb-1.5">Acessório Assinatura (Opcional)</label>
                <input type="text" id="novaAcessorio" placeholder="Ex: Brinco de argola dourada, colar fino de prata..." 
                       class="w-full bg-[#0b0f17] border border-gray-800 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition">
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-300 mb-1.5">Foto de Referência (Pinterest ou Matriz do Rosto)</label>
                <div id="dropzoneNova" class="border-2 border-dashed border-gray-700 hover:border-indigo-500 rounded-xl p-5 text-center cursor-pointer bg-[#0b0f17]/50 transition">
                  <input type="file" id="novaImagem" required accept="image/*" class="hidden" onchange="previewNovaImage(this)">
                  <div id="dropTextNova">
                    <div class="text-2xl mb-1">📸</div>
                    <p class="text-xs font-medium text-gray-300">Clique para selecionar foto do Pinterest ou matriz</p>
                    <p class="text-[11px] text-gray-500 mt-1">PNG, JPG até 10MB</p>
                  </div>
                  <div id="previewContainerNova" class="hidden">
                    <img id="imgPreviewNova" class="max-h-36 mx-auto rounded-lg object-contain mb-2">
                    <p id="fileNameNova" class="text-xs text-indigo-400 font-mono"></p>
                  </div>
                </div>
              </div>

              <button type="submit" id="btnSubmitNova" class="w-full bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 hover:opacity-95 text-white font-bold text-xs py-3.5 px-4 rounded-xl shadow-lg transition flex items-center justify-center gap-2">
                <span>🧬</span>
                <span id="btnTextNova">Extrair DNA Visual no MIRR0R™ & Registrar Persona</span>
              </button>
            </form>

            <div id="loadingNova" class="hidden mt-4 p-4 bg-indigo-950/30 border border-indigo-800/40 rounded-xl">
              <div class="flex items-center space-x-3">
                <div class="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                <p class="text-xs text-indigo-300 font-medium">Extraindo DNA no Gemini Vision e compilando Face Board 16:9...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Direita: Resultados Caminho 2 -->
        <div class="lg:col-span-7 space-y-6">
          <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 min-h-[500px]">
            <div class="flex items-center justify-between border-b border-gray-800 pb-4 mb-5">
              <div>
                <h3 class="text-base font-bold text-white flex items-center gap-2">
                  <span>✨</span> Nova Persona Cadastrada & Face Board (Matriz de Face Lock)
                </h3>
                <p class="text-xs text-gray-400">Pronta para cadastrar a Coleção no Google Flow.</p>
              </div>
              <div id="statusBadgeNova" class="hidden">
                <span class="text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full">Persona Registrada!</span>
              </div>
            </div>

            <div id="novaEmptyState" class="py-20 text-center">
              <div class="text-5xl mb-3 opacity-30">🧬</div>
              <h4 class="text-sm font-semibold text-gray-300">Nenhuma nova persona criada nesta sessão</h4>
              <p class="text-xs text-gray-500 max-w-sm mx-auto mt-1">Preencha o formulário ao lado e envie a foto de referência para gerar a colagem de 9 ângulos para o Flow.</p>
            </div>

            <div id="novaResultBox" class="hidden space-y-4">
              <!-- Instruções Flow -->
              <div class="p-3.5 bg-indigo-950/30 border border-indigo-500/30 rounded-xl text-xs text-indigo-200">
                <strong>💡 Próximo Passo no Google Flow:</strong> Copie o <strong>Prompt do Face Board Collage 16:9</strong> abaixo, cole no Flow em proporção 16:9. Na imagem de 9 ângulos gerada, clique com o botão direito / três pontos e selecione <em>"Adicionar a nova coleção"</em> com o nome da persona!
              </div>

              <!-- 1. Face Board Collage 16:9 Prompt -->
              <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-bold text-amber-400 flex items-center gap-1.5">
                    <span>📸</span> 1. Prompt Face Board Collage 16:9 (Matriz de Consistência Multi-Ângulo)
                  </span>
                  <button onclick="copiarTexto('novaFaceBoardCode', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar Face Board</button>
                </div>
                <div id="novaFaceBoardCode" class="text-xs text-gray-200 bg-[#070a10] p-3 rounded-lg max-h-48 overflow-y-auto leading-relaxed border border-gray-900"></div>
              </div>

              <!-- 2. Master Ground Truth Prompt -->
              <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                    <span>🎯</span> 2. Master Prompt Matriz Ground Truth (9:16)
                  </span>
                  <button onclick="copiarTexto('novaMasterCode', this)" class="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-2.5 py-1 rounded-md transition font-medium">Copiar Matriz</button>
                </div>
                <div id="novaMasterCode" class="text-xs text-gray-200 bg-[#070a10] p-3 rounded-lg max-h-36 overflow-y-auto leading-relaxed border border-gray-900"></div>
              </div>

              <!-- 3. DNA Resumido -->
              <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-4">
                <span class="text-xs font-bold text-indigo-400 flex items-center gap-1.5 mb-2">
                  <span>🧬</span> 3. DNA Visual Registrado no Sistema
                </span>
                <pre id="novaDnaCode" class="text-xs text-gray-300 bg-[#070a10] p-3 rounded-lg overflow-x-auto max-h-40 leading-relaxed border border-gray-900"></pre>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- ======================================================== -->
    <!-- ETAPA 4: PÓS-PRODUÇÃO ANTI-IA (FFMPEG) & MOTION          -->
    <!-- ======================================================== -->
    <div id="tabPosProducao" class="tab-content hidden space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Esquerda: Calibrador FFmpeg em 1 Clique -->
        <div class="lg:col-span-6 space-y-6">
          <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 shadow-xl">
            <div class="flex items-center justify-between mb-2">
              <h3 class="text-base font-bold text-white flex items-center gap-2">
                <span>⚡</span> Calibrador Anti-IA Automático (FFmpeg Engine)
              </h3>
              <span class="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full uppercase tracking-wider">
                1-Clique // Zero Edição Manual
              </span>
            </div>
            <p class="text-xs text-gray-400 mb-5">
              Elimina o brilho plástico e textura artificial de IA aplicando curvas de exposição de câmera real (-29% highlights, +10% shadows, -3% exp) e injeção de ruído orgânico de sensor mobile.
            </p>

            <form id="formCalibrar" onsubmit="enviarCalibrarVideo(event)" class="space-y-4">
              
              <!-- Detector de Vídeo Recente -->
              <div id="boxVideoRecente" class="p-4 bg-indigo-950/30 border border-indigo-500/30 rounded-xl">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-xs font-bold text-indigo-300 flex items-center gap-1.5">
                    <span>🎬</span> Vídeo Detectado na Área de Trabalho:
                  </span>
                  <span id="badgeRecenteSize" class="text-[10px] text-gray-400 font-mono"></span>
                </div>
                <p id="nomeVideoRecente" class="text-xs font-mono text-emerald-400 truncate mb-3">Verificando...</p>
                <label class="flex items-center space-x-2 cursor-pointer text-xs text-gray-300 font-medium">
                  <input type="checkbox" id="checkUsarRecente" checked onchange="toggleUsarRecente(this)" class="w-4 h-4 rounded text-indigo-600 bg-gray-900 border-gray-700 focus:ring-indigo-500">
                  <span>Processar este vídeo recente automaticamente</span>
                </label>
              </div>

              <!-- Upload de Outro Vídeo Opcional -->
              <div id="boxUploadVideo" class="space-y-1.5 opacity-50">
                <label class="block text-xs font-semibold text-gray-400">Ou selecione outro arquivo MP4:</label>
                <div id="dropzoneVideo" class="border-2 border-dashed border-gray-700 hover:border-indigo-500 rounded-xl p-4 text-center cursor-pointer bg-[#0b0f17]/50 transition">
                  <input type="file" id="inputVideoCustom" accept="video/mp4,video/*" class="hidden" onchange="previewVideoUpload(this)">
                  <div id="dropTextVideo">
                    <div class="text-xl mb-1">📼</div>
                    <p class="text-xs font-medium text-gray-300">Clique para selecionar outro arquivo MP4</p>
                  </div>
                  <p id="fileNameVideo" class="text-xs text-indigo-400 font-mono hidden mt-1"></p>
                </div>
              </div>

              <!-- Parâmetros Numéricos Aplicados pelo Motor -->
              <div class="grid grid-cols-4 gap-2 text-center text-xs">
                <div class="bg-[#0b0f17] p-2 rounded-lg border border-gray-800">
                  <div class="text-[10px] text-gray-400">Exposição</div>
                  <div class="font-bold text-rose-400 font-mono">-3%</div>
                </div>
                <div class="bg-[#0b0f17] p-2 rounded-lg border border-gray-800">
                  <div class="text-[10px] text-gray-400">Highlights</div>
                  <div class="font-bold text-amber-400 font-mono">-29%</div>
                </div>
                <div class="bg-[#0b0f17] p-2 rounded-lg border border-gray-800">
                  <div class="text-[10px] text-gray-400">Shadows</div>
                  <div class="font-bold text-emerald-400 font-mono">+10%</div>
                </div>
                <div class="bg-[#0b0f17] p-2 rounded-lg border border-gray-800">
                  <div class="text-[10px] text-gray-400">Sensor Noise</div>
                  <div class="font-bold text-indigo-400 font-mono">+3%</div>
                </div>
              </div>

              <button type="submit" id="btnSubmitCalibrar" class="w-full bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 hover:opacity-95 text-white font-bold text-xs py-3.5 px-4 rounded-xl shadow-lg transition flex items-center justify-center gap-2">
                <span>⚡</span>
                <span id="btnTextCalibrar">Calibrar Vídeo Anti-IA (FFmpeg Engine)</span>
              </button>
            </form>

            <div id="loadingCalibrar" class="hidden mt-4 p-4 bg-indigo-950/30 border border-indigo-800/40 rounded-xl">
              <div class="flex items-center space-x-3">
                <div class="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
                <p class="text-xs text-indigo-300 font-medium">Processando color grading e renderizando em 1080p MP4 via FFmpeg...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Direita: Central de Comparação & Master Final -->
        <div class="lg:col-span-6 space-y-6">
          <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6 min-h-[500px]">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between border-b border-gray-800 pb-4 mb-5 gap-2">
              <div>
                <h3 class="text-base font-bold text-white flex items-center gap-2">
                  <span>🎥</span> Central de Comparação & Master
                </h3>
                <p class="text-xs text-gray-400">Auditoria visual de texturas, curvas e entrega final.</p>
              </div>
              <span id="badgeCalibradoSuccess" class="hidden text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full self-start">
                Calibrado ✓
              </span>
            </div>

            <div id="calibradoEmptyState" class="py-24 text-center">
              <div class="text-5xl mb-3 opacity-30">🎬</div>
              <h4 class="text-sm font-semibold text-gray-300">Nenhum vídeo calibrado ainda</h4>
              <p class="text-xs text-gray-500 max-w-sm mx-auto mt-1">
                Clique no botão ao lado para processar o vídeo do Veo e gerar o comparativo Antes/Depois e a master final.
              </p>
            </div>

            <div id="calibradoResultBox" class="hidden space-y-5">
              <!-- Seletor de Modo de Visualização -->
              <div class="flex items-center bg-[#0b0f17] p-1.5 rounded-xl border border-gray-800">
                <button type="button" onclick="switchModoPlayer('split')" id="btnModoSplit" class="flex-1 py-2 text-xs font-bold rounded-lg bg-indigo-600 text-white transition flex items-center justify-center gap-1.5">
                  <span>🌓</span> Split 50/50
                </button>
                <button type="button" onclick="switchModoPlayer('dual')" id="btnModoDual" class="flex-1 py-2 text-xs font-semibold rounded-lg text-gray-400 hover:text-white transition flex items-center justify-center gap-1.5">
                  <span>👥</span> Lado a Lado
                </button>
                <button type="button" onclick="switchModoPlayer('master')" id="btnModoMaster" class="flex-1 py-2 text-xs font-semibold rounded-lg text-gray-400 hover:text-white transition flex items-center justify-center gap-1.5">
                  <span>✨</span> Master Limpo
                </button>
              </div>

              <!-- MODO 1: SPLIT SCREEN (50/50 Cortado ao Meio com Linha) -->
              <div id="viewSplitScreen" class="space-y-3">
                <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-3 flex justify-center relative">
                  <video id="playerSplitScreen" controls class="rounded-lg max-h-80 w-auto shadow-2xl bg-black" playsinline></video>
                </div>
                <div class="grid grid-cols-2 gap-2 text-[11px]">
                  <div class="bg-rose-950/20 border border-rose-900/40 p-2.5 rounded-lg text-rose-300">
                    <span class="font-bold flex items-center gap-1 mb-0.5"><span>👈</span> Antes (Bruto Veo)</span>
                    <p class="text-[10px] text-gray-400">Highlights estourados na testa/pele, aspecto plástico de render 3D.</p>
                  </div>
                  <div class="bg-emerald-950/20 border border-emerald-900/40 p-2.5 rounded-lg text-emerald-300">
                    <span class="font-bold flex items-center gap-1 mb-0.5"><span>👉</span> Depois (Anti-IA)</span>
                    <p class="text-[10px] text-gray-400">Rolloff de luz orgânico (-29%), ruído de sensor real (+3%), 1080p.</p>
                  </div>
                </div>
              </div>

              <!-- MODO 2: DUAL PLAYER LADO A LADO -->
              <div id="viewDualPlayer" class="hidden space-y-3">
                <div class="grid grid-cols-2 gap-3">
                  <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-2 text-center">
                    <div class="text-[10px] font-bold text-rose-400 mb-1.5">ANTES (Bruto Veo)</div>
                    <video id="playerDualRaw" class="rounded-lg max-h-60 w-auto mx-auto bg-black" playsinline muted></video>
                  </div>
                  <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-2 text-center">
                    <div class="text-[10px] font-bold text-emerald-400 mb-1.5">DEPOIS (Anti-IA)</div>
                    <video id="playerDualCalibrado" class="rounded-lg max-h-60 w-auto mx-auto bg-black" playsinline></video>
                  </div>
                </div>
                <div class="flex items-center justify-center gap-3">
                  <button type="button" onclick="playPauseDualSync()" id="btnDualPlaySync" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-md">
                    <span>▶️</span> Reproduzir Ambos Sincronizados
                  </button>
                  <button type="button" onclick="resetDualSync()" class="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs font-medium transition">
                    🔄 Reiniciar
                  </button>
                </div>
              </div>

              <!-- MODO 3: MASTER FINAL LIMPO -->
              <div id="viewMasterClean" class="hidden space-y-3">
                <div class="bg-[#0b0f17] border border-gray-800 rounded-xl p-3 flex justify-center">
                  <video id="playerMasterClean" controls class="rounded-lg max-h-80 w-auto shadow-2xl bg-black" playsinline></video>
                </div>
                <p class="text-[11px] text-gray-400 text-center">Master em 1080x1920 (Full HD vertical) sem marcas, pronto para tráfego pago ou orgânico.</p>
              </div>

              <!-- Botões de Download / Arquivos na Área de Trabalho -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <a id="btnDownloadCalibrado" href="#" download class="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-3 px-3 rounded-xl transition text-center shadow-md flex items-center justify-center gap-1.5 truncate">
                  <span>⬇️</span> Baixar Master (Anti-IA)
                </a>
                <a id="btnDownloadSplit" href="#" download class="bg-[#0b0f17] hover:bg-[#1a2233] border border-gray-700 hover:border-indigo-500 text-gray-200 font-bold text-xs py-3 px-3 rounded-xl transition text-center shadow-md flex items-center justify-center gap-1.5 truncate">
                  <span>🎬</span> Baixar Split-Screen
                </a>
              </div>

              <div class="p-3 bg-emerald-950/20 border border-emerald-800/30 rounded-xl text-center">
                <p class="text-[11px] text-emerald-400 font-medium">
                  ✓ Arquivos salvos automaticamente na sua <strong>Área de Trabalho</strong> como:
                </p>
                <div class="flex flex-col gap-1 mt-1 text-[10px] font-mono text-gray-300">
                  <span>• SYNTHIA_CALIBRADA_ANTI_IA.mp4</span>
                  <span>• SYNTHIA_COMPARATIVO_SPLIT_SCREEN.mp4</span>
                </div>
              </div>

            </div>
          </div>
        </div>

      </div>

      <!-- Seção Workflows RunningHub (ComfyUI na Nuvem) -->
      <div class="bg-[#131926] border border-gray-800 rounded-2xl p-6">
        <h3 class="text-base font-bold text-white mb-2 flex items-center gap-2">
          <span>⚡</span> Workflows Motion Transfer (ComfyUI na Nuvem / RunningHub)
        </h3>
        <p class="text-xs text-gray-400 mb-4">Utilize para transferir movimentos humanos reais de vídeos virais longos para a persona sem limitações de corte:</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a href="https://www.runninghub.ai/workflow/2006208707331362818?inviteCode=dn1kdyu2" target="_blank" class="block p-4 bg-[#0b0f17] border border-gray-800 hover:border-indigo-500 rounded-xl transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-white">Workflow Versão Beta (v1)</span>
              <span class="text-xs text-indigo-400">Abrir no RunningHub ↗</span>
            </div>
            <p class="text-[11px] text-gray-500 mt-1">Workflow otimizado para retenção facial e movimentos corporais naturais.</p>
          </a>

          <a href="https://www.runninghub.ai/workflow/2019833931192868866?inviteCode=dn1kdyu2" target="_blank" class="block p-4 bg-[#0b0f17] border border-gray-800 hover:border-indigo-500 rounded-xl transition">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-white">Workflow Versão Alpha (v2)</span>
              <span class="text-xs text-indigo-400">Abrir no RunningHub ↗</span>
            </div>
            <p class="text-[11px] text-gray-500 mt-1">Versão aprimorada com maior fidelidade de tecido, microexpressões e caimento.</p>
          </a>
        </div>
      </div>

    </div>

  </main>

  <script>
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-indigo-500', 'text-indigo-400');
        btn.classList.add('border-transparent', 'text-gray-400');
      });

      document.getElementById(tabId).classList.remove('hidden');
      if (tabId === 'tabPersonas') document.getElementById('btnTabPersonas').className = 'tab-btn px-4 py-3 text-xs font-bold border-b-2 border-indigo-500 text-indigo-400 flex items-center gap-2';
      if (tabId === 'tabVideo') document.getElementById('btnTabVideo').className = 'tab-btn px-4 py-3 text-xs font-bold border-b-2 border-indigo-500 text-indigo-400 flex items-center gap-2';
      if (tabId === 'tabEcommerce') document.getElementById('btnTabEcommerce').className = 'tab-btn px-4 py-3 text-xs font-bold border-b-2 border-indigo-500 text-indigo-400 flex items-center gap-2';
      if (tabId === 'tabPosProducao') document.getElementById('btnTabPosProducao').className = 'tab-btn px-4 py-3 text-xs font-bold border-b-2 border-indigo-500 text-indigo-400 flex items-center gap-2';
    }

    const dropzone = document.getElementById('dropzone');
    const inputImg = document.getElementById('imagem');

    dropzone.onclick = () => inputImg.click();
    dropzone.ondragover = (e) => { e.preventDefault(); dropzone.classList.add('border-indigo-500'); };
    dropzone.ondragleave = () => dropzone.classList.remove('border-indigo-500');
    dropzone.ondrop = (e) => {
      e.preventDefault();
      dropzone.classList.remove('border-indigo-500');
      if (e.dataTransfer.files.length) {
        inputImg.files = e.dataTransfer.files;
        previewImage(inputImg);
      }
    };

    function previewImage(input) {
      if (input.files && input.files[0]) {
        const file = input.files[0];
        document.getElementById('fileName').innerText = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          document.getElementById('imgPreview').src = e.target.result;
          document.getElementById('dropText').classList.add('hidden');
          document.getElementById('previewContainer').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
      }
    }

    async function enviarCampanha(e) {
      e.preventDefault();
      const loja = document.getElementById('loja').value;
      const cenario = document.getElementById('cenario').value;
      const personaId = document.getElementById('lojaPersonaId') ? document.getElementById('lojaPersonaId').value : 'synthia';
      const file = inputImg.files[0];

      if (!file) {
        alert('Por favor, selecione uma foto do produto!');
        return;
      }

      const formData = new FormData();
      formData.append('loja', loja);
      formData.append('cenario', cenario);
      formData.append('persona_id', personaId);
      formData.append('imagem', file);

      document.getElementById('btnSubmit').disabled = true;
      document.getElementById('btnText').innerText = 'Processando com MIRR0R™...';
      document.getElementById('loading').classList.remove('hidden');

      try {
        const res = await fetch('/api/campanha', { method: 'POST', body: formData });
        const data = await res.json();
        
        if (data.status === 'success') {
          const camp = data.campanha;
          document.getElementById('promptFlowCode').innerText = JSON.stringify(camp.flow_prompt_json, null, 2);
          document.getElementById('videoScriptCode').innerText = camp.video_prompt;
          
          document.getElementById('emptyState').classList.add('hidden');
          document.getElementById('resultContent').classList.remove('hidden');
          document.getElementById('statusBadge').classList.remove('hidden');
        } else {
          alert('Erro ao processar: ' + JSON.stringify(data));
        }
      } catch (err) {
        alert('Erro na requisição: ' + err);
      } finally {
        document.getElementById('btnSubmit').disabled = false;
        document.getElementById('btnText').innerText = 'Gerar Campanha Completa (DNA + Flow + Veo 3.1)';
        document.getElementById('loading').classList.add('hidden');
      }
    }

    const PRESETS_FALA = {
      joia: {
        fala: "Olha o reflexo e o corte dessa peça na luz natural... Os detalhes do acabamento são simplesmente impecáveis. O que vocês acharam?",
        voz: "sofisticada_aveludada",
        foco: "produto",
        camera: "macro push-in focusing sharply on the jewelry piece and its light reflection",
        cenario: "standing in front of a warm illuminated mirror, soft diffuse morning light reflecting on the jewelry"
      },
      provador: {
        fala: "Gente, para tudo... olhem o caimento dessa peça no corpo. O tecido é levíssimo e modela sem marcar nada. Vocês usariam?",
        voz: "criadora_conteudo",
        foco: "look",
        camera: "tilt down showing the full outfit drape, then returning to her smiling eyes",
        cenario: "standing in an upscale boutique fitting room with warm ambient mirror lighting, elegant fabric textures"
      },
      viral: {
        fala: "Ainda dizem por aí que eu sou apenas um prompt... Então chega um pouco mais perto. Assusta o quanto parece real, né?",
        voz: "jovem_espontanea",
        foco: "rosto",
        camera: "slow smooth zoom gliding physically towards her face, extreme close-up on eyes and pores",
        cenario: "lying comfortably on bed against cream pillows, soft diffuse morning window light from the left"
      },
      beleza: {
        fala: "Vocês vivem me perguntando o que eu passo na pele de manhã... vou contar meu segredo agora, mas não espalha pra ninguém, tá?",
        voz: "confessional_intima",
        foco: "rosto",
        camera: "slow smooth zoom gliding physically towards her face, extreme close-up on eyes and pores",
        cenario: "sitting in front of a warm illuminated vanity mirror, soft glowing morning light"
      },
      publi: {
        fala: "Consegui um cupom exclusivo de 20% pra vocês nessa coleção da loja! Mas corre no link da bio porque o estoque tá voando...",
        voz: "criadora_conteudo",
        foco: "vlog",
        camera: "gentle breathing sway of handheld smartphone frame, relaxed and intimate",
        cenario: "modern bright apartment living room with sunlight pouring in, holding phone casually"
      },
      sofisticada: {
        fala: "Tem dias em que menos é mais. Uma peça bem cortada muda completamente a sua presença sem você precisar dizer nada.",
        voz: "sofisticada_aveludada",
        foco: "look",
        camera: "tilt down showing the full outfit drape, then returning to her smiling eyes",
        cenario: "sitting in an elegant European terrace cafe in Milan, soft golden hour sunlight"
      }
    };

    function aplicarPresetFala(tipo) {
      const p = PRESETS_FALA[tipo];
      if (!p) return;
      document.getElementById('videoFala').value = p.fala;
      if (document.getElementById('videoVoz') && p.voz) document.getElementById('videoVoz').value = p.voz;
      if (document.getElementById('videoCamera') && p.camera) document.getElementById('videoCamera').value = p.camera;
      if (document.getElementById('videoCenario') && p.cenario) document.getElementById('videoCenario').value = p.cenario;
      if (document.getElementById('videoFocoVisual') && p.foco) document.getElementById('videoFocoVisual').value = p.foco;
    }

    async function gerarFalaAutomaticaIa() {
      const temaInput = document.getElementById('inputTemaIa');
      const tema = temaInput.value.trim() || 'vestido elegante de festa';
      const btn = document.getElementById('btnGerarFalaIa');
      const originalText = btn.innerHTML;

      btn.disabled = true;
      btn.innerHTML = '<span>⏳</span> Criando...';

      try {
        const formData = new FormData();
        formData.append('tema', tema);
        formData.append('tom', 'provador');

        const res = await fetch('/api/video/gerar-fala', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.status === 'success' && data.fala) {
          document.getElementById('videoFala').value = data.fala;
        } else {
          alert('Erro ao gerar fala: ' + JSON.stringify(data));
        }
      } catch (err) {
        alert('Erro ao conectar com assistente: ' + err);
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }

    async function gerarVideoHumano(e) {
      e.preventDefault();
      const fala = document.getElementById('videoFala').value;
      const camera = document.getElementById('videoCamera').value;
      const cenario = document.getElementById('videoCenario') ? document.getElementById('videoCenario').value : 'lying comfortably on bed against cream pillows, soft diffuse morning window light from the left';
      const vocalStyle = document.getElementById('videoVoz') ? document.getElementById('videoVoz').value : 'jovem_espontanea';
      const personaId = document.getElementById('videoPersonaId') ? document.getElementById('videoPersonaId').value : 'synthia';
      const focoVisual = document.getElementById('videoFocoVisual') ? document.getElementById('videoFocoVisual').value : 'produto';

      document.getElementById('btnSubmitVideo').disabled = true;
      document.getElementById('btnTextVideo').innerText = 'Sintetizando Prompt & DNA Acústico...';

      const formData = new FormData();
      formData.append('fala', fala);
      formData.append('camera', camera);
      formData.append('cenario', cenario);
      formData.append('vocal_style', vocalStyle);
      formData.append('persona_id', personaId);
      formData.append('foco_visual', focoVisual);

      try {
        const res = await fetch('/api/video-humano', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.status === 'success') {
          document.getElementById('videoPromptOutput').innerText = data.video_prompt;
          
          if (document.getElementById('boxAudioTag') && data.acoustic_tag) {
            document.getElementById('audioTagOutput').innerText = data.acoustic_tag;
            document.getElementById('boxAudioTag').classList.remove('hidden');
          }
          if (document.getElementById('boxVeoJson') && data.veo_json) {
            document.getElementById('veoJsonOutput').innerText = JSON.stringify(data.veo_json, null, 2);
            document.getElementById('boxVeoJson').classList.remove('hidden');
          }
        } else {
          alert('Erro ao gerar vídeo: ' + JSON.stringify(data));
        }
      } catch (err) {
        alert('Erro: ' + err);
      } finally {
        document.getElementById('btnSubmitVideo').disabled = false;
        document.getElementById('btnTextVideo').innerText = 'Sintetizar Prompt Comportamental & Acústico (Veo 3.1)';
      }
    }

    // Alterna sub-abas da aba 3 (Personas)
    function switchPersonaSubTrack(track) {
      const elExistente = document.getElementById('subTrackExistente');
      const elNova = document.getElementById('subTrackNova');
      const btnExistente = document.getElementById('btnSubTrackExistente');
      const btnNova = document.getElementById('btnSubTrackNova');

      if (track === 'trackExistente') {
        elExistente.classList.remove('hidden');
        elNova.classList.add('hidden');
        btnExistente.className = 'px-4 py-2 text-xs font-bold rounded-lg bg-indigo-600 text-white transition flex items-center gap-2';
        btnNova.className = 'px-4 py-2 text-xs font-semibold rounded-lg text-gray-400 hover:text-white transition flex items-center gap-2';
      } else {
        elExistente.classList.add('hidden');
        elNova.classList.remove('hidden');
        btnNova.className = 'px-4 py-2 text-xs font-bold rounded-lg bg-indigo-600 text-white transition flex items-center gap-2';
        btnExistente.className = 'px-4 py-2 text-xs font-semibold rounded-lg text-gray-400 hover:text-white transition flex items-center gap-2';
      }
    }

    // Drag and drop para Caminho 2 (Nova Persona)
    const dropzoneNova = document.getElementById('dropzoneNova');
    const inputImgNova = document.getElementById('novaImagem');

    if (dropzoneNova && inputImgNova) {
      dropzoneNova.onclick = () => inputImgNova.click();
      dropzoneNova.ondragover = (e) => { e.preventDefault(); dropzoneNova.classList.add('border-indigo-500'); };
      dropzoneNova.ondragleave = () => dropzoneNova.classList.remove('border-indigo-500');
      dropzoneNova.ondrop = (e) => {
        e.preventDefault();
        dropzoneNova.classList.remove('border-indigo-500');
        if (e.dataTransfer.files.length) {
          inputImgNova.files = e.dataTransfer.files;
          previewNovaImage(inputImgNova);
        }
      };
    }

    function previewNovaImage(input) {
      if (input.files && input.files[0]) {
        const file = input.files[0];
        document.getElementById('fileNameNova').innerText = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          document.getElementById('imgPreviewNova').src = e.target.result;
          document.getElementById('dropTextNova').classList.add('hidden');
          document.getElementById('previewContainerNova').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
      }
    }

    // Caminho 1: Enviar Nova Cena de Persona Existente
    async function enviarCenaPersona(e) {
      e.preventDefault();
      const personaId = document.getElementById('cenaPersonaId').value;
      const cenario = document.getElementById('cenaDescricao').value;
      const proporcao = document.getElementById('cenaProporcao').value;
      const luz = document.getElementById('cenaLuz').value;

      document.getElementById('btnSubmitCena').disabled = true;
      document.getElementById('btnTextCena').innerText = 'Blindando Face Lock e Gerando...';

      const formData = new FormData();
      formData.append('persona_id', personaId);
      formData.append('cenario', cenario);
      formData.append('proporcao', proporcao);
      formData.append('estilo_luz', luz);

      try {
        const res = await fetch('/api/persona/gerar-cena', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.status === 'success') {
          document.getElementById('cenaFlowCode').innerText = JSON.stringify(data.flow_json, null, 2);
          document.getElementById('cenaMasterCode').innerText = data.master_prompt;
          document.getElementById('cenaVeoCode').innerText = data.veo_prompt;

          if (data.collection_url) {
            document.getElementById('cenaFlowLink').href = data.collection_url;
          }

          document.getElementById('cenaEmptyState').classList.add('hidden');
          document.getElementById('cenaResultBox').classList.remove('hidden');
        } else {
          alert('Erro ao gerar cena: ' + JSON.stringify(data));
        }
      } catch (err) {
        alert('Erro na requisição: ' + err);
      } finally {
        document.getElementById('btnSubmitCena').disabled = false;
        document.getElementById('btnTextCena').innerText = 'Gerar Pacote de Cena (MIRR0R JSON + Veo 3.1)';
      }
    }

    // Caminho 2: Criar Nova Persona do Zero (Cold Start)
    async function enviarCriarPersona(e) {
      e.preventDefault();
      const nome = document.getElementById('novaNome').value;
      const nicho = document.getElementById('novaNicho').value;
      const acessorio = document.getElementById('novaAcessorio').value;
      const file = inputImgNova ? inputImgNova.files[0] : null;

      if (!file) {
        alert('Por favor, selecione uma foto de referência!');
        return;
      }

      document.getElementById('btnSubmitNova').disabled = true;
      document.getElementById('btnTextNova').innerText = 'Analisando DNA com MIRR0R™...';
      document.getElementById('loadingNova').classList.remove('hidden');

      const formData = new FormData();
      formData.append('nome', nome);
      formData.append('nicho', nicho);
      formData.append('acessorio', acessorio);
      formData.append('imagem', file);

      try {
        const res = await fetch('/api/persona/criar', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.status === 'success') {
          document.getElementById('novaFaceBoardCode').innerText = data.face_board_prompt;
          document.getElementById('novaMasterCode').innerText = data.master_prompt;
          document.getElementById('novaDnaCode').innerText = JSON.stringify(data.persona.dna, null, 2);

          document.getElementById('novaEmptyState').classList.add('hidden');
          document.getElementById('novaResultBox').classList.remove('hidden');
          document.getElementById('statusBadgeNova').classList.remove('hidden');

          // Atualiza lista de personas no dropdown do Caminho 1
          atualizarDropdownPersonas();
        } else {
          alert('Erro ao criar persona: ' + JSON.stringify(data));
        }
      } catch (err) {
        alert('Erro na requisição: ' + err);
      } finally {
        document.getElementById('btnSubmitNova').disabled = false;
        document.getElementById('btnTextNova').innerText = 'Extrair DNA Visual no MIRR0R™ & Registrar Persona';
        document.getElementById('loadingNova').classList.add('hidden');
      }
    }

    // Atualiza dropdown de personas
    async function atualizarDropdownPersonas() {
      try {
        const res = await fetch('/api/personas');
        const personas = await res.json();
        const targetIds = ['cenaPersonaId', 'videoPersonaId', 'lojaPersonaId'];
        if (personas && personas.length) {
          targetIds.forEach(id => {
            const select = document.getElementById(id);
            if (select) {
              const currentVal = select.value;
              select.innerHTML = '';
              personas.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                const niche = p.commercial_profile?.primary_niche || p.archetype || 'Ativa';
                opt.text = `${p.name} (${niche})`;
                select.appendChild(opt);
              });
              if (currentVal && Array.from(select.options).some(o => o.value === currentVal)) {
                select.value = currentVal;
              }
            }
          });
        }
      } catch (err) {
        console.error('Erro ao listar personas:', err);
      }
    }

    // ETAPA 4: Pós-Produção Anti-IA (FFmpeg)
    let videoRecenteDetectado = null;

    async function verificarVideoRecente() {
      try {
        const res = await fetch('/api/pos-producao/video-recente');
        const data = await res.json();
        const nomeEl = document.getElementById('nomeVideoRecente');
        const sizeEl = document.getElementById('badgeRecenteSize');
        if (data.exists) {
          videoRecenteDetectado = data;
          nomeEl.innerText = data.filename;
          sizeEl.innerText = data.size_mb + ' MB';
          document.getElementById('checkUsarRecente').checked = true;
          document.getElementById('boxUploadVideo').classList.add('opacity-50');
        } else {
          nomeEl.innerText = 'Nenhum vídeo recente detectado na Área de Trabalho.';
          document.getElementById('checkUsarRecente').checked = false;
          document.getElementById('boxUploadVideo').classList.remove('opacity-50');
        }
      } catch (err) {
        console.error('Erro ao verificar vídeo recente:', err);
      }
    }

    function toggleUsarRecente(cb) {
      const boxUpload = document.getElementById('boxUploadVideo');
      if (cb.checked) {
        boxUpload.classList.add('opacity-50');
      } else {
        boxUpload.classList.remove('opacity-50');
      }
    }

    const dropzoneVideo = document.getElementById('dropzoneVideo');
    const inputVideoCustom = document.getElementById('inputVideoCustom');
    if (dropzoneVideo && inputVideoCustom) {
      dropzoneVideo.onclick = () => inputVideoCustom.click();
      dropzoneVideo.ondragover = (e) => { e.preventDefault(); dropzoneVideo.classList.add('border-indigo-500'); };
      dropzoneVideo.ondragleave = () => dropzoneVideo.classList.remove('border-indigo-500');
      dropzoneVideo.ondrop = (e) => {
        e.preventDefault();
        dropzoneVideo.classList.remove('border-indigo-500');
        if (e.dataTransfer.files.length) {
          inputVideoCustom.files = e.dataTransfer.files;
          previewVideoUpload(inputVideoCustom);
        }
      };
    }

    function previewVideoUpload(input) {
      if (input.files && input.files[0]) {
        const file = input.files[0];
        document.getElementById('fileNameVideo').innerText = file.name;
        document.getElementById('fileNameVideo').classList.remove('hidden');
        document.getElementById('checkUsarRecente').checked = false;
        document.getElementById('boxUploadVideo').classList.remove('opacity-50');
      }
    }

    // Alterna modos de visualização do player
    function switchModoPlayer(modo) {
      document.getElementById('viewSplitScreen').classList.add('hidden');
      document.getElementById('viewDualPlayer').classList.add('hidden');
      document.getElementById('viewMasterClean').classList.add('hidden');

      const btnSplit = document.getElementById('btnModoSplit');
      const btnDual = document.getElementById('btnModoDual');
      const btnMaster = document.getElementById('btnModoMaster');

      const inactiveClass = 'flex-1 py-2 text-xs font-semibold rounded-lg text-gray-400 hover:text-white transition flex items-center justify-center gap-1.5';
      const activeClass = 'flex-1 py-2 text-xs font-bold rounded-lg bg-indigo-600 text-white transition flex items-center justify-center gap-1.5';

      btnSplit.className = inactiveClass;
      btnDual.className = inactiveClass;
      btnMaster.className = inactiveClass;

      if (modo === 'split') {
        document.getElementById('viewSplitScreen').classList.remove('hidden');
        btnSplit.className = activeClass;
      } else if (modo === 'dual') {
        document.getElementById('viewDualPlayer').classList.remove('hidden');
        btnDual.className = activeClass;
      } else if (modo === 'master') {
        document.getElementById('viewMasterClean').classList.remove('hidden');
        btnMaster.className = activeClass;
      }
    }

    let isDualPlaying = false;
    function playPauseDualSync() {
      const vRaw = document.getElementById('playerDualRaw');
      const vCal = document.getElementById('playerDualCalibrado');
      const btn = document.getElementById('btnDualPlaySync');
      if (!isDualPlaying) {
        vRaw.play();
        vCal.play();
        isDualPlaying = true;
        btn.innerHTML = '<span>⏸️</span> Pausar Ambos';
      } else {
        vRaw.pause();
        vCal.pause();
        isDualPlaying = false;
        btn.innerHTML = '<span>▶️</span> Reproduzir Ambos Sincronizados';
      }
    }

    function resetDualSync() {
      const vRaw = document.getElementById('playerDualRaw');
      const vCal = document.getElementById('playerDualCalibrado');
      const btn = document.getElementById('btnDualPlaySync');
      vRaw.currentTime = 0;
      vCal.currentTime = 0;
      vRaw.pause();
      vCal.pause();
      isDualPlaying = false;
      btn.innerHTML = '<span>▶️</span> Reproduzir Ambos Sincronizados';
    }

    function exibirResultadosPosProducao(data) {
      // Split player
      const pSplit = document.getElementById('playerSplitScreen');
      if (pSplit && (data.split_url || data.video_url)) {
        pSplit.src = data.split_url || data.video_url;
        pSplit.load();
      }

      // Dual players
      const pDualRaw = document.getElementById('playerDualRaw');
      const pDualCal = document.getElementById('playerDualCalibrado');
      if (pDualRaw && pDualCal) {
        if (data.raw_url) pDualRaw.src = data.raw_url;
        if (data.video_url) pDualCal.src = data.video_url;
        pDualRaw.load();
        pDualCal.load();
      }

      // Master Clean player
      const pMaster = document.getElementById('playerMasterClean');
      if (pMaster && data.video_url) {
        pMaster.src = data.video_url;
        pMaster.load();
      }

      const btnDownCal = document.getElementById('btnDownloadCalibrado');
      if (btnDownCal && data.video_url) {
        btnDownCal.href = data.video_url;
        btnDownCal.download = data.filename || 'SYNTHIA_CALIBRADA_ANTI_IA.mp4';
      }

      const btnDownSplit = document.getElementById('btnDownloadSplit');
      if (btnDownSplit && data.split_url) {
        btnDownSplit.href = data.split_url;
        btnDownSplit.download = data.split_filename || 'SYNTHIA_COMPARATIVO_SPLIT_SCREEN.mp4';
      }

      document.getElementById('calibradoEmptyState').classList.add('hidden');
      document.getElementById('calibradoResultBox').classList.remove('hidden');
      document.getElementById('badgeCalibradoSuccess').classList.remove('hidden');
    }

    async function carregarUltimoCalibrado() {
      try {
        const res = await fetch('/api/pos-producao/ultimo-calibrado');
        const data = await res.json();
        if (data.has_calibrated) {
          exibirResultadosPosProducao(data);
        }
      } catch (err) {
        console.error('Erro ao verificar último calibrado:', err);
      }
    }

    async function enviarCalibrarVideo(e) {
      e.preventDefault();
      const usarRecente = document.getElementById('checkUsarRecente').checked;
      const file = inputVideoCustom ? inputVideoCustom.files[0] : null;

      if (!usarRecente && !file) {
        alert('Selecione um arquivo de vídeo ou marque para usar o vídeo recente!');
        return;
      }

      document.getElementById('btnSubmitCalibrar').disabled = true;
      document.getElementById('btnTextCalibrar').innerText = 'Processando no FFmpeg (Color Grading + Split)...';
      document.getElementById('loadingCalibrar').classList.remove('hidden');

      const formData = new FormData();
      formData.append('usar_recente', usarRecente);
      if (file) {
        formData.append('video', file);
      }

      try {
        const res = await fetch('/api/pos-producao/calibrar', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.status === 'success') {
          exibirResultadosPosProducao(data);
        } else {
          alert('Erro na calibração: ' + JSON.stringify(data));
        }
      } catch (err) {
        alert('Erro na requisição: ' + err);
      } finally {
        document.getElementById('btnSubmitCalibrar').disabled = false;
        document.getElementById('btnTextCalibrar').innerText = 'Calibrar Vídeo Anti-IA (FFmpeg Engine)';
        document.getElementById('loadingCalibrar').classList.add('hidden');
      }
    }

    // Inicialização
    atualizarDropdownPersonas();
    verificarVideoRecente();
    carregarUltimoCalibrado();

    const selVideoPersona = document.getElementById('videoPersonaId');
    if (selVideoPersona) {
      selVideoPersona.addEventListener('change', async () => {
        const pId = selVideoPersona.value;
        try {
          const res = await fetch('/api/personas');
          const personas = await res.json();
          const p = personas.find(item => item.id === pId);
          if (p) {
            const niche = (p.commercial_profile?.primary_niche || '').toLowerCase();
            const fVisual = document.getElementById('videoFocoVisual');
            if (fVisual) {
              if (niche.includes('jóia') || niche.includes('joia') || niche.includes('acessór')) {
                fVisual.value = 'produto';
              } else if (niche.includes('moda') || niche.includes('vestu')) {
                fVisual.value = 'look';
              } else if (niche.includes('beleza') || niche.includes('skin')) {
                fVisual.value = 'rosto';
              }
            }
          }
        } catch (e) {}
      });
    }

    function copiarTexto(elementId, btn) {
      const text = document.getElementById(elementId).innerText;
      navigator.clipboard.writeText(text).then(() => {
        const originalText = btn.innerText;
        btn.innerText = 'Copiado! ✓';
        btn.classList.add('bg-emerald-600', 'text-white');
        setTimeout(() => {
          btn.innerText = originalText;
          btn.classList.remove('bg-emerald-600', 'text-white');
        }, 2000);
      });
    }
  </script>

</body>
</html>
    """
    return html_content

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8088, reload=False)
