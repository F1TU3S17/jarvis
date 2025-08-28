"""
Продвинутые голографические компоненты для JARVIS в стиле Marvel
"""

import math
import random
from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal, QPointF
from PyQt5.QtGui import (QPainter, QPen, QBrush, QColor, QLinearGradient, QRadialGradient, 
                        QPolygonF, QFont, QFontMetrics, QPainterPath)


class HolographicArc(QWidget):
    """Голографическая дуга с частицами"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 400)
        self.animation_angle = 0
        self.particles = []
        self.initialize_particles()
        
        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(33)  # 30 FPS
        
    def initialize_particles(self):
        """Инициализация частиц"""
        for _ in range(50):
            particle = {
                'x': random.uniform(50, 350),
                'y': random.uniform(50, 350),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'life': random.uniform(0.5, 1.0),
                'size': random.uniform(1, 3)
            }
            self.particles.append(particle)
    
    def update_animation(self):
        self.animation_angle = (self.animation_angle + 2) % 360
        
        # Обновление частиц
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 0.01
            
            # Перезапуск частицы
            if particle['life'] <= 0:
                particle['x'] = random.uniform(50, 350)
                particle['y'] = random.uniform(50, 350)
                particle['life'] = random.uniform(0.5, 1.0)
                
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x, center_y = self.width() // 2, self.height() // 2
        
        # Рисуем концентрические круги
        for i in range(5):
            radius = 50 + i * 30
            alpha = int(100 - i * 15)
            color = QColor(0, 255, 255, alpha)
            painter.setPen(QPen(color, 2))
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Рисуем вращающиеся дуги
        painter.setPen(QPen(QColor(0, 255, 255, 200), 3))
        for i in range(3):
            start_angle = (self.animation_angle + i * 120) % 360
            painter.drawArc(center_x - 100, center_y - 100, 200, 200, 
                          start_angle * 16, 60 * 16)
        
        # Рисуем радиальные линии
        painter.setPen(QPen(QColor(0, 200, 255, 150), 1))
        for i in range(12):
            angle = (self.animation_angle + i * 30) % 360
            angle_rad = math.radians(angle)
            x1 = center_x + 80 * math.cos(angle_rad)
            y1 = center_y + 80 * math.sin(angle_rad)
            x2 = center_x + 120 * math.cos(angle_rad)
            y2 = center_y + 120 * math.sin(angle_rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Рисуем частицы
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = QColor(0, 255, 255, alpha)
            painter.setPen(QPen(color, particle['size']))
            painter.drawPoint(int(particle['x']), int(particle['y']))


class DataStreamWidget(QWidget):
    """Виджет потока данных в стиле Matrix"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 400)
        self.data_streams = []
        self.initialize_streams()
        
        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_streams)
        self.animation_timer.start(100)
        
    def initialize_streams(self):
        """Инициализация потоков данных"""
        chars = "0123456789ABCDEF"
        for i in range(10):
            stream = {
                'x': i * 20 + 10,
                'chars': [random.choice(chars) for _ in range(20)],
                'y_offset': random.randint(0, 400),
                'speed': random.uniform(2, 5)
            }
            self.data_streams.append(stream)
    
    def update_streams(self):
        for stream in self.data_streams:
            stream['y_offset'] += stream['speed']
            if stream['y_offset'] > 400:
                stream['y_offset'] = -20
                # Обновляем символы
                chars = "0123456789ABCDEF"
                stream['chars'] = [random.choice(chars) for _ in range(20)]
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        font = QFont("Courier New", 10)
        painter.setFont(font)
        
        for stream in self.data_streams:
            for i, char in enumerate(stream['chars']):
                y = stream['y_offset'] + i * 15
                if 0 <= y <= 400:
                    alpha = max(0, min(255, 255 - abs(y - 200)))
                    color = QColor(0, 255, 100, alpha)
                    painter.setPen(color)
                    painter.drawText(stream['x'], int(y), char)


class HolographicInterface(QFrame):
    """Голографический интерфейс в стиле фильма"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("holographicInterface")
        self.setup_ui()
        
        # Анимация появления
        self.opacity_effect = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_effect.setDuration(2000)
        self.opacity_effect.setStartValue(0.0)
        self.opacity_effect.setEndValue(1.0)
        self.opacity_effect.setEasingCurve(QEasingCurve.InOutCubic)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок с эффектом
        title_widget = self.create_holographic_title()
        layout.addWidget(title_widget)
        
        # Основной контент
        content_layout = QHBoxLayout()
        
        # Левая панель с потоком данных
        data_stream = DataStreamWidget()
        content_layout.addWidget(data_stream)
        
        # Центральная голографическая дуга
        holo_arc = HolographicArc()
        content_layout.addWidget(holo_arc)
        
        # Правая панель с данными
        info_panel = self.create_info_panel()
        content_layout.addWidget(info_panel)
        
        layout.addLayout(content_layout)
        
    def create_holographic_title(self):
        """Создание голографического заголовка"""
        title_frame = QFrame()
        title_frame.setFixedHeight(100)
        
        return title_frame
        
    def create_info_panel(self):
        """Создание информационной панели"""
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setObjectName("infoPanel")
        
        layout = QVBoxLayout(panel)
        
        # Добавляем информационные элементы
        info_items = [
            "SYSTEM STATUS: ONLINE",
            "POWER LEVEL: 100%",
            "NETWORK: SECURE",
            "AI CORE: ACTIVE",
            "SENSORS: OPERATIONAL"
        ]
        
        for item in info_items:
            label = QLabel(item)
            label.setObjectName("infoItem")
            layout.addWidget(label)
            
        layout.addStretch()
        return panel


class CinematicJarvisCore(QWidget):
    """Кинематографическое ядро Джарвиса"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(500, 500)
        self.core_angle = 0
        self.pulse_radius = 0
        self.energy_rings = []
        self.scan_lines = []
        
        # Инициализация элементов
        self.initialize_energy_rings()
        self.initialize_scan_lines()
        
        # Таймеры анимации
        self.core_timer = QTimer()
        self.core_timer.timeout.connect(self.update_core)
        self.core_timer.start(50)
        
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.update_pulse)
        self.pulse_timer.start(100)
        
    def initialize_energy_rings(self):
        """Инициализация энергетических колец"""
        for i in range(5):
            ring = {
                'radius': 50 + i * 40,
                'angle': i * 72,
                'speed': 1 + i * 0.5,
                'opacity': 200 - i * 30
            }
            self.energy_rings.append(ring)
            
    def initialize_scan_lines(self):
        """Инициализация линий сканирования"""
        for i in range(8):
            line = {
                'angle': i * 45,
                'length': 150,
                'speed': 2,
                'opacity': 150
            }
            self.scan_lines.append(line)
    
    def update_core(self):
        self.core_angle = (self.core_angle + 1) % 360
        
        # Обновление энергетических колец
        for ring in self.energy_rings:
            ring['angle'] = (ring['angle'] + ring['speed']) % 360
            
        # Обновление линий сканирования
        for line in self.scan_lines:
            line['angle'] = (line['angle'] + line['speed']) % 360
            
        self.update()
        
    def update_pulse(self):
        self.pulse_radius = (self.pulse_radius + 5) % 200
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x, center_y = self.width() // 2, self.height() // 2
        
        # Фоновый градиент
        gradient = QRadialGradient(center_x, center_y, 200)
        gradient.setColorAt(0, QColor(0, 50, 100, 100))
        gradient.setColorAt(0.5, QColor(0, 100, 200, 50))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), QBrush(gradient))
        
        # Центральное ядро
        core_gradient = QRadialGradient(center_x, center_y, 30)
        core_gradient.setColorAt(0, QColor(255, 255, 255, 200))
        core_gradient.setColorAt(0.3, QColor(0, 255, 255, 150))
        core_gradient.setColorAt(1, QColor(0, 100, 255, 50))
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(QPen(QColor(0, 255, 255, 200), 2))
        painter.drawEllipse(center_x - 30, center_y - 30, 60, 60)
        
        # Энергетические кольца
        for ring in self.energy_rings:
            painter.setPen(QPen(QColor(0, 255, 255, ring['opacity']), 2))
            painter.drawEllipse(center_x - ring['radius'], center_y - ring['radius'], 
                              ring['radius'] * 2, ring['radius'] * 2)
        
        # Вращающиеся элементы
        painter.setPen(QPen(QColor(0, 255, 255, 150), 3))
        for i in range(6):
            angle = self.core_angle + i * 60
            angle_rad = math.radians(angle)
            x1 = center_x + 100 * math.cos(angle_rad)
            y1 = center_y + 100 * math.sin(angle_rad)
            x2 = center_x + 120 * math.cos(angle_rad)
            y2 = center_y + 120 * math.sin(angle_rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Линии сканирования
        for line in self.scan_lines:
            angle_rad = math.radians(line['angle'])
            painter.setPen(QPen(QColor(255, 255, 0, line['opacity']), 1))
            x1 = center_x + 50 * math.cos(angle_rad)
            y1 = center_y + 50 * math.sin(angle_rad)
            x2 = center_x + line['length'] * math.cos(angle_rad)
            y2 = center_y + line['length'] * math.sin(angle_rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Пульсирующий эффект
        if self.pulse_radius > 0:
            painter.setPen(QPen(QColor(0, 255, 255, 100), 2))
            painter.drawEllipse(center_x - self.pulse_radius, center_y - self.pulse_radius,
                              self.pulse_radius * 2, self.pulse_radius * 2)


class HolographicText(QLabel):
    """Голографический текст с эффектами"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.original_text = text
        self.glitch_timer = QTimer()
        self.glitch_timer.timeout.connect(self.create_glitch_effect)
        self.is_glitching = False
        
    def start_glitch_effect(self):
        """Запуск эффекта глитча"""
        self.is_glitching = True
        self.glitch_timer.start(100)
        QTimer.singleShot(2000, self.stop_glitch_effect)
        
    def stop_glitch_effect(self):
        """Остановка эффекта глитча"""
        self.is_glitching = False
        self.glitch_timer.stop()
        self.setText(self.original_text)
        
    def create_glitch_effect(self):
        """Создание эффекта глитча"""
        if self.is_glitching:
            glitch_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
            glitched_text = ""
            for char in self.original_text:
                if random.random() < 0.1:  # 10% шанс глитча
                    glitched_text += random.choice(glitch_chars)
                else:
                    glitched_text += char
            self.setText(glitched_text)


class AdvancedVoiceVisualizer(QWidget):
    """Продвинутый визуализатор голоса"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(150)
        self.setMinimumWidth(300)
        self.frequencies = [0] * 64  # 64 частотные полосы
        self.is_active = False
        
        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_frequencies)
        
    def start_visualization(self):
        self.is_active = True
        self.animation_timer.start(50)
        
    def stop_visualization(self):
        self.is_active = False
        self.animation_timer.stop()
        self.frequencies = [0] * 64
        self.update()
        
    def update_frequencies(self):
        if self.is_active:
            # Симуляция спектра частот
            for i in range(len(self.frequencies)):
                if random.random() > 0.3:
                    # Создаем реалистичный спектр
                    base_freq = math.sin(i * 0.1) * 0.5 + 0.5
                    noise = random.uniform(0, 0.3)
                    self.frequencies[i] = min(1.0, base_freq + noise)
                else:
                    self.frequencies[i] *= 0.85  # Затухание
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        bar_width = width / len(self.frequencies)
        
        for i, freq in enumerate(self.frequencies):
            x = i * bar_width
            bar_height = freq * height * 0.8
            y = height - bar_height
            
            # Цветовой градиент от низких к высоким частотам
            hue = int(240 - (i / len(self.frequencies)) * 180)  # От синего к красному
            color = QColor.fromHsv(hue, 255, min(255, int(255 * freq)))
            
            # Основная полоса
            painter.fillRect(int(x), int(y), int(bar_width - 1), int(bar_height), color)
            
            # Эффект свечения
            glow_color = QColor(color)
            glow_color.setAlpha(100)
            painter.fillRect(int(x), int(y - 5), int(bar_width - 1), 5, glow_color)
