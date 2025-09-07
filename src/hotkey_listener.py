from typing import Optional, Union
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard

from logger import get_logger, log_exception, HotkeyError


class GlobalHotkeyListener(QObject):
    """Handles global hotkey detection for Alt+W (show) and Alt+Ctrl+Q (quit)."""
    hotkey_pressed = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("hotkey_listener")
        self.listener: Optional[keyboard.Listener] = None
        self.logger.debug("Hotkey listener initialized")
        
    def start_listening(self) -> None:
        """Starts the global hotkey listener for Alt+W and Alt+Ctrl+Q."""
        try:            
            if self.listener is not None:
                self.logger.debug("Hotkey listener already running")
                return
            
            show_hotkey = keyboard.HotKey(
                keyboard.HotKey.parse('<alt>+w'),
                self.on_show_pressed
            )
            
            quit_hotkey = keyboard.HotKey(
                keyboard.HotKey.parse('<alt>+<ctrl>+q'),
                self.on_quit_pressed
            )
            
            def on_press(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]) -> None:
                """Handles key press events."""
                if key is not None:
                    try:
                        show_hotkey.press(listener.canonical(key))
                        quit_hotkey.press(listener.canonical(key))
                    except Exception as e:
                        self.logger.error(f"Error in hotkey press handler: {e}")
                
            def on_release(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]) -> None:
                """Handles key release events."""
                if key is not None:
                    try:
                        show_hotkey.release(listener.canonical(key))
                        quit_hotkey.release(listener.canonical(key))
                    except Exception as e:
                        self.logger.error(f"Error in hotkey release handler: {e}")
            
            listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self.listener = listener
            self.listener.start()
            self.logger.info("Hotkey listener started")
            
        except Exception as e:
            log_exception(self.logger, e, "starting hotkey listener")
            raise HotkeyError("Failed to start hotkey listener") from e
        
    def on_show_pressed(self) -> None:
        """Emits signal when show hotkey is pressed."""
        self.logger.info("Alt+W pressed - showing search")
        self.hotkey_pressed.emit()
    
    def on_quit_pressed(self) -> None:
        """Emits signal when hide hotkey is pressed."""
        self.logger.info("Alt+Ctrl+Q pressed - quitting application")
        self.quit_requested.emit()
        
    def stop_listening(self) -> None:
        """Stops the global hotkey listener and cleans up resources."""
        try:
            if self.listener:
                self.logger.debug("Hotkey listener stopping")
                self.listener.stop()
                self.listener = None
                self.logger.debug("Hotkey listener stopped")
        except Exception as e:
            log_exception(self.logger, e, "stopping hotkey listener")
