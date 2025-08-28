import asyncio
import httpx
import speech_recognition as sr

from app.core.brain import Brain
from app.services.speak import SpeakService






recognizer = sr.Recognizer()
speak_service = SpeakService()
brain = Brain()

while True:
    with sr.Microphone() as source:
        print("Скажи что-нибудь...")
        audio = recognizer.listen(source)
        
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")  # можно "en-US"

        response = asyncio.run(brain.get_answer(user_input=text))
        speak_service.speak(response)

    except sr.UnknownValueError:
        speak_service.speak("Не понял речь")
    except sr.RequestError:
        speak_service.speak("Ошибка запроса к сервису")


