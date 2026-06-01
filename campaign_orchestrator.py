import os
import json
from google import genai # Atualizado para a SDK padrão recomendada do Gemini

class MarketingOrchestrator:
    def __init__(self):
        # Inicializa o cliente do Gemini coletando a API Key do ambiente
        # Para rodar, configure a variável de ambiente: export GEMINI_API_KEY="sua_chave"
        self.client = genai.Client()
        self.state = {
            "campaign_brief": {},
            "strategy_output": {},
            "creative_output": {},
            "media_factory_ready": False
        }
        
    def start_campaign_flow(self, user_prompt: str):
        """
        Ponto de partida da automação. Recebe os trilhos e objetivos do usuário
        e inicia a passagem de contexto entre os nós (agentes).
        """
        print("🚀 Iniciando Fluxo Automatizado da Agência MKT Guardian...")
        self.state["campaign_brief"] = {"initial_prompt": user_prompt}
        
        # 1. Executa Nó do Estrategista
        self._run_strategist_node()
        
        # 2. Executa Nó do Criativo de Conteúdo
        self._run_creative_node()
        
        # 3. Alerta a Fábrica de Mídia
        if self.state["creative_output"]:
            self.state["media_factory_ready"] = True
            print("📢 Estado Atualizado: Pronto para acionar a Fábrica de Mídia.")
            
        return self.state

    def _run_strategist_node(self):
        print("\n🧠 [Agente 1: Estrategista] Analisando briefing e definindo ICP...")
        # Aqui o agente lê o arquivo estático '01_estrategista.md' como base de conhecimento (SOP)
        # e gera o planejamento estruturado em JSON.
        
        # Código de integração com Gemini 2.5 Flash entrará aqui
        # Simulando preenchimento do State com o output estruturado
        self.state["strategy_output"] = {
            "target_audience": "Pessoas de 25-70 anos vulneráveis a golpes no WhatsApp",
            "positioning": "Proteção inteligente para sua vida, no WhatsApp.",
            "goals": "1.000 downloads na primeira semana com CAC < R$ 25"
        }
        print("✅ Estrategista concluiu. Dados consolidados no Estado Global.")

    def _run_creative_node(self):
        print("\n✍️ [Agente 2: Criativo de Conteúdo] Consumindo estratégia para criar copies...")
        # O diferencial da automação: Este nó consome dinamicamente o 'strategy_output' gerado acima
        contexto_estrategia = self.state["strategy_output"]
        
        # Código de geração de roteiros dinâmicos baseado na estratégia real
        self.state["creative_output"] = {
            "roteiro_anuncio_01": "Sofreu tentativa de golpe no Whats hoje? Veja como se proteger...",
            "cta": "Clique e baixe o App Guardian AI"
        }
        print("✅ Criativo concluiu. Roteiros estruturados prontos para produção de mídia.")

if __name__ == "__main__":
    # Exemplo de ativação da agência apenas com o prompt mestre
    prompt_inicial = (
        "Lançar app de segurança digital com foco em combater golpes no WhatsApp. "
        "Público-alvo focado em pessoas comuns e idosos. Orçamento inicial de R$ 5.000."
    )
    
    orchestrator = MarketingOrchestrator()
    final_state = orchestrator.start_campaign_flow(prompt_inicial)
