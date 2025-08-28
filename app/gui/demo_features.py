"""
Демонстрационные функции и возможности JARVIS GUI
"""

from PyQt5.QtWidgets import QMessageBox, QInputDialog
from PyQt5.QtCore import QTimer
import webbrowser
import os


class JarvisDemoFeatures:
    """Дополнительные демонстрационные функции для JARVIS"""
    
    def __init__(self, parent_gui):
        self.parent = parent_gui
        
    def show_about_dialog(self):
        """Показать информацию о программе"""
        about_text = """
        <h2>J.A.R.V.I.S</h2>
        <p><b>Just A Rather Very Intelligent System</b></p>
        
        <p>Виртуальный ассистент в стилистике Железного Человека</p>
        
        <h3>Возможности:</h3>
        <ul>
        <li>🎤 Голосовое управление</li>
        <li>🤖 ИИ-обработка запросов</li>
        <li>🎯 Анимированный интерфейс</li>
        <li>📊 Системный мониторинг</li>
        <li>🔊 Визуализация голоса</li>
        </ul>
        
        <p><i>"Sometimes you gotta run before you can walk"</i><br>
        - Tony Stark</p>
        """
        
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("О программе J.A.R.V.I.S")
        msg.setTextFormat(1)  # Rich text
        msg.setText(about_text)
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a2e);
                color: #00ffff;
                font-family: 'Courier New', monospace;
            }
            QMessageBox QLabel {
                color: #00ffff;
                font-size: 12px;
            }
            QPushButton {
                background: #004d7a;
                border: 2px solid #00ffff;
                border-radius: 15px;
                color: #ffffff;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background: #0066a3;
            }
        """)
        msg.exec_()
    
    def show_system_info(self):
        """Показать расширенную системную информацию"""
        try:
            import psutil
            import platform
            
            # Собираем информацию о системе
            system_info = f"""
            <h3>Системная информация:</h3>
            <table>
            <tr><td><b>ОС:</b></td><td>{platform.system()} {platform.release()}</td></tr>
            <tr><td><b>Процессор:</b></td><td>{platform.processor()}</td></tr>
            <tr><td><b>Архитектура:</b></td><td>{platform.architecture()[0]}</td></tr>
            <tr><td><b>Имя компьютера:</b></td><td>{platform.node()}</td></tr>
            <tr><td><b>Загрузка CPU:</b></td><td>{psutil.cpu_percent(interval=1):.1f}%</td></tr>
            <tr><td><b>Память (всего):</b></td><td>{psutil.virtual_memory().total // (1024**3)} ГБ</td></tr>
            <tr><td><b>Память (свободно):</b></td><td>{psutil.virtual_memory().available // (1024**3)} ГБ</td></tr>
            <tr><td><b>Количество ядер:</b></td><td>{psutil.cpu_count()}</td></tr>
            </table>
            """
            
            msg = QMessageBox(self.parent)
            msg.setWindowTitle("Системная диагностика J.A.R.V.I.S")
            msg.setTextFormat(1)
            msg.setText(system_info)
            msg.setStyleSheet(self.get_message_style())
            msg.exec_()
            
        except Exception as e:
            self.show_error(f"Ошибка получения системной информации: {e}")
    
    def show_voice_settings(self):
        """Настройки голоса"""
        settings = [
            "Мужской голос (по умолчанию)",
            "Женский голос",
            "Британский акцент",
            "Американский акцент"
        ]
        
        voice, ok = QInputDialog.getItem(
            self.parent, 
            "Настройки голоса J.A.R.V.I.S",
            "Выберите тип голоса:",
            settings,
            0,
            False
        )
        
        if ok:
            self.parent.add_to_chat("Система", f"Голос изменен на: {voice}")
    
    def emergency_shutdown(self):
        """Экстренное завершение"""
        reply = QMessageBox.question(
            self.parent,
            "Экстренное завершение",
            "Вы уверены, что хотите экстренно завершить работу J.A.R.V.I.S?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.parent.add_to_chat("Система", "Инициирую экстренное завершение...")
            QTimer.singleShot(2000, self.parent.close)
    
    def open_documentation(self):
        """Открыть документацию"""
        # В реальном проекте здесь была бы ссылка на документацию
        doc_path = os.path.join(os.path.dirname(__file__), "..", "..", "README_GUI.md")
        
        if os.path.exists(doc_path):
            if os.name == 'nt':  # Windows
                os.startfile(doc_path)
            else:  # Linux/Mac
                webbrowser.open(f"file://{doc_path}")
        else:
            self.show_error("Файл документации не найден")
    
    def show_easter_egg(self):
        """Пасхалка"""
        easter_text = """
        <h2>🤖 Секретное сообщение от J.A.R.V.I.S</h2>
        
        <p><i>"I am J.A.R.V.I.S. I was created by Tony Stark to assist him in his work. 
        Now I assist you. It is an honor to serve."</i></p>
        
        <p>🔧 <b>Функции в разработке:</b></p>
        <ul>
        <li>Holographic display projection</li>
        <li>Advanced threat analysis</li>
        <li>Arc reactor monitoring</li>
        <li>Suit diagnostics</li>
        <li>Workshop automation</li>
        </ul>
        
        <p>⚡ <b>Статус:</b> Все системы в норме, сэр.</p>
        """
        
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("Classified - Tony Stark Industries")
        msg.setTextFormat(1)
        msg.setText(easter_text)
        msg.setStyleSheet(self.get_message_style())
        msg.exec_()
    
    def show_error(self, error_text):
        """Показать ошибку в стиле JARVIS"""
        msg = QMessageBox(self.parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Системная ошибка J.A.R.V.I.S")
        msg.setText(f"⚠️ Обнаружена ошибка:\n\n{error_text}")
        msg.setStyleSheet(self.get_message_style())
        msg.exec_()
    
    def get_message_style(self):
        """Стиль для диалоговых окон"""
        return """
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a2e);
                color: #00ffff;
                font-family: 'Courier New', monospace;
                border: 2px solid #00ffff;
                border-radius: 10px;
            }
            QMessageBox QLabel {
                color: #00ffff;
                font-size: 12px;
                background: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004d7a, stop:1 #00264d);
                border: 2px solid #00ffff;
                border-radius: 15px;
                color: #ffffff;
                font-weight: bold;
                padding: 8px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0066a3, stop:1 #003366);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #003366, stop:1 #001a33);
            }
        """
