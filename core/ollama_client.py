import requests
from .ai_engine import AIEngine


class OllamaClient(AIEngine):
    def __init__(self, host, model):
        self.host = host
        self.model = model

    def get_response(self, message, persona_desc):
        try:
            url = f"{self.host}/api/chat"
            messages = [
                {"role": "system", "content": persona_desc},
                {"role": "user", "content": message}
            ]

            data = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.7, "num_ctx": 2048}
            }

            response = requests.post(url, json=data, timeout=60)
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "抱歉，我现在遇到了一些问题，暂时无法回复。")
        except Exception as e:
            raise Exception(f"调用Ollama出错: {str(e)}")

    def test_connection(self):
        try:
            url = f"{self.host}/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            raise Exception(f"Ollama连接错误: {str(e)}")