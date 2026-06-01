#!/bin/bash
cd /home/leandro/Documentos/Guardian-AI/MKT_Guardian-AI

echo "🚀 Gerando Agente MKT_AGENT_01..."

# 1. Cria o script Python principal
cat > mkt_agent_01.py << 'FIM_PY'
import os, json, time, requests
from dotenv import load_dotenv
from moviepy.editor import AudioFileClip, ImageClip
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MAX_VIDEOS = int(os.getenv("MAX_VIDEOS_DIARIOS", 10))
OUTPUT_DIR = os.getenv("PASTA_SAIDA", "output_videos")

genai.configure(api_key=GEMINI_KEY)

def gerar_audio(texto, id_video):
    url = "https://api.elevenlabs.io/v1/text-to-speech/EXPERIMENTAL_TTS_VOICE_ID"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {"text": texto, "model_id": "eleven_multilingual_v2"}
    resp = requests.post(url, json=data, headers=headers)
    if resp.status_code == 200:
        path = f"{OUTPUT_DIR}/audio_{id_video}.mp3"
        with open(path, 'wb') as f: f.write(resp.content)
        return path
    print(f"Erro Audio: {resp.text}")
    return None

def gerar_imagem(prompt, id_video):
    img = Image.new('RGB', (1080, 1920), color=(10, 10, 10))
    d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except: font = ImageFont.load_default()
    d.text((50, 900), "Guardian AI\nProteção Familiar", fill=(255, 50, 50), font=font)
    path = f"{OUTPUT_DIR}/img_{id_video}.png"
    img.save(path)
    return path

def montar_video(audio_p, img_p, id_video):
    audio = AudioFileClip(audio_p)
    clip = ImageClip(img_p).set_duration(audio.duration)
    clip = clip.set_fps(24).set_audio(audio)
    out = f"{OUTPUT_DIR}/video_{id_video}.mp4"
    clip.write_videofile(out, codec='libx264', audio_codec='aac')
    os.remove(audio_p); os.remove(img_p)
    return out

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    try:
        with open('roteiros.json', 'r') as f: roteiros = json.load(f)
    except: print("Erro: roteiros.json não encontrado!"); return
    
    print(f"🎬 Produzindo até {MAX_VIDEOS} vídeos...")
    for r in roteiros[:MAX_VIDEOS]:
        print(f"Processando: {r['titulo']}")
        aud = gerar_audio(r['texto_narracao'], r['id'])
        img = gerar_imagem(r['prompt_imagem'], r['id'])
        if aud and img:
            final = montar_video(aud, img, r['id'])
            print(f"✅ Sucesso: {final}")

if __name__ == "__main__": main()
FIM_PY

# 2. Cria o arquivo .env
cat > .env << 'FIM_ENV'
ELEVENLABS_API_KEY=COLE_SUA_CHAVE_AQUI
GEMINI_API_KEY=COLE_SUA_CHAVE_AQUI
MAX_VIDEOS_DIARIOS=10
PASTA_SAIDA=output_videos
FIM_ENV

# 3. Cria o exemplo de roteiros
cat > roteiros.json << 'FIM_JSON'
[
  {"id": "v1", "titulo": "Golpe PIX", "texto_narracao": "Atenção! Novo golpe do PIX mirando idosos.", "prompt_imagem": "Alerta vermelho celular"},
  {"id": "v2", "titulo": "Proteção Kids", "texto_narracao": "Proteja seus filhos de assédio online agora.", "prompt_imagem": "Escudo digital criança"}
]
FIM_JSON

echo "✅ Arquivos gerados com sucesso!"
ls -lh mkt_agent_01.py .env roteiros.json
