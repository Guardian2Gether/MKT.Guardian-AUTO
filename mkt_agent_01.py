import os
import time
import requests
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont

class MediaFactory:
    def __init__(self):
        # Clientes de API integrados na nova SDK do Gemini e ambiente local
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        
        # Tokens e chaves coletados com segurança das variáveis de ambiente
        self.elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
        self.runway_key = os.environ.get("RUNWAY_API_KEY")
        
        # Configuração padrão de locução (ElevenLabs)
        self.voice_id = "21m00Tcm4TlvDq8ikWAM" # ID de voz genérico de alta qualidade
        
    def generate_campaign_assets(self, creative_data: dict) -> dict:
        """
        Executa sequencialmente o novo stack: ElevenLabs -> Gemini Imagen -> Pillow Design -> Runway Video
        """
        print("\n🏭 [Fábrica de Mídia v2] Iniciando motores com o novo Stack...")
        os.makedirs("output_campanha", exist_ok=True)
        
        # Extração de textos do Estado Global fornecido pelo Criativo
        texto_audio = f"{creative_data['gancho_atencao_inicial']}. {creative_data['desenvolvimento_copy']}"
        texto_cta = creative_data['chamada_para_acao_cta']
        
        # 1. Geração do Áudio Profissional (ElevenLabs)
        audio_path = self._generate_audio(texto_audio)
        
        # 2. Geração da Imagem Base (Gemini Imagen)
        print("🎨 [Designer AI] Gerando o conceito visual principal com o Gemini...")
        image_prompt = self._create_image_prompt(texto_audio, texto_cta)
        base_image_path = "output_campanha/anuncio_base.jpg"
        self._generate_gemini_image(image_prompt, base_image_path)
        
        # 3. Tratamento e Injeção de Design Comercial (Pillow/PIL)
        print("📐 [Pillow Engine] Formatando arte final e aplicando tipografia de CTA...")
        final_design_path = "output_campanha/anuncio_final_design.jpg"
        self._apply_pillow_overlay(base_image_path, final_design_path, texto_cta)
        
        # 4. Animação de Mídia e Produção de Vídeo (Runway API)
        print("🎬 [Runway Engine] Iniciando renderização de vídeo dinâmico para Reels/Stories...")
        video_path = self._generate_runway_video(image_prompt, final_design_path)
        
        return {
            "audio_file": audio_path,
            "static_image_file": final_design_path,
            "commercial_video_file": video_path,
            "designer_prompt": image_prompt
        }

    def _generate_audio(self, text: str) -> str:
        """Envia o roteiro do criativo para narração humana artificial via ElevenLabs."""
        if not self.elevenlabs_key:
            print("⚠️ ElevenLabs Key não detectada. Pulando para Modo Simulação.")
            return "output_campanha/anuncio_audio_mock.mp3"
            
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_key
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                path = "output_campanha/anuncio_audio.mp3"
                with open(path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Locução gravada: {path}")
                return path
        except Exception as e:
            print(f"❌ Falha no ElevenLabs: {e}")
        return ""

    def _create_image_prompt(self, copy_text: str, cta_text: str) -> str:
        """Usa as diretrizes do arquivo 03_designer_visual.md para criar o prompt ideal de imagem."""
        sop_designer = ""
        if os.path.exists("03_designer_visual.md"):
            with open("03_designer_visual.md", "r", encoding="utf-8") as f:
                sop_designer = f.read()
                
        instruction = (
            f"{sop_designer}\n\n"
            "Escreva um prompt em INGLÊS cinematográfico, altamente realista e comercial "
            "para o motor Imagen 3 criar o fundo perfeito para este anúncio. Sem textos adicionais na resposta."
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"{instruction}\n\nTexto: {copy_text} | CTA: {cta_text}"
            )
            return response.text.strip()
        except:
            return "A professional smartphone cybersecurity protection interface, high-tech, 8k resolution."

    def _generate_gemini_image(self, prompt: str, output_path: str):
        """Dispara a geração de imagens pelo motor Imagen nativo da nova SDK do Gemini."""
        try:
            result = self.client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1" # Quadrado ideal para Feed Meta Ads
                )
            )
            for generated_image in result.generated_images:
                with open(output_path, "wb") as f:
                    f.write(generated_image.image.image_bytes)
            print(f"✅ Imagem base gerada pelo Gemini: {output_path}")
        except Exception as e:
            print(f"❌ Erro ao gerar imagem no Gemini Imagen: {e}")
            # Fallback cria um arquivo temporário vazio para não parar o fluxo
            Image.new('RGB', (800, 800), color=(20, 24, 33)).save(output_path)

    def _apply_pillow_overlay(self, input_path: str, output_path: str, text: str):
        """Abre a imagem gerada pela IA e desenha o layout comercial com texto por cima (Substituindo o Canva)."""
        try:
            img = Image.open(input_path).convert("RGBA")
            txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            
            w, h = img.size
            # Desenha uma barra retangular escura semi-transparente na base da imagem para dar contraste comercial
            barra_altura = int(h * 0.15)
            draw.rectangle([(0, h - barra_altura), (w, h)], fill=(0, 0, 0, 180)) # Opacidade de 180 (0-255)
            
            # Carrega uma fonte do sistema padrão ou tenta uma genérica
            try:
                font = ImageFont.truetype("arial.ttf", int(barra_altura * 0.4))
            except:
                font = ImageFont.load_default()
                
            # Centraliza o texto da CTA dentro da barra
            text_size = draw.textbbox((0, 0), text, font=font)
            text_w = text_size[2] - text_size[0]
            text_h = text_size[3] - text_size[1]
            
            x_pos = (w - text_w) // 2
            y_pos = (h - barra_altura) + (barra_altura - text_h) // 2
            
            # Escreve o texto com uma cor chamativa (Ex: Amarelo/Dourado ou Branco)
            draw.text((x_pos, y_pos), text, fill=(255, 215, 0, 255), font=font)
            
            # Junta as camadas e salva em JPEG de alta qualidade
            final_img = Image.alpha_composite(img, txt_layer).convert("RGB")
            final_img.save(output_path, "JPEG", quality=95)
            print(f"✅ Design comercial consolidado localmente via Pillow: {output_path}")
        except Exception as e:
            print(f"❌ Erro ao processar design no Pillow: {e}")
            if os.path.exists(input_path):
                os.replace(input_path, output_path)

    def _generate_runway_video(self, image_prompt: str, image_path: str) -> str:
        """Conecta com a API de geração de vídeo da Runway (Gen-3 Alpha) para criar o anúncio animado."""
        if not self.runway_key:
            print("⚠️ Runway API Key não encontrada. Vídeo em modo de simulação.")
            return "output_campanha/anuncio_video_mock.mp4"
            
        url = "https://api.v1.runwayml.com/v1/image_to_video" # Endpoint padrão da API Runway
        headers = {
            "Authorization": f"Bearer {self.runway_key}",
            "Content-Type": "application/json"
        }
        
        # Em produção, a imagem gerada no Pillow precisaria estar hospedada num link público S3/Imgur, 
        # para este escopo passamos o prompt refinado combinando texto e movimento descritivo para a IA animar.
        data = {
            "prompt": f"Commercial motion graphic overlay, smooth transitions, panning camera effect. Based on scene: {image_prompt}",
            "model": "gen3_alpha",
            "duration": 4 # 4 segundos padrão de anúncio animado
        }
        
        try:
            # Envia a tarefa de renderização para os servidores da Runway
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 202:
                task_id = response.json().get("id")
                print(f"⏳ Renderização iniciada na Runway (ID: {task_id}). Aguardando processamento...")
                
                # Sistema de checagem em loop (Pooling) para aguardar o download ficar pronto
                for _ in range(12): # Tenta checar por até 2 minutos
                    time.sleep(10)
                    status_url = f"https://api.v1.runwayml.com/v1/tasks/{task_id}"
                    status_resp = requests.get(status_url, headers=headers).json()
                    
                    if status_resp.get("status") == "SUCCEEDED":
                        video_url = status_resp.get("output")[0]
                        video_data = requests.get(video_url).content
                        video_path = "output_campanha/anuncio_video_comercial.mp4"
                        with open(video_path, "wb") as f:
                            f.write(video_data)
                        print(f"✅ Anúncio em vídeo baixado com sucesso da Runway: {video_path}")
                        return video_path
                        
            print(f"❌ Runway retornou código inesperado: {response.status_code}")
        except Exception as e:
            print(f"❌ Falha de integração com a API da Runway: {e}")
            
        return "output_campanha/anuncio_video_mock.mp4"
