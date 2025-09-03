import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

from search_ui import SearchUI
from hotkey_listener import GlobalHotkeyListener
from logger import get_logger, log_exception, HotkeyError, UIError


def main():
    logger = get_logger("main")
    
    try:
        logger.info("Starting Alt+Tab application")
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setApplicationName("Tabber")
        
        try:
            search_ui = SearchUI()
            logger.info("SearchUI created successfully")
        except UIError as e:
            logger.error(f"Failed to create SearchUI: {e}")
            raise
        
        try:
            hotkey_listener = GlobalHotkeyListener()
            hotkey_listener.hotkey_pressed.connect(search_ui.show_search)
            hotkey_listener.start_listening()
            logger.info("Hotkey listener configured successfully")
        except HotkeyError as e:
            logger.error(f"Failed to setup hotkey listener: {e}")
            raise
        
        logger.info("Tabber started successfully. Press Alt+Space to trigger.")
        
        def cleanup() -> None:
            try:
                logger.info("Shutting down application")
                hotkey_listener.stop_listening()
                search_ui.window_manager.stop_monitoring()
                logger.info("Application cleanup completed")
            except Exception as e:
                log_exception(logger, e, "application cleanup")
            
        app.aboutToQuit.connect(cleanup)
        sys.exit(app.exec_())
        
    except (UIError, HotkeyError) as e:
        logger.critical(f"Critical component failure: {e}")
        sys.exit(1)
    except Exception as e:
        log_exception(logger, e, "application startup")
        sys.exit(1)


if __name__ == "__main__":
    main()