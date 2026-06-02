import os
import json
from google import genai
from google.genai import types

class DataAnalyst:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"
        # Definição estrita da meta do projeto MKT.Guardian-AI
        self.META_CAC_MAXIMO = 25.00 

    def _load_analyst_sop(self) -> str:
        if os.path.exists("05_analista_dados.md"):
            with open("05_analista_dados.md", "r", encoding="utf-8") as f:
                return f.read()
        return "Você é um Analista de Dados Sênior de Marketing Digital focado em ROI e otimização de funil."

    def analyze_campaign_performance(self, campaign_id: str, real_api_data: dict = None) -> dict:
        """
        Analisa os dados de performance de funil (reais ou simulados)
        e aplica a matriz de decisão inteligente para comandar o Orquestrador.
        """
        print(f"\n📊 [Analista de Dados v2] Executando auditoria algorítmica na campanha {campaign_id}...")
        sop = self._load_analyst_sop()

        # Se não passarmos dados da API real ainda, usamos o cenário de simulação de gargalo
        metrics = real_api_data if real_api_data else {
            "valor_gasto": 500.00,
            "impressoes": 40000,
            "cliques": 320,
            "ctr_porcentagem": 0.8,      # Gargalo simulado aqui: Cliques muito baixos para 40 mil impressões
            "conversoes_downloads": 10,
            "cac_atual": 50.00           # R$ 500 / 10 downloads = R$ 50,00 (Meta é 25)
        }

        # Construímos as diretrizes de contexto para o Gemini cruzar com as regras de negócio
        contexto_regras = (
            f"{sop}\n\n"
            f"DIRETRIZES DE METRICAS DA AGÊNCIA:\n"
            f"- A meta absoluta de CAC para o App de Segurança é menor que R$ {self.META_CAC_MAXIMO}.\n"
            f"- CTR Ideal de mercado para anúncios de interrupção em redes sociais deve ser >= 1.5%.\n\n"
            f"MATRIZ DE DECISÃO EXIGIDA:\n"
            f"1. Se CAC > {self.META_CAC_MAXIMO} E CTR < 1.5% -> Ação: 'REFAZER_CRIATIVOS'\n"
            f"2. Se CAC > {self.META_CAC_MAXIMO} E CTR >= 1.5% -> Ação: 'REFAZER_SEGMENTACAO'\n"
            f"3. Se CAC <= {self.META_CAC_MAXIMO} -> Ação: 'ESCALAR_ORCAMENTO'\n\n"
            f"Gere um diagnóstico de negócios e determine o próximo comando lógico estritamente no formato JSON fornecido."
        )

        config = types.GenerateContentConfig(
            system_instruction=contexto_regras,
            temperature=0.1, # Minimizamos a criatividade para focar puramente em lógica de dados
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "diagnostico_funil": {"type": "STRING", "description": "Análise detalhada sobre onde o dinheiro está sendo perdido."},
                    "status_campanha": {"type": "STRING", "description": "SAUDAVEL, ATENCAO ou CRITICO."},
                    "acao_corretiva_obrigatoria": {"type": "STRING", "description": "Deve ser estritamente: REFAZER_CRIATIVOS, REFAZER_SEGMENTACAO ou ESCALAR_ORCAMENTO."},
                    "sugestao_ajuste_prompt": {"type": "STRING", "description": "Instrução textual direcionada para o próximo agente corrigir o problema."}
                },
                "required": ["diagnostico_funil", "status_campanha", "acao_corretiva_obrigatoria", "sugestao_ajuste_prompt"]
            }
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Dados atuais de performance do anúncio:\n{json.dumps(metrics)}",
                config=config
            )
            
            analysis = json.loads(response.text)
            print(f"✅ Análise concluída com sucesso.")
            print(f"📈 Status Diagnosticado: {analysis['status_campanha']}")
            print(f"🤖 Comando emitido para a Esteira: {analysis['acao_corretiva_obrigatoria']}")
            print(f"💡 Orientação técnica: {analysis['sugestao_ajuste_prompt']}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Falha crítica no processamento do modelo de dados: {e}")
            return {
                "diagnostico_funil": "Erro na leitura de dados.",
                "status_campanha": "ATENCAO",
                "acao_corretiva_obrigatoria": "MANTER",
                "sugestao_ajuste_prompt": "Revisar logs do sistema."
            }

if __name__ == "__main__":
    # Teste rápido simulando uma campanha que está performando super bem (CAC de R$ 20,00)
    teste_sucesso = {
        "valor_gasto": 200.00,
        "impressoes": 10000,
        "cliques": 250,
        "ctr_porcentagem": 2.5,
        "conversoes_downloads": 10,
        "cac_atual": 20.00
    }
    
    analyst = DataAnalyst()
    analyst.analyze_campaign_performance("CAMP_TESTE_SUCESSO", teste_sucesso)
