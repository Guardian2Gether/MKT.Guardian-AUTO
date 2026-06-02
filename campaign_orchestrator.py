import os
import json
from google import genai
from google.genai import types

# Importa os módulos dinâmicos da nossa agência
from mkt_agent_01 import MediaFactory
from traffic_manager import TrafficManager

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
            "traffic_setup": {} # Espaço na memória para o Gestor de Tráfego
        }

    def _load_agent_knowledge(self, filename: str) -> str:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        return "Você é um especialista em marketing digital de alta performance."

    def start_campaign_flow(self, user_prompt: str):
        print("🚀 [Orquestrador] Iniciando Fluxo Automatizado da Agência MKT Guardian...")
        self.state["campaign_brief"] = {"initial_prompt": user_prompt}
        
        # 1. Executa Inteligência de Mercado (Estrategista)
        self._run_strategist_node()
        
        # 2. Executa Copywriting e Roteirização (Criativo)
        self._run_creative_node()
        
        # 3. Dispara a Produção Visual/Áudio (Fábrica de Mídia)
        if self.state["creative_output"]:
            self.state["media_factory_ready"] = True
            factory = MediaFactory()
            assets = factory.generate_campaign_assets(self.state["creative_output"])
            self.state["generated_assets"] = assets
            
            # 4. DISPARO SPRINT 3: Executa Mapeamento e Publicação (Gestor de Tráfego)
            traffic = TrafficManager()
            setup_final = traffic.structure_advertising_campaign(
                self.state["strategy_output"], 
                self.state["generated_assets"]
            )
            self.state["traffic_setup"] = setup_final
            
            print("\n🏁 [Orquestrador] Todos os agentes concluíram suas respectivas tarefas com sucesso!")
            
        return self.state

    def _run_strategist_node(self):
        print("\n🧠 [Agente 1: Estrategista] Lendo SOP e analisando briefing da campanha...")
        sop_estrategista = self._load_agent_knowledge("01_estrategista.md")
        system_instruction = f"{sop_estrategista}\n\nAnalise o briefing e gere um planejamento em JSON."
        prompt_input = f"Briefing:\n{self.state['campaign_brief']['initial_prompt']}"

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
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
        response = self.client.models.generate_content(model=self.model_name, contents=prompt_input, config=config)
        self.state["strategy_output"] = json.loads(response.text)
        print("✅ Estrategista concluiu.")

    def _run_creative_node(self):
        print("\n✍️ [Agente 2: Criativo de Conteúdo] Lendo SOP e absorvendo o planejamento...")
        sop_criativo = self._load_agent_knowledge("02_criativo_conteudo.md")
        system_instruction = f"{sop_criativo}\n\nCrie copies baseadas na estratégia. Responda em JSON."
        estrategia_definida = self.state["strategy_output"]
        prompt_input = f"Estratégia:\n- Público: {estrategia_definida['publico_alvo_icp']}\n- Foco: {estrategia_definida['principais_metas']}"

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
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
        response = self.client.models.generate_content(model=self.model_name, contents=prompt_input, config=config)
        self.state["creative_output"] = json.loads(response.text)
        print("✅ Criativo de Conteúdo concluiu.")

if __name__ == "__main__":
    prompt_inicial = (
        "Lançar app de segurança digital focado em combater fraudes no WhatsApp. "
        "Alvo principal: Idosos e cidadãos comuns."
    )
    orchestrator = MarketingOrchestrator()
    resultado = orchestrator.start_campaign_flow(prompt_inicial)
    
    print("\n📦 [ESTADO TOTAL DA AGÊNCIA MULTI-AGENTE (PRONTO PARA VEICULAR)]")
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
