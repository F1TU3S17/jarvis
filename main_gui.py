#!/usr/bin/env python3
"""
JARVIS GUI Application
Графический интерфейс пользователя для ассистента JARVIS в стилистике Железного Человека
"""

import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.gui.jarvis_gui import main

if __name__ == "__main__":
    main()
