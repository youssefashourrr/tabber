import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

from searchbar import SearchBar
from hotkey_listener import GlobalHotkeyListener
from logger import get_logger, log_exception, HotkeyError, UIError


def main():
    logger = get_logger("main")
    
    try:
        logger.info("Starting application")
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setApplicationName("Tabber")
        
        try:
            searchbar = SearchBar()
            logger.info("UI initialized")
        except UIError as e:
            logger.error(f"UI initialization failed: {e}")
            raise
        
        try:
            hotkey_listener = GlobalHotkeyListener()
            hotkey_listener.hotkey_pressed.connect(searchbar.show_search)
            hotkey_listener.quit_requested.connect(app.quit)
            hotkey_listener.start_listening()
            logger.info("Hotkey listener ready")
        except HotkeyError as e:
            logger.error(f"Hotkey setup failed: {e}")
            raise
        
        logger.info("Application ready (Alt+W to open, Alt+Ctrl+Q to quit)")
        
        def cleanup() -> None:
            try:
                logger.info("Shutting down")
                hotkey_listener.stop_listening()
                searchbar.window_manager.stop_monitoring()
                logger.info("Cleanup complete")
            except Exception as e:
                log_exception(logger, e, "application cleanup")
            
        app.aboutToQuit.connect(cleanup)
        sys.exit(app.exec_())
        
    except (UIError, HotkeyError) as e:
        logger.critical(f"Component failure: {e}")
        sys.exit(1)
    except Exception as e:
        log_exception(logger, e, "application startup")
        sys.exit(1)


if __name__ == "__main__":
    main()