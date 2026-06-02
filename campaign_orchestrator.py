import os
import json
from google import genai
from google.genai import types

# Importação de toda a cadeia de agentes refatorados
from mkt_agent_01 import MediaFactory
from traffic_manager import TrafficManager
from data_analyst import DataAnalyst
from community_manager import CommunityManager

class MarketingOrchestrator:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        
        self.state = {
            "campaign_brief": {},
            "strategy_output": {},
            "creative_output": {},
            "media_factory_ready": False,
            "generated_assets": {},
            "traffic_setup": {},
            "optimization_alert": {},
            "simulated_chat_reply": ""
        }

    def _load_agent_knowledge(self, filename: str) -> str:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        return "Especialista em marketing."

    def start_campaign_flow(self, user_prompt: str):
        print("🚀 [Orquestrador] Iniciando Ecossistema Multi-Agente MKT Guardian AI...")
        self.state["campaign_brief"] = {"initial_prompt": user_prompt}
        
        # 1. Agente Estrategista (01_estrategista.md)
        self._run_strategist_node()
        
        # 2. Agente Criativo (02_criativo_conteudo.md)
        self._run_creative_node()
        
        # 3. Fábrica de Mídia (Gemini Imagen + ElevenLabs + Pillow + Runway)
        if self.state["creative_output"]:
            self.state["media_factory_ready"] = True
            factory = MediaFactory()
            self.state["generated_assets"] = factory.generate_campaign_assets(self.state["creative_output"])
            
            # 4. Agente Gestor de Tráfego (04_gestor_trafego.md)
            traffic = TrafficManager()
            self.state["traffic_setup"] = traffic.structure_advertising_campaign(
                self.state["strategy_output"], 
                self.state["generated_assets"]
            )
            
            # 5. Agente Analista de Dados - Fechamento de Loop (05_analista_dados.md)
            analyst = DataAnalyst()
            self.state["optimization_alert"] = analyst.analyze_campaign_performance(
                campaign_id="CAMP_01_CYBER"
            )
            
            # 6. Agente Community Manager - Atendimento de Ponta (06_community_manager.md)
            manager = CommunityManager()
            self.state["simulated_chat_reply"] = manager.process_incoming_message(
                lead_name="Dona Maria", 
                message_text="Esse aplicativo realmente impede clonarem meu zap? Tenho medo de golpe."
            )
            
            print("\n🏁 [Orquestrador] Ciclo operacional de 360 graus concluído.")
            
        return self.state

    def _run_strategist_node(self):
        print("\n🧠 [Agente 1: Estrategista] Mapeando mercado e objetivos...")
        sop = self._load_agent_knowledge("01_estrategista.md")
        config = types.GenerateContentConfig(
            system_instruction=f"{sop}\nResponda em JSON.",
            temperature=0.3,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "publico_alvo_icp": {"type": "STRING"},
                    "posicionamento_comunicacao": {"type": "STRING"},
                    "principais_metas": {"type": "STRING"}
                },
                "required": ["publico_alvo_icp", "posicionamento_comunicacao", "principais_metas"]
            }
        )
        response = self.client.models.generate_content(model=self.model_name, contents=self.state["campaign_brief"]["initial_prompt"], config=config)
        self.state["strategy_output"] = json.loads(response.text)

    def _run_creative_node(self):
        print("\n✍️ [Agente 2: Criativo de Conteúdo] Estruturando roteiro e copies...")
        sop = self._load_agent_knowledge("02_criativo_conteudo.md")
        config = types.GenerateContentConfig(
            system_instruction=f"{sop}\nResponda em JSON.",
            temperature=0.7,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "gancho_atencao_inicial": {"type": "STRING"},
                    "desenvolvimento_copy": {"type": "STRING"},
                    "chamada_para_acao_cta": {"type": "STRING"}
                },
                "required": ["gancho_atencao_inicial", "desenvolvimento_copy", "chamada_para_acao_cta"]
            }
        )
        prompt_input = f"Estratégia anterior:\n{json.dumps(self.state['strategy_output'])}"
        response = self.client.models.generate_content(model=self.model_name, contents=prompt_input, config=config)
        self.state["creative_output"] = json.loads(response.text)

if __name__ == "__main__":
    prompt_mestre = (
        "Lançar app de segurança digital contra fraudes financeiras com foco em blindar o WhatsApp de idosos. "
        "A meta é atingir tração inicial rápida explicando o perigo de forma simples."
    )
    
    orchestrator = MarketingOrchestrator()
    agencia_viva = orchestrator.start_campaign_flow(prompt_mestre)
    
    print("\n📦 [ESTADO COMPLETO DA AGÊNCIA INTEGRADA EM MEMÓRIA]")
    print(json.dumps(agencia_viva, indent=4, ensure_ascii=False))
