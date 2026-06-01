import os
import json
import requests
from google import genai
from google.genai import types

class MediaFactory:
    def __init__(self):
        # Inicializa o cliente do Gemini
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        
        # Carrega a API Key do ElevenLabs da variável de ambiente
        self.elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
        # ID de voz padrão (pode ser alterado para a voz clonada da sua agência)
        self.voice_id = "21m00Tcm4TlvDq8ikWAM" 

    def generate_campaign_assets(self, creative_data: dict):
        """
        Recebe a inteligência do Criativo e gera os arquivos físicos de áudio e imagem.
        """
        print("\n🏭 [Fábrica de Mídia] Iniciando produção automatizada de Assets...")
        
        # Cria a pasta de output se não existir para organizar os arquivos
        os.makedirs("output_campanha", exist_ok=True)
        
        # 1. Extrai os textos gerados pelo nó Criativo anterior
        texto_audio = f"{creative_data['gancho_atencao_inicial']}. {creative_data['desenvolvimento_copy']}"
        texto_cta = creative_data['chamada_para_acao_cta']
        
        print(f"🎙️ Texto enviado para locução: '{texto_audio[:50]}...'")
        
        # 2. Executa Geração do Áudio (ElevenLabs)
        audio_path = self._generate_audio(texto_audio)
        
        # 3. Executa Geração do Prompt de Imagem (Gemini lê o contexto e cria o prompt visual)
        print("🎨 Solicitando ao Gemini o conceito visual ideal para o anúncio...")
        image_prompt = self._create_image_prompt(texto_audio, texto_cta)
        
        # 4. Executa Geração da Imagem (Gemini 2.5 Imagen)
        image_path = self._generate_image(image_prompt)
        
        return {
            "audio_file": audio_path,
            "image_file": image_path,
            "applied_prompt": image_prompt
        }

    def _generate_audio(self, text: str) -> str:
        """Conecta com a API do ElevenLabs para gerar a locução em formato MP3."""
        if not self.elevenlabs_key:
            print("⚠️ ElevenLabs API Key não configurada. Pulando geração de áudio real (Modo Simulação).")
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
                file_path = "output_campanha/anuncio_audio.mp3"
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Locução gerada com sucesso e salva em: {file_path}")
                return file_path
            else:
                print(f"❌ Erro na API do ElevenLabs: {response.text}")
                return ""
        except Exception as e:
            print(f"❌ Falha ao conectar no ElevenLabs: {e}")
            return ""

    def _create_image_prompt(self, copy_text: str, cta_text: str) -> str:
        """Usa o Gemini para criar um prompt descritivo altamente detalhado para geração de imagem."""
        sop_designer = ""
        if os.path.exists("03_designer_visual.md"):
            with open("03_designer_visual.md", "r", encoding="utf-8") as f:
                sop_designer = f.read()

        instruction = (
            f"{sop_designer}\n\n"
            "Com base no SOP de Designer Visual acima e no texto do anúncio fornecido, "
            "escreva um prompt em INGLÊS altamente descritivo e focado em conversão para alimentar uma IA geradora de imagens (Imagen 3). "
            "Traga apenas o prompt final limpo, sem textos adicionais."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"{instruction}\n\nTexto do anúncio: {copy_text} - CTA: {cta_text}"
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Erro ao estruturar prompt de imagem: {e}")
            return "A professional smartphone cybersecurity app protection interface, high tech, modern."

    def _generate_image(self, prompt: str) -> str:
        """Gera a imagem comercial utilizando o motor Imagen do ecossistema Gemini SDK."""
        print(f"🖼️ Enviando prompt ao Imagen: '{prompt[:60]}...'")
        file_path = "output_campanha/anuncio_visual.jpg"
        
        try:
            # Chama o modelo de geração de imagens oficial da SDK atualizada do Gemini
            result = self.client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1" # Padrão Feed do Instagram/Facebook
                )
            )
            
            for generated_image in result.generated_images:
                with open(file_path, "wb") as f:
                    f.write(generated_image.image.image_bytes)
            
            print(f"✅ Arte do anúncio gerada com sucesso e salva em: {file_path}")
            return file_path
        except Exception as e:
            print(f"⚠️ Erro ao gerar imagem via API Imagen: {e}. Criando arquivo simulado.")
            # Fallback seguro para não travar a esteira de automação caso a cota da API falhe
            with open(file_path, "w") as f:
                f.write("Fábrica de Mídia - Imagem Simulada")
            return file_path
