import os
import json
from google import genai
from google.genai import types

class DataAnalyst:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"

    def _load_analyst_sop(self) -> str:
        if os.path.exists("05_analista_dados.md"):
            with open("05_analista_dados.md", "r", encoding="utf-8") as f:
                return f.read()
        return "Você é um Analista de Dados de Performance de Marketing Digital focado em ROI."

    def analyze_campaign_performance(self, campaign_id: str) -> dict:
        """
        Simula a coleta de métricas de tráfego reais e usa a IA para julgar
        se a campanha precisa de ajustes no criativo ou no público.
        """
        print(f"\n📊 [Analista de Dados] Puxando relatórios para a campanha {campaign_id}...")
        sop = self._load_analyst_sop()

        # Dados simulados simulando o comportamento de uma campanha real com problemas no criativo (CTR baixo)
        mock_performance_data = {
            "valor_gasto": 250.00,
            "impressoes": 15000,
            "cliques": 120,
            "ctr_porcentagem": 0.8, # CTR abaixo de 1% geralmente indica problemas no criativo/gancho
            "conversoes_downloads": 4,
            "cac_atual": 62.50 # Meta original do projeto é CAC < R$ 25
        }

        system_instruction = (
            f"{sop}\n\n"
            "Analise as métricas de performance enviadas comparando com a meta padrão de mercado. "
            "Determine se a campanha está saudável ou se precisa de otimização de criativos. "
            "Responda estritamente no formato JSON fornecido."
        )

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "status_diagnostico": {"type": "STRING", "description": "OTIMO, ALERTA ou CRITICO."},
                    "motivo_principal": {"type": "STRING", "description": "Explicação técnica do problema encontrado."},
                    "acao_corretiva_obrigatoria": {"type": "STRING", "description": "Comando claro para o próximo ciclo (ex: REFAZER_CRIATIVOS)."}
                },
                "required": ["status_diagnostico", "motivo_principal", "acao_corretiva_obrigatoria"]
            }
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Métricas reais do anúncio:\n{json.dumps(mock_performance_data)}",
                config=config
            )
            analysis_result = json.loads(response.text)
            print(f"✅ Diagnóstico Concluído. Status: {analysis_result['status_diagnostico']}")
            print(f"📢 Ação recomendada: {analysis_result['acao_corretiva_obrigatoria']}")
            return analysis_result
        except Exception as e:
            print(f"❌ Erro na análise de dados: {e}")
            return {"status_diagnostico": "ALERTA", "acao_corretiva_obrigatoria": "MANTER"}
