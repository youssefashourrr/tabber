import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal

from search_ui import SearchUI
from hotkey_listener import GlobalHotkeyListener


def main():
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setApplicationName("Alt+Tab")
        
        search_ui = SearchUI()
        
        hotkey_listener = GlobalHotkeyListener()
        hotkey_listener.hotkey_pressed.connect(search_ui.show_search)
        hotkey_listener.start_listening()
        
        print("Alt+Tab Replacement started. Press Alt+Space to activate search.")
        
        def cleanup() -> None:
            hotkey_listener.stop_listening()
            search_ui.window_manager.stop_monitoring()
            
        app.aboutToQuit.connect(cleanup)
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()