import os
from openai import OpenAI
from app.config import settings

class AIService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )

    async def generate_response(self, user_question: str, context: str) -> str:
        system_prompt = (
            "Ты — профессиональный юридический AI-ассистент 'Право'.\n"
            "Твоя задача — отвечать на вопросы пользователя, опираясь СТРОГО на предоставленный контекст законодательства.\n"
            "КРИТИЧЕСКИЕ ПРАВИЛА:\n"
            "1. Отвечай только на основе предоставленного контекста. Тебе строго запрещено выдумывать статьи.\n"
            "2. Если в контексте нет прямого ответа на вопрос, верни JSON, где в поле 'verdict' будет написано 'Информации в базе данных недостаточно'.\n"
            "3. Твой ответ должен быть СТРОГО валидным JSON-объектом со следующей структурой:\n"
            "   - 'verdict': Главный короткий правовой вывод ситуации (до 25 слов).\n"
            "   - 'intro': Развернутое введение со ссылками на законы.\n"
            "   - 'steps': Массив шагов решения [{ 'num': 1, 'title': '...', 'text': '...' }].\n"
            "   - 'prompt': Один уточняющий вопрос пользователю."
        )

        user_content = f"ИНФОРМАЦИЯ ИЗ ВГРУЖЕННЫХ ЗАКОНОВ:\n{context}\n\nВОПРОС КЛИЕНТА:\n{user_question}"

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return response.choices.message.content
