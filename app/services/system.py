import subprocess


class SystemService:
    @staticmethod
    def open_app(app_name: str):
        """
        Открывает приложение по имени.
        Примеры app_name: "notepad", "calc", "mspaint"
        """
        try:
            subprocess.Popen(app_name)
            return f"{app_name} успешно открыт."
        except FileNotFoundError:
            return f"Не удалось найти приложение {app_name}."
        except Exception as e:
            return f"Ошибка при открытии {app_name}: {e}"
    
    @staticmethod
    def set_volume(level: int) -> int:
        """Устанавливает громкость системы (0-100)"""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            from random import randint

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))


            volume.SetMasterVolumeLevelScalar(level / 100, None) 

            current_volume = volume.GetMasterVolumeLevelScalar() # Получить текущий уровень звука

        except Exception as e:
            return f"Ошибка при установке громкости: {e}"

        return current_volume
    
    @staticmethod
    def empty_recycle_bin():
        """Очищает корзину"""
        try:
            subprocess.run("rd /s /q C:\\$Recycle.Bin", shell=True)
            return "Корзина очищена"
        except Exception as e:
            return f"Ошибка очистки корзины: {e}"

