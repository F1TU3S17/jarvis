"""
Дополнительные виджеты для JARVIS GUI в стилистике HUD (Heads-Up Display)
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QBrush
import psutil
import datetime


class HUDPanel(QFrame):
    """Панель в стиле HUD с системной информацией"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("hudPanel")
        self.init_ui()
        
        # Таймер для обновления данных
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(1000)  # Обновление каждую секунду
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Время
        self.time_label = QLabel()
        self.time_label.setObjectName("hudTimeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)
        
        # Системные характеристики
        self.cpu_label = QLabel("CPU: ---%")
        self.cpu_label.setObjectName("hudInfoLabel")
        
        self.memory_label = QLabel("RAM: ---%")
        self.memory_label.setObjectName("hudInfoLabel")
        
        self.disk_label = QLabel("DISK: ---%")
        self.disk_label.setObjectName("hudInfoLabel")
        
        # Статус системы
        self.status_label = QLabel("СИСТЕМА: ГОТОВА")
        self.status_label.setObjectName("hudStatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.time_label)
        layout.addWidget(QLabel())  # Spacer
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.memory_label)
        layout.addWidget(self.disk_label)
        layout.addWidget(QLabel())  # Spacer
        layout.addWidget(self.status_label)
        
    def update_info(self):
        # Обновление времени
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        self.time_label.setText(f"{current_time}\n{current_date}")
        
        # Обновление системной информации
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_percent = psutil.virtual_memory().percent
            
            # Для Windows используем диск C:
            try:
                disk_percent = psutil.disk_usage('C:\\').percent
            except:
                disk_percent = 0
            
            self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
            self.memory_label.setText(f"RAM: {memory_percent:.1f}%")
            self.disk_label.setText(f"DISK: {disk_percent:.1f}%")
            
            # Изменение цвета в зависимости от нагрузки
            cpu_color = self.get_status_color(cpu_percent)
            memory_color = self.get_status_color(memory_percent)
            disk_color = self.get_status_color(disk_percent)
            
            self.cpu_label.setStyleSheet(f"color: {cpu_color};")
            self.memory_label.setStyleSheet(f"color: {memory_color};")
            self.disk_label.setStyleSheet(f"color: {disk_color};")
            
        except Exception as e:
            print(f"Ошибка обновления системной информации: {e}")
    
    def get_status_color(self, percent):
        """Возвращает цвет в зависимости от процента загрузки"""
        if percent < 50:
            return "#00ff00"  # Зеленый
        elif percent < 80:
            return "#ffff00"  # Желтый
        else:
            return "#ff0000"  # Красный


class PowerButton(QWidget):
    """Кнопка питания в стиле Джарвиса"""
    
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.is_hovered = False
        self.is_pressed = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x, center_y = self.width() // 2, self.height() // 2
        radius = 25
        
        # Внешний круг
        if self.is_pressed:
            color = QColor(255, 100, 100, 200)
        elif self.is_hovered:
            color = QColor(0, 255, 255, 200)
        else:
            color = QColor(0, 150, 255, 150)
            
        painter.setPen(QPen(color, 3))
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 30)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Символ питания
        painter.setPen(QPen(color, 4))
        painter.drawLine(center_x, center_y - 10, center_x, center_y + 10)
        
        # Дуга
        painter.drawArc(center_x - 8, center_y - 8, 16, 16, 0, 180 * 16)
    
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressed = True
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressed = False
            self.update()
            if self.rect().contains(event.pos()):
                self.clicked.emit()


class VoiceVisualizerWidget(QWidget):
    """Виджет визуализации голоса"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.levels = [0] * 20  # 20 полосок
        self.is_active = False
        
        # Таймер для анимации
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_levels)
        
    def start_visualization(self):
        self.is_active = True
        self.animation_timer.start(50)
        
    def stop_visualization(self):
        self.is_active = False
        self.animation_timer.stop()
        self.levels = [0] * 20
        self.update()
        
    def update_levels(self):
        if self.is_active:
            import random
            # Симуляция уровней звука
            for i in range(len(self.levels)):
                if random.random() > 0.3:
                    self.levels[i] = random.uniform(0.1, 1.0)
                else:
                    self.levels[i] *= 0.8  # Затухание
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        bar_width = width // len(self.levels)
        
        for i, level in enumerate(self.levels):
            x = i * bar_width
            bar_height = int(height * level)
            y = height - bar_height
            
            # Цветовой градиент от зеленого к красному
            if level < 0.3:
                color = QColor(0, 255, 0, 200)
            elif level < 0.7:
                color = QColor(255, 255, 0, 200)
            else:
                color = QColor(255, 0, 0, 200)
                
            painter.fillRect(x + 2, y, bar_width - 4, bar_height, color)
            
            # Подсветка
            painter.fillRect(x + 2, y, bar_width - 4, max(1, bar_height // 4), 
                           QColor(255, 255, 255, 100))
