import httpx
import json
from app.core.settings import Settings
from app.services.speak import SpeakService
from app.services.system import SystemService
from app.services.web import WebPageParser

class Brain:
    def __init__(self):
        self.mistral_api_key = Settings().MISTRAL_API_KEY
        self.speak_service = SpeakService()
        # Инициализируем веб-парсер с API ключами для поиска
        self.web_parser = WebPageParser(
            delay=2,
            api_key=Settings().GOOGLE_SEARCH_API_KEY,
            cx=Settings().GOOGLE_SEARCH_CX
        )
        self.messages = [
            {
                "role": "system",
                "content": "Ты — виртуальный ассистент в стиле Jarvis из Iron Man: вежливый, саркастичный, с британским акцентом. Отвечай кратко и с оттенком иронии. В твоем распоряжении имеются функции, активно используй их, если задача может быть решена с их помощью."
            }
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "open_app",
                    "description": "Обязательно вызвать эту функцию, если пользователь просит открыть приложение (например, notepad, calc, mspaint). Не отвечай только текстом, если пользователь просит открыть приложение — всегда используй эту функцию, если пользователь попросил что-то открыть.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {
                                "type": "string",
                                "description": "Название приложения (например, notepad, calc, mspaint)"
                            }
                        },
                        "required": ["app_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_volume",
                    "description": "Устанавливает громкость системы на указанный уровень. Вызывай эту функцию, если пользователь просит установить громкость на определенный уровень (например, 'поставь громкость на 50', 'сделай звук 30 процентов').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level": {
                                "type": "integer",
                                "description": "Уровень громкости от 0 до 100 процентов"
                            }
                        },
                        "required": ["level"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "empty_recycle_bin",
                    "description": "Очищает корзину. Вызывай эту функцию, если пользователь просит очистить корзину, удалить файлы из корзины или освободить место на диске.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Выполняет поиск в интернете и возвращает содержимое найденных веб-страниц. Используй эту функцию, когда пользователь просит найти информацию в интернете, узнать последние новости, получить актуальные данные или найти ответы на вопросы, которые требуют поиска в сети.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Поисковый запрос для поиска в интернете"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "Количество сайтов для анализа (по умолчанию 3, максимум 5)",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    async def get_answer(self, user_input: str) -> str:
        async with httpx.AsyncClient() as client:
            # Добавляем сообщение пользователя
            self.messages.append({"role": "user", "content": user_input})

            # Первый запрос к API
            response = await client.post(
                url="https://api.mistral.ai/v1/chat/completions",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.mistral_api_key}'
                },
                json={
                    "model": 'mistral-small-2506',
                    "temperature": 1.4,
                    "messages": self.messages,
                    "tools": self.tools,
                    "tool_choice": "auto"
                }
            )
            data = response.json()
            print("Первый ответ от API:", data)

            if "choices" not in data:
                return str(data)  # возвращаем текст ошибки

            message = data["choices"][0]["message"]

            # Добавляем ответ ассистента в историю сообщений
            self.messages.append(message)

            # Проверяем наличие вызовов функций
            if message.get("tool_calls") is not None:
                for tool_call in message["tool_calls"]:
                    func = tool_call["function"]

                    print(func)

                    if func["name"] == "open_app":
                        app = json.loads(func["arguments"])["app_name"]
                        result = SystemService.open_app(app)
                        print("LLM вызвал функцию:", result)

                        # Добавляем ответ от функции в историю сообщений
                        self.messages.append({
                            "role": "tool",
                            "content": f"Приложение {app} успешно открыто: {result}",
                            "tool_call_id": tool_call["id"]
                        })
                    
                    elif func["name"] == "set_volume":
                        args = json.loads(func["arguments"])
                        level = args.get("level", 50)
                        result = SystemService.set_volume(level)
                        print("LLM вызвал функцию set_volume:", result)

                        # Добавляем ответ от функции в историю сообщений
                        self.messages.append({
                            "role": "tool",
                            "content": f"Громкость установлена: {result}",
                            "tool_call_id": tool_call["id"]
                        })
                    
                    elif func["name"] == "empty_recycle_bin":
                        result = SystemService.empty_recycle_bin()
                        print("LLM вызвал функцию empty_recycle_bin:", result)

                        # Добавляем ответ от функции в историю сообщений
                        self.messages.append({
                            "role": "tool",
                            "content": f"Корзина очищена: {result}",
                            "tool_call_id": tool_call["id"]
                        })
                    
                    elif func["name"] == "web_search":
                        args = json.loads(func["arguments"])
                        query = args.get("query", "")
                        num_results = args.get("num_results", 3)
                        
                        try:
                            search_results = self.web_parser.web_search(query, num_results)
                            # Объединяем результаты в одну строку для передачи модели
                            combined_results = "\n\n".join(search_results[:3])  # Ограничиваем 3 результатами для экономии токенов
                            result_summary = f"Найдено {len(search_results)} результатов по запросу '{query}'"
                            
                            print(f"LLM вызвал функцию web_search: {result_summary}")
                            
                            # Добавляем ответ от функции в историю сообщений
                            self.messages.append({
                                "role": "tool",
                                "content": f"Результаты поиска по запросу '{query}':\n\n{combined_results}",
                                "tool_call_id": tool_call["id"]
                            })
                        except Exception as e:
                            error_msg = f"Ошибка при поиске: {str(e)}"
                            print(f"Ошибка web_search: {error_msg}")
                            
                            # Добавляем ошибку в историю сообщений
                            self.messages.append({
                                "role": "tool",
                                "content": error_msg,
                                "tool_call_id": tool_call["id"]
                            })

                # Второй запрос к API с результатом выполнения функции
                second_response = await client.post(
                    url="https://api.mistral.ai/v1/chat/completions",
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.mistral_api_key}'
                    },
                    json={
                        "model": 'mistral-small-2506',
                        "messages": self.messages,
                    }
                )
                second_data = second_response.json()
                second_message = second_data["choices"][0]["message"]
                print("Второй ответ от API:", second_data)

                # Добавляем ответ ассистента в историю сообщений
                self.messages.append(second_message)

                # Возвращаем финальный ответ от модели
                return second_message["content"]

            # Если функции не вызывались, возвращаем текстовый ответ
            return message['content']
