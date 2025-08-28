from typing import Optional, Union
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard


class GlobalHotkeyListener(QObject):
    hotkey_pressed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.listener: Optional[keyboard.Listener] = None
        
    def start_listening(self) -> None:
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<alt>+<space>'),
            self.on_hotkey_pressed
        )
        
        def on_press(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]) -> None:
            if key is not None:
                hotkey.press(listener.canonical(key))
            
        def on_release(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]) -> None:
            if key is not None:
                hotkey.release(listener.canonical(key))
        
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.listener = listener
        self.listener.start()
        
    def on_hotkey_pressed(self) -> None:
        self.hotkey_pressed.emit()
        
    def stop_listening(self) -> None:
        if self.listener:
            self.listener.stop()
