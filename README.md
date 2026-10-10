# INFLUENCER STUDIO PRO™ // Enterprise Operating System

Plataforma operacional para criação, direção de arte e roteirização de **Influenciadoras Virtuais Realistas**, Provador Virtual de Marcas (UGC para E-commerce) e Roteirização Comportamental Anti-IA para Google Veo 3.1.

---

## ⚡ Pilares do Sistema

1. **🧬 Etapa 1: Identidade & Face Lock**
   - Cold Start e Extração de DNA Visual 1:1 via MIRR0R Engine (Gemini Vision).
   - Síntese de Face Board Collage (16:9 multi-ângulo) para blindagem de Face Lock no Google Flow / ImageFX.
   - Suporte multi-persona (Synthia, Valentina, Maya ou qualquer personagem customizada).

2. **🎬 Etapa 2: Roteirista Comportamental (HUMAN ENGINE™)**
   - Roteiros falados em Português do Brasil com pausas, respiração humana e dinâmica vocal autêntica.
   - Arquitetura Acústica Anti-IA embutida no prompt do Google Veo 3.1 (sem voz sintética robótica).
   - Enquadramento dinâmico por foco: **💎 Jóia / Produto** (macro com reflexos especulares), **👗 Look Completo**, **💄 Rosto & Expressão** ou **📱 POV Casual**.

3. **🛍️ Etapa 3: Provador Virtual de Marcas & E-commerce (UGC)**
   - Extração do DNA técnico de corte, tecido e caimento de peças físicas da loja.
   - Ajuste fotográfico da influenciadora vestindo o produto sem perder consistência facial.

4. **⚡ Etapa 4: Pós-Produção Anti-IA (FFmpeg Engine)**
   - Color grading cinematográfico (curvas de realismo e ruído analógico de sensor).
   - Renderização comparativa split-screen em tempo real (Antes x Depois).

---

## 🚀 Como Executar Localmente

### Pré-requisitos
* Python 3.10+
* Chave de API do Gemini (`GEMINI_API_KEY` ou `GOOGLE_API_KEY`)
* FFmpeg instalado no PATH (para calibração de vídeo na Etapa 4)

### Instalação
```bash
pip install -r requirements.txt
```

### Inicialização do Servidor
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8088
```
Acesse o dashboard no navegador: `http://127.0.0.1:8088`

---

## ☁️ Deploy na Nuvem (Vercel)

O projeto é 100% compatível com Vercel Serverless Functions (`@vercel/python`):
```bash
vercel --prod
```
*Configure a variável de ambiente `GEMINI_API_KEY` no painel da Vercel.*
