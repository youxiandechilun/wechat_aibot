import openai
from .ai_engine import AIEngine


class DeepSeekClient(AIEngine):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_response(self, message, persona_desc):
        try:
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )

            messages = [
                {"role": "system", "content": persona_desc},
                {"role": "user", "content": message}
            ]

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"调用DeepSeek出错: {str(e)}")

    def test_connection(self):
        try:
            client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "测试连接"}],
                stream=False
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"DeepSeek连接失败: {str(e)}")