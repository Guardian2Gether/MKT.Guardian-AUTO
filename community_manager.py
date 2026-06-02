import os
from google import genai

class CommunityManager:
    def __init__(self):
        self.client = genai.Client()
        self.model_name = "gemini-2.5-flash"

    def _load_community_sop(self) -> str:
        if os.path.exists("06_community_manager.md"):
            with open("06_community_manager.md", "r", encoding="utf-8") as f:
                return f.read()
        return "Você é um Community Manager responsável pelo atendimento rápido e conversão de leads."

    def process_incoming_message(self, lead_name: str, message_text: str) -> str:
        """
        Simula a recepção de uma mensagem via API do WhatsApp e gera
        a resposta comercial usando o tom de voz corporativo.
        """
        print(f"\n💬 [Community Manager] Novo lead '{lead_name}' enviou uma mensagem.")
        sop = self._load_community_sop()

        prompt = (
            f"Aja conforme suas diretrizes operacionais:\n{sop}\n\n"
            f"O lead {lead_name} diz: '{message_text}'\n"
            "Gere uma resposta curta, profissional, empática e focada em fechar a venda do aplicativo de segurança."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"❌ Erro no processamento do chat: {e}")
            return "Olá! Como posso te ajudar com a segurança do seu WhatsApp hoje?"
