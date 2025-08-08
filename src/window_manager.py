import psutil
import win32gui
import win32process
import win32con

from window import Window


class WindowManager:
    def __init__(self):
        self.windows = []
    
    