from typing import Optional, Union
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard

from logger import get_logger, log_exception, HotkeyError


class GlobalHotkeyListener(QObject):
    hotkey_pressed = pyqtSignal()
    
    def __init__(self):
        try:
            super().__init__()
            self.logger = get_logger("hotkey_listener")
            self.listener: Optional[keyboard.Listener] = None
            self.logger.info("GlobalHotkeyListener initialized successfully")
        except Exception as e:
            logger = get_logger("hotkey_listener")
            log_exception(logger, e, "hotkey listener initialization")
            raise HotkeyError("Failed to initialize hotkey listener") from e
        
    def start_listening(self) -> None:
        try:
            self.logger.info("Starting hotkey listener for Alt+Space")
            
            if self.listener is not None:
                self.logger.warning("Hotkey listener is already running")
                return
            
            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse('<alt>+<space>'),
                self.on_hotkey_pressed
            )
            
            def on_press(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]) -> None:
                if key is not None:
                    try:
                        hotkey.press(listener.canonical(key))
                    except Exception as e:
                        self.logger.debug(f"Error in hotkey press handler: {e}")
                
            def on_release(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]) -> None:
                if key is not None:
                    try:
                        hotkey.release(listener.canonical(key))
                    except Exception as e:
                        self.logger.debug(f"Error in hotkey release handler: {e}")
            
            listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self.listener = listener
            self.listener.start()
            self.logger.info("Hotkey listener started successfully")
            
        except Exception as e:
            log_exception(self.logger, e, "starting hotkey listener")
            raise HotkeyError("Failed to start hotkey listener") from e
        
    def on_hotkey_pressed(self) -> None:
        try:
            self.logger.debug("Hotkey Alt+Space pressed")
            self.hotkey_pressed.emit()
        except Exception as e:
            log_exception(self.logger, e, "hotkey press signal emission")
            self.logger.error("Failed to emit hotkey pressed signal")
        
    def stop_listening(self) -> None:
        try:
            if self.listener:
                self.logger.info("Stopping hotkey listener")
                self.listener.stop()
                self.listener = None
                self.logger.info("Hotkey listener stopped successfully")
        except Exception as e:
            log_exception(self.logger, e, "stopping hotkey listener")
