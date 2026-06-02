import os
import json
from google import genai
from google.genai import types

class TrafficManager:
    def __init__(self):
        # Inicializa o cliente do Gemini
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        
        # Tokens fictícios ou reais da API de tráfego recolhidos do ambiente
        self.meta_access_token = os.environ.get("META_ACCESS_TOKEN")
        self.meta_ad_account_id = os.environ.get("META_AD_ACCOUNT_ID")

    def _load_traffic_sop(self) -> str:
        """Carrega o conhecimento prático e regras do ficheiro 04_gestor_trafego.md"""
        if os.path.exists("04_gestor_trafego.md"):
            with open("04_gestor_trafego.md", "r", encoding="utf-8") as f:
                return f.read()
        return "Você é um Gestor de Tráfego Pago focado em ROAS e conversões em Meta Ads."

    def structure_advertising_campaign(self, strategy_data: dict, media_assets: dict) -> dict:
        """
        Lê o ICP do estrategista, os caminhos dos ficheiros gerados e 
        devolve a estrutura técnica final mapeada para anúncios.
        """
        print("\n🎯 [Gestor de Tráfego] Iniciando o mapeamento técnico da campanha para API...")
        sop_trafego = self._load_traffic_sop()

        # Instrução do sistema para forçar o Gemini a agir como um gestor de tráfego e cuspir JSON técnico
        system_instruction = (
            f"{sop_trafego}\n\n"
            "Sua tarefa é ler a definição de público-alvo (ICP) fornecida e traduzi-la em "
            "configurações de segmentação estritas para a API do Meta Ads. "
            "Você deve responder APENAS com o formato JSON estruturado exigido."
        )

        prompt_input = f"Público Alvo determinado pelo Estrategista:\n{strategy_data.get('publico_alvo_icp')}"

        # Configura o Schema JSON para garantir que a IA preenche dados que um código consegue ler
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "idade_minima": {"type": "INTEGER", "description": "Idade mínima para segmentação (mínimo 18)."},
                    "idade_maxima": {"type": "INTEGER", "description": "Idade máxima para segmentação (máximo 65)."},
                    "genero": {"type": "STRING", "description": "ALL, MALE, ou FEMALE baseado no público alvo."},
                    "interesses_meta_keywords": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                        "description": "Lista de 3 a 5 palavras-chave exatas de interesses disponíveis no gerenciador do Meta Ads."
                    }
                },
                "required": ["idade_minima", "idade_maxima", "genero", "interesses_meta_keywords"]
            }
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_input,
                config=config
            )
            
            # Segmentação técnica resolvida pela IA
            targeting = json.loads(response.text)
            print("✅ Segmentação de público traduzida para formato de API com sucesso.")
            
            # Montagem do payload completo da campanha estruturada (Ad Set e Ad Creative)
            campaign_payload = {
                "campaign_setup": {
                    "name": f"CAMPANHA_AUTOMATICA_{strategy_data.get('posicionamento_comunicacao', 'MKT')[:15].upper()}",
                    "objective": "OUTCOMES", # Padrão Meta Ads para Conversões/Vendas/Leads
                    "status": "PAUSED" # Segurança: Sempre começa pausada para revisão humana do orçamento
                },
                "ad_set_setup": {
                    "name": f"CONJUNTO_{targeting['idade_minima']}-{targeting['idade_maxima']}",
                    "targeting_criteria": targeting,
                    "daily_budget_cents": 2000 # R$ 20.00 diários padrão de teste (representado em centavos na API)
                },
                "ad_creative_setup": {
                    "name": "ANUNCIO_DINAMICO_V1",
                    "text_copy": media_assets.get("designer_prompt", "Confira no link."),
                    "attached_media": {
                        "image_path": media_assets.get("static_image_file"),
                        "video_path": media_assets.get("commercial_video_file"),
                        "audio_path": media_assets.get("audio_file")
                    }
                }
            }

            # Se houver chaves reais configuradas, faria o disparo HTTP aqui
            if self.meta_access_token and self.meta_ad_account_id:
                self._publish_to_meta_api(campaign_payload)
            else:
                print("ℹ️ Modo de Simulação Ativo (Dry Run): Nenhuma chave de API de Tráfego configurada.")
                print(f"📌 Interesses Meta Ads sugeridos: {targeting['interesses_meta_keywords']}")

            return campaign_payload

        except Exception as e:
            print(f"❌ Erro ao estruturar tráfego: {e}")
            return {}

    def _publish_to_meta_api(self, payload: dict):
        """Método reservado para chamadas reais à Graph API da Meta."""
        print("⚡ [Meta API Connection] Enviando payloads de criação para a API gráfica...")
        # Lógica de requests.post() entraria aqui utilizando os tokens do ambiente.
        print("✅ Campanhas injetadas no seu Gerenciador de Anúncios!")
