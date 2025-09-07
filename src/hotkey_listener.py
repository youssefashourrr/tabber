from typing import Optional, Union
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard

from logger import get_logger, log_exception, HotkeyError


class GlobalHotkeyListener(QObject):
    """Handles global hotkey detection for Alt+W (show) and Alt+Ctrl+Q (quit)."""
    hotkey_pressed = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self):
        try:
            super().__init__()
            self.logger = get_logger("hotkey_listener")
            self.listener: Optional[keyboard.Listener] = None
            self.logger.info("Initialized")
        except Exception as e:
            logger = get_logger("hotkey_listener")
            log_exception(logger, e, "hotkey listener initialization")
            raise HotkeyError("Failed to initialize hotkey listener") from e
        
    def start_listening(self) -> None:
        """Starts the global hotkey listener."""
        try:
            self.logger.info("Starting listener (Alt+W, Alt+Ctrl+Q)")
            
            if self.listener is not None:
                self.logger.warning("Already running")
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
                        self.logger.debug(f"Error in hotkey press handler: {e}")
                
            def on_release(key: Optional[Union[keyboard.Key, keyboard.KeyCode]]) -> None:
                """Handles key release events."""
                if key is not None:
                    try:
                        show_hotkey.release(listener.canonical(key))
                        quit_hotkey.release(listener.canonical(key))
                    except Exception as e:
                        self.logger.debug(f"Error in hotkey release handler: {e}")
            
            listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self.listener = listener
            self.listener.start()
            self.logger.info("Started successfully")
            
        except Exception as e:
            log_exception(self.logger, e, "starting hotkey listener")
            raise HotkeyError("Failed to start hotkey listener") from e
        
    def on_show_pressed(self) -> None:
        """Emits signal when Alt+W is pressed to show search bar."""
        try:
            self.logger.debug("Alt+W pressed")
            self.hotkey_pressed.emit()
        except Exception as e:
            log_exception(self.logger, e, "hotkey press signal emission")
            self.logger.error("Signal emission failed")
    
    def on_quit_pressed(self) -> None:
        """Emits signal when Alt+Ctrl+Q is pressed to quit application."""
        try:
            self.logger.info("Alt+Ctrl+Q pressed - shutting down")
            self.quit_requested.emit()
        except Exception as e:
            log_exception(self.logger, e, "quit hotkey press signal emission")
            self.logger.error("Quit signal failed")
        
    def stop_listening(self) -> None:
        """Stops the global hotkey listener and cleans up resources."""
        try:
            if self.listener:
                self.logger.info("Stopping listener")
                self.listener.stop()
                self.listener = None
                self.logger.info("Stopped")
        except Exception as e:
            log_exception(self.logger, e, "stopping hotkey listener")
