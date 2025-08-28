import pyttsx3


class SpeakService:
    def __init__(self):
        pass

    def speak(self, text: str):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 225)      # скорость речи
            engine.setProperty("volume", 0.9)    # громкость (0-1)
            voices = engine.getProperty("voices")
            if voices:
                engine.setProperty("voice", voices[0].id)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"Ошибка озвучки: {e}")
            # Fallback на gTTS если pyttsx3 не работает
            self._fallback_speak(text)
