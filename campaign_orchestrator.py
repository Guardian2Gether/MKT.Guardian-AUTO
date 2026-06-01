import os
import json
from google import genai
from google.genai import types

# Importa de forma dinâmica a nossa fábrica de mídia refatorada
from mkt_agent_01 import MediaFactory

class MarketingOrchestrator:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        
        self.state = {
            "campaign_brief": {},
            "strategy_output": {},
            "creative_output": {},
            "media_factory_ready": False,
            "generated_assets": {}
        }

    def _load_agent_knowledge(self, filename: str) -> str:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        return "Você é um especialista em marketing digital de alta performance."

    def start_campaign_flow(self, user_prompt: str):
        print("🚀 [Orquestrador] Iniciando Fluxo Automatizado da Agência MKT Guardian...")
        self.state["campaign_brief"] = {"initial_prompt": user_prompt}
        
        # 1. Executa Inteligência de Mercado
        self._run_strategist_node()
        
        # 2. Executa Copywriting e Roteirização
        self._run_creative_node()
        
        # 3. Dispara de forma assíncrona/direta a Fábrica de Mídia
        if self.state["creative_output"]:
            self.state["media_factory_ready"] = True
            print("\n📢 [Orquestrador] Enviando dados para a Esteira de Produção de Mídia...")
            
            # Instancia a fábrica e processa as mídias usando os dados gerados em tempo real
            factory = MediaFactory()
            assets = factory.generate_campaign_assets(self.state["creative_output"])
            
            self.state["generated_assets"] = assets
            print("\n✅ [Orquestrador] Fluxo Completo Finalizado com Sucesso!")
            
        return self.state

    def _run_strategist_node(self):
        print("\n🧠 [Agente 1: Estrategista] Lendo SOP e analisando briefing da campanha...")
        sop_estrategista = self._load_agent_knowledge("01_estrategista.md")
        
        system_instruction = (
            f"{sop_estrategista}\n\n"
            "Você deve analisar o briefing enviado pelo usuário e gerar um planejamento mestre de marketing. "
            "Sua resposta deve seguir OBRIGATORIAMENTE o formato JSON estruturado fornecido."
        )
        
        prompt_input = f"Briefing da Campanha fornecido pelo cliente:\n{self.state['campaign_brief']['initial_prompt']}"

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "publico_alvo_icp": {"type": "STRING", "description": "Definição detalhada do Cliente Ideal (ICP)."},
                    "posicionamento_comunicacao": {"type": "STRING", "description": "Gancho principal e tom da comunicação."},
                    "principais_metas": {"type": "STRING", "description": "Metas SMART para os primeiros 30 a 90 dias."}
                },
                "required": ["publico_alvo_icp", "posicionamento_comunicacao", "principais_metas"]
            }
        )

        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt_input, config=config)
            self.state["strategy_output"] = json.loads(response.text)
            print("✅ Estrategista concluiu e estruturou os dados com sucesso.")
        except Exception as e:
            print(f"❌ Erro no Estrategista: {e}")
            raise e

    def _run_creative_node(self):
        print("\n✍️ [Agente 2: Criativo de Conteúdo] Lendo SOP e absorvendo o planejamento...")
        sop_criativo = self._load_agent_knowledge("02_criativo_conteudo.md")
        
        system_instruction = (
            f"{sop_criativo}\n\n"
            "Sua tarefa é criar a copy e o roteiro exato para a fábrica de mídia baseado no planejamento do Estrategista. "
            "Sua resposta deve ser estritamente em formato JSON."
        )

        estrategia_definida = self.state["strategy_output"]
        prompt_input = (
            f"Crie um roteiro de alta conversão baseado nestes dados estratégicos reais:\n"
            f"- Público Alvo: {estrategia_definida['publico_alvo_icp']}\n"
            f"- Posicionamento: {estrategia_definida['posicionamento_comunicacao']}\n"
            f"- Foco da Meta: {estrategia_definida['principais_metas']}"
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "gancho_atencao_inicial": {"type": "STRING", "description": "Frase de impacto inicial para reter o público."},
                    "desenvolvimento_copy": {"type": "STRING", "description": "Corpo do anúncio explicando o problema e a solução."},
                    "chamada_para_acao_cta": {"type": "STRING", "description": "O comando final exato."}
                },
                "required": ["gancho_atencao_inicial", "desenvolvimento_copy", "chamada_para_acao_cta"]
            }
        )

        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt_input, config=config)
            self.state["creative_output"] = json.loads(response.text)
            print("✅ Criativo de Conteúdo concluiu a roteirização automatizada.")
        except Exception as e:
            print(f"❌ Erro no Criativo: {e}")
            raise e

if __name__ == "__main__":
    prompt_inicial = (
        "Lançar app de segurança digital contra fraudes financeiras com foco em blindar o WhatsApp de idosos. "
        "A meta é atingir tração inicial rápida explicando o perigo de forma simples."
    )
    
    orchestrator = MarketingOrchestrator()
    resultado_final = orchestrator.start_campaign_flow(prompt_inicial)
    
    print("\n📦 [ESTADO FINAL CONSOLIDADO (PRONTO PARA COMPRAR TRAFEGO)]")
    print(json.dumps(resultado_final, indent=4, ensure_ascii=False))
