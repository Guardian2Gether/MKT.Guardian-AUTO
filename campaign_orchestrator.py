import os
import json
from google import genai
from google.genai import types

class MarketingOrchestrator:
    def __init__(self):
        # Inicializa o cliente oficial da nova SDK do Gemini
        # Lembre-se de configurar a variável de ambiente antes de rodar:
        # No Windows (Prompt): set GEMINI_API_KEY=sua_chave_aqui
        # No Linux/Mac: export GEMINI_API_KEY="sua_chave_aqui"
        self.client = genai.Client()
        
        # Modelo recomendado para velocidade, custo e excelente suporte a JSON estruturado
        self.model_name = "gemini-2.5-flash"
        
        # Estado Global da Campanha (Memória Compartilhada)
        self.state = {
            "campaign_brief": {},
            "strategy_output": {},
            "creative_output": {},
            "media_factory_ready": False
        }

    def _load_agent_knowledge(self, filename: str) -> str:
        """
        Lê as diretrizes originais do arquivo Markdown para servir 
        como o Procedimento Operacional Padrão (SOP) do Agente.
        """
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        else:
            print(f"⚠️ Aviso: Arquivo de conhecimento '{filename}' não encontrado. Usando base genérica.")
            return "Você é um especialista em marketing digital de alta performance."

    def start_campaign_flow(self, user_prompt: str):
        """
        Ponto de entrada mestre. Recebe os trilhos do usuário e orquestra a execução.
        """
        print("🚀 [Orquestrador] Iniciando Fluxo Automatizado da Agência MKT Guardian...")
        self.state["campaign_brief"] = {"initial_prompt": user_prompt}
        
        # Passo 1: Executa o nó do Estrategista
        self._run_strategist_node()
        
        # Passo 2: Executa o nó do Criativo de Conteúdo
        self._run_creative_node()
        
        # Verificação e liberação para a Fábrica de Mídia
        if self.state["creative_output"]:
            self.state["media_factory_ready"] = True
            print("\n📢 [Orquestrador] Estado Atualizado com Sucesso!")
            print("💾 Todos os dados foram unificados na memória. Pronto para acionar a Fábrica de Mídia.")
            
        return self.state

    def _run_strategist_node(self):
        print("\n🧠 [Agente 1: Estrategista] Lendo SOP e analisando briefing da campanha...")
        
        # Carrega o conhecimento do arquivo original do seu repositório
        sop_estrategista = self._load_agent_knowledge("01_estrategista.md")
        
        system_instruction = (
            f"{sop_estrategista}\n\n"
            "Você deve analisar o briefing enviado pelo usuário e gerar um planejamento mestre de marketing. "
            "Sua resposta deve seguir OBRIGATORIAMENTE o formato JSON estruturado fornecido."
        )
        
        prompt_input = f"Briefing da Campanha fornecido pelo cliente:\n{self.state['campaign_brief']['initial_prompt']}"

        # Configura a API para exigir uma resposta estritamente estruturada em JSON
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3, # Baixa temperatura para respostas mais exatas e menos criativas/aleatórias
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
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_input,
                config=config
            )
            
            # Converte a string JSON retornada pelo Gemini em um dicionário Python e salva no Estado Global
            self.state["strategy_output"] = json.loads(response.text)
            print("✅ Estrategista concluiu e estruturou os dados com sucesso.")
            print(f"📊 ICP Definido: {self.state['strategy_output']['publico_alvo_icp']}")
            
        except Exception as e:
            print(f"❌ Erro na execução do nó Estrategista: {e}")
            raise e

    def _run_creative_node(self):
        print("\n✍️ [Agente 2: Criativo de Conteúdo] Lendo SOP e absorvendo o planejamento do Estrategista...")
        
        # Carrega o conhecimento do segundo arquivo original
        sop_criativo = self._load_agent_knowledge("02_criativo_conteudo.md")
        
        system_instruction = (
            f"{sop_criativo}\n\n"
            "Sua tarefa é criar a copy e o roteiro exato para a fábrica de mídia. "
            "Você não cria do nada: você DEVE se basear no planejamento estruturado do Estrategista. "
            "Sua resposta deve ser estritamente em formato JSON."
        )

        # O agente criativo consome o output do estrategista de dentro da memória global (self.state)
        estrategia_definida = self.state["strategy_output"]
        prompt_input = (
            f"Crie um roteiro de alta conversão baseado nestes dados estratégicos reais:\n"
            f"- Público Alvo: {estrategia_definida['publico_alvo_icp']}\n"
            f"- Posicionamento: {estrategia_definida['posicionamento_comunicacao']}\n"
            f"- Foco da Meta: {estrategia_definida['principais_metas']}"
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7, # Temperatura ligeiramente maior para dar liberdade criativa nas copies
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "gancho_atencao_inicial": {"type": "STRING", "description": "A frase de impacto dos primeiros 3 segundos para reter o público."},
                    "desenvolvimento_copy": {"type": "STRING", "description": "O corpo do anúncio explicando o problema e a solução."},
                    "chamada_para_acao_cta": {"type": "STRING", "description": "O comando final exato (ex: Clique em Saiba Mais para baixar)."}
                },
                "required": ["gancho_atencao_inicial", "desenvolvimento_copy", "chamada_para_acao_cta"]
            }
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_input,
                config=config
            )
            
            self.state["creative_output"] = json.loads(response.text)
            print("✅ Criativo de Conteúdo concluiu a roteirização automatizada.")
            print(f"📝 Gancho do Anúncio Criado: '{self.state['creative_output']['gancho_atencao_inicial']}'")
            
        except Exception as e:
            print(f"❌ Erro na execução do nó Criativo: {e}")
            raise e

if __name__ == "__main__":
    # Testando o ecossistema completo com um prompt de entrada mestre
    prompt_inicial = (
        "Lançar app de segurança digital contra fraudes financeiras com foco em blindar o WhatsApp de idosos. "
        "A meta é atingir tração inicial rápida explicando o perigo de forma simples."
    )
    
    orchestrator = MarketingOrchestrator()
    resultado_final = orchestrator.start_campaign_flow(prompt_inicial)
    
    # Imprime o resultado final consolidado gerado inteiramente pelas IAs em cadeia
    print("\n📦 [RESULTADO DO ESTADO FINAL DA CAMPANHA EM JSON]")
    print(json.dumps(resultado_final, indent=4, ensure_ascii=False))
