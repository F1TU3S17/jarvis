import sys
import asyncio
import threading
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                            QFrame, QGraphicsDropShadowEffect, QSplitter, QMenu)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QPen, QColor, QLinearGradient
import speech_recognition as sr
from app.core.brain import Brain
from app.services.speak import SpeakService
from app.gui.hud_widgets import HUDPanel, PowerButton, VoiceVisualizerWidget
from app.gui.demo_features import JarvisDemoFeatures


class AnimatedCircle(QWidget):
    """Анимированный круг в стиле Джарвиса"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.is_listening = False
        self.is_speaking = False
        self.animation_angle = 0
        
        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
    def start_listening_animation(self):
        self.is_listening = True
        self.is_speaking = False
        self.animation_timer.start(50)  # 20 FPS
        
    def start_speaking_animation(self):
        self.is_listening = False
        self.is_speaking = True
        self.animation_timer.start(30)  # Быстрее для речи
        
    def stop_animation(self):
        self.is_listening = False
        self.is_speaking = False
        self.animation_timer.stop()
        self.update()
        
    def update_animation(self):
        self.animation_angle = (self.animation_angle + 5) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x, center_y = self.width() // 2, self.height() // 2
        radius = 80
        
        # Основной круг
        if self.is_listening:
            # Синий пульсирующий круг для прослушивания
            glow_radius = radius + 10 + 5 * abs(self.animation_angle % 60 - 30) / 30
            painter.setPen(QPen(QColor(0, 150, 255, 100), 3))
            painter.setBrush(QBrush(QColor(0, 100, 255, 30)))
            painter.drawEllipse(int(center_x - glow_radius), int(center_y - glow_radius), 
                              int(glow_radius * 2), int(glow_radius * 2))
                              
        elif self.is_speaking:
            # Золотой пульсирующий круг для речи
            glow_radius = radius + 5 + 8 * abs(self.animation_angle % 40 - 20) / 20
            painter.setPen(QPen(QColor(255, 215, 0, 150), 3))
            painter.setBrush(QBrush(QColor(255, 215, 0, 40)))
            painter.drawEllipse(int(center_x - glow_radius), int(center_y - glow_radius), 
                              int(glow_radius * 2), int(glow_radius * 2))
        else:
            # Статичный голубой круг
            painter.setPen(QPen(QColor(0, 255, 255, 200), 2))
            painter.setBrush(QBrush(QColor(0, 200, 255, 20)))
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
            
        # Внутренний круг
        inner_radius = 40
        painter.setPen(QPen(QColor(0, 255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(0, 150, 255, 50)))
        painter.drawEllipse(center_x - inner_radius, center_y - inner_radius, 
                          inner_radius * 2, inner_radius * 2)
        
        # Вращающиеся элементы
        if self.is_listening or self.is_speaking:
            painter.setPen(QPen(QColor(0, 255, 255, 200), 2))
            for i in range(6):
                angle = self.animation_angle + i * 60
                angle_rad = math.radians(angle)
                x1 = center_x + 60 * math.cos(angle_rad)
                y1 = center_y + 60 * math.sin(angle_rad)
                x2 = center_x + 70 * math.cos(angle_rad)
                y2 = center_y + 70 * math.sin(angle_rad)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))


class SpeechThread(QThread):
    """Поток для обработки речи"""
    text_recognized = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.is_running = False
        
    def run(self):
        self.is_running = True
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                self.text_recognized.emit(text)
            except sr.UnknownValueError:
                self.error_occurred.emit("Не удалось распознать речь")
            except sr.RequestError:
                self.error_occurred.emit("Ошибка сервиса распознавания")
            except sr.WaitTimeoutError:
                self.error_occurred.emit("Время ожидания истекло")
        self.is_running = False


class BrainThread(QThread):
    """Поток для обработки запросов к ИИ"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.brain = Brain()
        
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.brain.get_answer(user_input=self.text))
            self.response_ready.emit(response)
            loop.close()
        except Exception as e:
            self.error_occurred.emit(f"Ошибка обработки: {str(e)}")


class JarvisGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.brain = Brain()
        self.speak_service = SpeakService()
        self.speech_thread = None
        self.brain_thread = None
        self.demo_features = JarvisDemoFeatures(self)
        
        self.init_ui()
        self.setup_context_menu()
        
    def init_ui(self):
        self.setWindowTitle("J.A.R.V.I.S - Just A Rather Very Intelligent System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.get_jarvis_style())
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной макет с разделителем
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Создаем сплиттер для разделения на панели
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель (HUD)
        self.create_left_panel(splitter)
        
        # Центральная панель
        self.create_center_panel(splitter)
        
        # Правая панель (системная информация)
        self.create_right_panel(splitter)
        
        # Устанавливаем пропорции
        splitter.setSizes([200, 600, 200])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setCollapsible(2, False)
        
        main_layout.addWidget(splitter)
    
    def setup_context_menu(self):
        """Настройка контекстного меню"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """Показать контекстное меню"""
        context_menu = QMenu(self)
        
        # Основные действия
        about_action = context_menu.addAction("ℹ️ О программе")
        about_action.triggered.connect(self.demo_features.show_about_dialog)
        
        system_action = context_menu.addAction("🖥️ Системная информация")
        system_action.triggered.connect(self.demo_features.show_system_info)
        
        voice_action = context_menu.addAction("🔊 Настройки голоса")
        voice_action.triggered.connect(self.demo_features.show_voice_settings)
        
        context_menu.addSeparator()
        
        # Дополнительные функции
        docs_action = context_menu.addAction("📖 Документация")
        docs_action.triggered.connect(self.demo_features.open_documentation)
        
        easter_action = context_menu.addAction("🥚 Секретное меню")
        easter_action.triggered.connect(self.demo_features.show_easter_egg)
        
        context_menu.addSeparator()
        
        # Выход
        emergency_action = context_menu.addAction("⚠️ Экстренное завершение")
        emergency_action.triggered.connect(self.demo_features.emergency_shutdown)
        
        # Применяем стиль к меню
        context_menu.setStyleSheet("""
            QMenu {
                background: rgba(0, 50, 100, 0.9);
                border: 2px solid #00ffff;
                border-radius: 8px;
                color: #00ffff;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 5px;
            }
            QMenu::item {
                background: transparent;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: rgba(0, 255, 255, 0.2);
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background: #00ffff;
                margin: 5px 10px;
            }
        """)
        
        context_menu.exec_(self.mapToGlobal(position))
    
    def confirm_exit(self):
        """Подтверждение выхода из приложения"""
        from PyQt5.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Завершение работы J.A.R.V.I.S")
        msg.setText("Вы действительно хотите завершить работу J.A.R.V.I.S?")
        msg.setInformativeText("Все активные процессы будут остановлены.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setIcon(QMessageBox.Question)
        
        # Применяем стиль Джарвиса к диалогу
        msg.setStyleSheet("""
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
                font-size: 14px;
                background: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004d7a, stop:1 #00264d);
                border: 2px solid #00ffff;
                border-radius: 15px;
                color: #ffffff;
                font-weight: bold;
                padding: 10px 25px;
                min-width: 80px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0066a3, stop:1 #003366);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #003366, stop:1 #001a33);
            }
        """)
        
        result = msg.exec_()
        
        if result == QMessageBox.Yes:
            # Добавляем сообщение в чат перед выходом
            self.add_to_chat("J.A.R.V.I.S", "Завершаю работу. До свидания, сэр.")
            
            # Устанавливаем флаг закрытия
            self._closing = True
            
            # Останавливаем все активные потоки
            if self.speech_thread and self.speech_thread.isRunning():
                self.speech_thread.terminate()
            if self.brain_thread and self.brain_thread.isRunning():
                self.brain_thread.terminate()
                
            # Короткая задержка для отображения сообщения
            QTimer.singleShot(1500, self.close)
        else:
            # Пользователь отменил выход
            self.add_to_chat("J.A.R.V.I.S", "Отмена завершения работы. Продолжаю работу.")
    
    def closeEvent(self, event):
        """Обработка события закрытия окна"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Если приложение уже закрывается (например, через confirm_exit), просто закрываем
        if hasattr(self, '_closing') and self._closing:
            event.accept()
            return
            
        # Показываем диалог подтверждения
        msg = QMessageBox(self)
        msg.setWindowTitle("Завершение работы J.A.R.V.I.S")
        msg.setText("Вы действительно хотите завершить работу J.A.R.V.I.S?")
        msg.setInformativeText("Все активные процессы будут остановлены.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setIcon(QMessageBox.Question)
        
        # Применяем стиль
        msg.setStyleSheet("""
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
                font-size: 14px;
                background: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004d7a, stop:1 #00264d);
                border: 2px solid #00ffff;
                border-radius: 15px;
                color: #ffffff;
                font-weight: bold;
                padding: 10px 25px;
                min-width: 80px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0066a3, stop:1 #003366);
            }
        """)
        
        result = msg.exec_()
        
        if result == QMessageBox.Yes:
            # Устанавливаем флаг, что приложение закрывается
            self._closing = True
            
            # Останавливаем потоки
            if self.speech_thread and self.speech_thread.isRunning():
                self.speech_thread.terminate()
            if self.brain_thread and self.brain_thread.isRunning():
                self.brain_thread.terminate()
                
            event.accept()
        else:
            event.ignore()
    
    def create_left_panel(self, splitter):
        """Левая панель с элементами управления"""
        left_widget = QWidget()
        left_widget.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # Кнопка питания
        power_button = PowerButton()
        power_button.clicked.connect(self.confirm_exit)
        power_button.setToolTip("Завершить работу J.A.R.V.I.S\n(с подтверждением)")
        
        # Визуализатор голоса
        self.voice_visualizer = VoiceVisualizerWidget()
        
        # Элементы управления
        self.listen_button = QPushButton("🎤 СЛУШАТЬ")
        self.listen_button.setObjectName("listenButton")
        self.listen_button.clicked.connect(self.start_listening)
        
        self.stop_button = QPushButton("⏹ СТОП")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_listening)
        self.stop_button.setEnabled(False)
        
        left_layout.addWidget(QLabel("УПРАВЛЕНИЕ"))
        left_layout.addWidget(power_button, alignment=Qt.AlignCenter)
        left_layout.addWidget(QLabel())  # Spacer
        left_layout.addWidget(QLabel("ГОЛОС"))
        left_layout.addWidget(self.voice_visualizer)
        left_layout.addWidget(QLabel())  # Spacer
        left_layout.addWidget(self.listen_button)
        left_layout.addWidget(self.stop_button)
        left_layout.addStretch()
        
        splitter.addWidget(left_widget)
    
    def create_center_panel(self, splitter):
        """Центральная панель с основным интерфейсом"""
        center_widget = QWidget()
        center_widget.setObjectName("centerPanel")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(20)
        
        # Заголовок
        self.create_header(center_layout)
        
        # Анимированный круг
        self.create_jarvis_circle(center_layout)
        
        # Панель чата
        self.create_chat_panel(center_layout)
        
        # Статус бар
        self.create_status_bar(center_layout)
        
        splitter.addWidget(center_widget)
    
    def create_right_panel(self, splitter):
        """Правая панель с системной информацией"""
        right_widget = QWidget()
        right_widget.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_widget)
        
        # HUD панель
        self.hud_panel = HUDPanel()
        
        right_layout.addWidget(QLabel("СИСТЕМА"))
        right_layout.addWidget(self.hud_panel)
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        
    def create_header(self, layout):
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("J.A.R.V.I.S")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Just A Rather Very Intelligent System")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_vlayout = QVBoxLayout()
        header_vlayout.addWidget(title_label)
        header_vlayout.addWidget(subtitle_label)
        
        header_layout.addLayout(header_vlayout)
        layout.addWidget(header_frame)
        
    def create_jarvis_circle(self, layout):
        circle_frame = QFrame()
        circle_frame.setObjectName("circleFrame")
        circle_layout = QHBoxLayout(circle_frame)
        circle_layout.setAlignment(Qt.AlignCenter)
        
        self.jarvis_circle = AnimatedCircle()
        circle_layout.addWidget(self.jarvis_circle)
        
        layout.addWidget(circle_frame)
        
    def create_chat_panel(self, layout):
        chat_frame = QFrame()
        chat_frame.setObjectName("chatFrame")
        chat_layout = QVBoxLayout(chat_frame)
        
        chat_label = QLabel("Диалог:")
        chat_label.setObjectName("sectionLabel")
        
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("chatDisplay")
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(200)
        
        chat_layout.addWidget(chat_label)
        chat_layout.addWidget(self.chat_display)
        
        layout.addWidget(chat_frame)
        
    def create_status_bar(self, layout):
        self.status_label = QLabel("Готов к работе")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.status_label)
        
    def get_jarvis_style(self):
        return """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0a0a, stop:1 #1a1a2e);
            color: #00ffff;
        }
        
        QSplitter::handle {
            background: #00ffff;
            width: 2px;
        }
        
        #leftPanel, #rightPanel {
            background: rgba(0, 50, 100, 0.3);
            border: 1px solid #00ffff;
            border-radius: 10px;
            padding: 10px;
        }
        
        #centerPanel {
            background: rgba(0, 100, 255, 0.1);
            border: 2px solid #00ffff;
            border-radius: 15px;
            padding: 15px;
        }
        
        #headerFrame {
            background: rgba(0, 255, 255, 0.1);
            border: 2px solid #00ffff;
            border-radius: 15px;
            padding: 10px;
        }
        
        #titleLabel {
            font-family: 'Courier New', monospace;
            font-size: 28px;
            font-weight: bold;
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
        }
        
        #subtitleLabel {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #80d4ff;
            text-shadow: 0 0 5px #80d4ff;
        }
        
        #circleFrame {
            background: rgba(0, 100, 255, 0.05);
            border: 1px solid #0080ff;
            border-radius: 15px;
            padding: 20px;
        }
        
        #chatFrame {
            background: rgba(0, 255, 255, 0.05);
            border: 1px solid #00ffff;
            border-radius: 10px;
            padding: 15px;
        }
        
        #sectionLabel {
            font-family: 'Courier New', monospace;
            font-size: 16px;
            font-weight: bold;
            color: #00ffff;
            margin-bottom: 10px;
        }
        
        #chatDisplay {
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00ffff;
            border-radius: 8px;
            color: #ffffff;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            padding: 10px;
        }
        
        #listenButton, #stopButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #004d7a, stop:1 #00264d);
            border: 2px solid #00ffff;
            border-radius: 20px;
            color: #ffffff;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            font-weight: bold;
            padding: 12px 20px;
            margin: 3px;
        }
        
        #listenButton:hover, #stopButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0066a3, stop:1 #003366);
            box-shadow: 0 0 15px #00ffff;
        }
        
        #listenButton:pressed, #stopButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #003366, stop:1 #001a33);
        }
        
        #listenButton:disabled, #stopButton:disabled {
            background: #333333;
            color: #666666;
            border-color: #666666;
        }
        
        #statusLabel {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #80d4ff;
            padding: 10px;
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid #00ffff;
            border-radius: 5px;
        }
        
        /* HUD стили */
        #hudPanel {
            background: rgba(0, 50, 100, 0.4);
            border: 1px solid #00ffff;
            border-radius: 8px;
            padding: 15px;
        }
        
        #hudTimeLabel {
            font-family: 'Courier New', monospace;
            font-size: 16px;
            font-weight: bold;
            color: #00ffff;
            text-shadow: 0 0 8px #00ffff;
            text-align: center;
        }
        
        #hudInfoLabel {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #80d4ff;
            padding: 2px;
        }
        
        #hudStatusLabel {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: bold;
            color: #00ff00;
            text-shadow: 0 0 5px #00ff00;
            text-align: center;
        }
        
        QLabel {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #80d4ff;
            font-weight: bold;
        }
        
        QToolTip {
            background: rgba(0, 50, 100, 0.9);
            border: 2px solid #00ffff;
            border-radius: 8px;
            color: #00ffff;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            padding: 8px;
        }
        """
    
    def add_to_chat(self, sender, message):
        timestamp = QTimer().remainingTime()
        self.chat_display.append(f"<span style='color: #00ffff;'>[{sender}]:</span> {message}")
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def start_listening(self):
        self.listen_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Слушаю...")
        
        self.jarvis_circle.start_listening_animation()
        self.voice_visualizer.start_visualization()
        
        self.speech_thread = SpeechThread()
        self.speech_thread.text_recognized.connect(self.on_text_recognized)
        self.speech_thread.error_occurred.connect(self.on_speech_error)
        self.speech_thread.finished.connect(self.on_listening_finished)
        self.speech_thread.start()
    
    def stop_listening(self):
        if self.speech_thread and self.speech_thread.isRunning():
            self.speech_thread.terminate()
        self.on_listening_finished()
    
    def on_listening_finished(self):
        self.listen_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.jarvis_circle.stop_animation()
        self.voice_visualizer.stop_visualization()
        self.status_label.setText("Готов к работе")
    
    def on_text_recognized(self, text):
        self.add_to_chat("Пользователь", text)
        self.status_label.setText("Обрабатываю запрос...")
        
        self.jarvis_circle.start_speaking_animation()
        
        self.brain_thread = BrainThread(text)
        self.brain_thread.response_ready.connect(self.on_response_ready)
        self.brain_thread.error_occurred.connect(self.on_brain_error)
        self.brain_thread.start()
    
    def on_response_ready(self, response):
        self.add_to_chat("JARVIS", response)
        self.status_label.setText("Озвучиваю ответ...")
        
        # Запуск озвучки в отдельном потоке
        speak_thread = threading.Thread(target=self.speak_response, args=(response,))
        speak_thread.daemon = True
        speak_thread.start()
    
    def speak_response(self, response):
        try:
            self.speak_service.speak(response)
        except Exception as e:
            print(f"Ошибка озвучки: {e}")
        finally:
            # Возвращаемся в главный поток для обновления UI
            QTimer.singleShot(0, self.on_speaking_finished)
    
    def on_speaking_finished(self):
        self.jarvis_circle.stop_animation()
        self.status_label.setText("Готов к работе")
        self.start_listening()
    
    def on_speech_error(self, error):
        self.add_to_chat("Система", f"Ошибка распознавания: {error}")
        self.on_listening_finished()
    
    def on_brain_error(self, error):
        self.add_to_chat("Система", f"Ошибка обработки: {error}")
        self.jarvis_circle.stop_animation()
        self.status_label.setText("Готов к работе")


def main():
    app = QApplication(sys.argv)
    
    # Установка темной темы
    app.setStyle('Fusion')
    
    jarvis = JarvisGUI()
    jarvis.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
