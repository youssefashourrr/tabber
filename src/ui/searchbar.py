from typing import List, Any
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QLineEdit, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QFocusEvent, QCloseEvent

from ..core.window_manager import WindowManager
from ..core.search_engine import search_windows
from ..core.window import Window
from ..utils.logger import get_logger, log_exception, UIError, SearchEngineError, WindowManagerError


class SearchBar(QWidget):
    """Main UI widget that provides a search interface for window switching."""
    def __init__(self):
        super().__init__()
        self.logger = get_logger("searchbar")
        
        try:
            self.window_manager = WindowManager()
            self.window_manager.add_change_callback(self.on_windows_changed)
            
            self.setup_ui()
            self.setup_style()
            self.setup_behavior()
            
            self.logger.debug("Search bar initialized")
        except Exception as e:
            log_exception(self.logger, e, "searchbar initialization")
            raise UIError("Failed to initialize search bar") from e
        
    def setup_ui(self) -> None:
        """Sets up the UI components including search input and results list."""
        try:
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(5)
            
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Search windows...")
            self.search_input.setMinimumHeight(45)
            self.search_input.textChanged.connect(self.on_search_changed)
            
            self.results_list = QListWidget()
            self.results_list.setMaximumHeight(300)
            self.results_list.itemClicked.connect(self.on_item_clicked)
            self.results_list.hide()
            
            main_layout.addWidget(self.search_input)
            main_layout.addWidget(self.results_list)
            
            self.setLayout(main_layout)
            self.logger.debug("UI setup complete")
        except Exception as e:
            log_exception(self.logger, e, "UI setup")
            raise UIError("Failed to setup UI components") from e
        
    def setup_style(self) -> None:
        """Applies modern styling to the search bar components."""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(45, 45, 45, 240);
                border-radius: 12px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLineEdit {
                background-color: rgba(60, 60, 60, 200);
                border: 2px solid rgba(100, 100, 100, 100);
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 16px;
                color: white;
            }
            
            QLineEdit:focus {
                border: 2px solid rgba(0, 120, 215, 200);
                background-color: rgba(70, 70, 70, 220);
            }
            
            QListWidget {
                background-color: rgba(50, 50, 50, 220);
                border: 1px solid rgba(100, 100, 100, 100);
                border-radius: 8px;
                outline: none;
                padding: 5px;
            }
            
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                margin: 2px 0px;
                min-height: 20px;
            }
            
            QListWidget::item:selected {
                background-color: rgba(0, 120, 215, 180);
                color: white;
            }
            
            QListWidget::item:hover {
                background-color: rgba(80, 80, 80, 150);
            }
        """)
        
    def setup_behavior(self) -> None:
        """Configures window behavior including always on top and transparency."""
        try:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)  # type: ignore
            self.setAttribute(Qt.WA_TranslucentBackground)  # type: ignore
            self.setFocusPolicy(Qt.StrongFocus)  # type: ignore
            
            self.setFixedWidth(500)
            self.resize(500, 55)
            self.center_on_screen()
            self.logger.debug("Behavior setup complete")
        except Exception as e:
            log_exception(self.logger, e, "UI behavior setup")
            raise UIError("Failed to setup UI behavior") from e
        
    def on_windows_changed(self) -> None:
        """Refreshes search results when window list changes."""
        try:
            if self.results_list.isVisible() and self.search_input.text().strip():
                self.on_search_changed(self.search_input.text())
        except Exception as e:
            log_exception(self.logger, e, "window change callback")
            self.results_list.hide()
            self.resize(500, 55)
        
    def center_on_screen(self) -> None:
        """Centers the search bar on the primary screen."""
        try:
            screen = QApplication.desktop().screenGeometry()  # type: ignore
            size = self.geometry()
            x = (screen.width() - size.width()) // 2
            y = (screen.height() - size.height()) // 3
            self.move(x, y)
        except Exception as e:
            self.logger.error(f"Failed to center on screen: {e}")
            self.move(100, 100)
        
    def show_search(self) -> None:
        """Shows the search bar and prepares it for user input."""
        try:
            self.logger.info("Search bar shown")
            self.search_input.clear()
            self.results_list.clear()
            self.results_list.hide()
            self.resize(500, 55)
            self.center_on_screen()
            self.show()
            self.activateWindow()
            self.search_input.setFocus()
        except Exception as e:
            log_exception(self.logger, e, "showing search UI")
            raise UIError("Failed to show search bar") from e
        
    def hide_search(self) -> None:
        """Hides the search bar and clears its contents."""
        self.hide()
        self.search_input.clear()
        self.results_list.clear()
        self.logger.info("Search bar hidden")
        
    def on_search_changed(self, text: str) -> None:
        """Handles search input changes and updates results display."""
        if not text.strip():
            self.results_list.hide()
            self.resize(500, 55)
            return
            
        try:
            self.logger.debug(f"Searching: '{text}'")
            current_windows = self.window_manager.get_all_windows()
            results = search_windows(current_windows, text)
            self.update_results(results[:3])
        except (SearchEngineError, WindowManagerError) as e:
            self.logger.error(f"Search failed: {e}")
            self.results_list.hide()
            self.resize(500, 55)
            raise
        except Exception as e:
            log_exception(self.logger, e, "search changed")
            self.results_list.hide()
            self.resize(500, 55)
            raise UIError("Failed to process search query") from e
            
    def update_results(self, windows: List[Window]) -> None:
        """Updates the results list with matching windows."""
        try:
            self.results_list.clear()
            
            if not windows:
                self.results_list.hide()
                self.resize(500, 55)
                return
                
            for window in windows:
                try:
                    item_text = self.format_window_item(window)
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.UserRole, window.handle)  # type: ignore
                    self.results_list.addItem(item)
                except Exception as e:
                    self.logger.error(f"Failed to create list item for window {window.handle}: {e}")
                    continue
                
            self.results_list.show()
            item_height = 44
            list_height = min(len(windows) * item_height + 10, 300)
            total_height = 55 + list_height + 5
            self.resize(500, total_height)
            
            if self.results_list.count() > 0:
                self.results_list.setCurrentRow(0)
        except Exception as e:
            log_exception(self.logger, e, "updating results")
            self.results_list.hide()
            self.resize(500, 55)
            
    def format_window_item(self, window: Window) -> str:
        """Formats a window title for display in the results list."""
        try:
            title = window.title
            if len(title) > 50:
                title = title[:47] + "..."
            return title
        except Exception as e:
            self.logger.error(f"Failed to format window item: {e}")
            return f"Window {window.handle}"
        
    def on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handles mouse clicks on window items in the results list."""
        try:
            window_handle = item.data(Qt.UserRole)  # type: ignore
            if window_handle is not None:
                self.switch_to_window(window_handle)
            else:
                self.logger.debug("No window handle in item data")
        except Exception as e:
            log_exception(self.logger, e, "item click handling")
        
    def switch_to_window(self, window_handle: int) -> None:
        """Switches to the specified window using the window manager."""
        try:
            self.logger.debug(f"Switching to window {window_handle}")
            success = self.window_manager.switch_to_window(window_handle)
            if success:
                self.hide_search()
                self.logger.info(f"Switched to window {window_handle}")
            else:
                self.logger.error(f"Failed to switch to window {window_handle}")
        except Exception as e:
            log_exception(self.logger, e, f"switching to window {window_handle}")
            
    def keyPressEvent(self, event: QKeyEvent) -> None:  # type: ignore
        """Handles keyboard events for navigation and actions."""
        if event.key() == Qt.Key_Escape:  # type: ignore
            self.hide_search()
            
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # type: ignore
            if self.results_list.isVisible() and self.results_list.count() > 0:
                current_item = self.results_list.currentItem()
                if current_item:
                    window_handle = current_item.data(Qt.UserRole)  # type: ignore
                    self.switch_to_window(window_handle)
                    
        elif event.key() == Qt.Key_Down:  # type: ignore
            if self.results_list.isVisible() and self.results_list.count() > 0:
                current_row = self.results_list.currentRow()
                if current_row < self.results_list.count() - 1:
                    self.results_list.setCurrentRow(current_row + 1)
                    
        elif event.key() == Qt.Key_Up:  # type: ignore
            if self.results_list.isVisible() and self.results_list.count() > 0:
                current_row = self.results_list.currentRow()
                if current_row > 0:
                    self.results_list.setCurrentRow(current_row - 1)
                    
        else:
            if not self.search_input.hasFocus():
                self.search_input.setFocus()
            super().keyPressEvent(event)
            
    def focusOutEvent(self, event: QFocusEvent) -> None:  # type: ignore
        """Handles focus loss events to auto-hide the search bar."""
        QTimer.singleShot(150, self.check_focus)
        
    def check_focus(self) -> None:
        """Checks if any part of the search bar has focus and hides if not."""
        try:
            if not self.hasFocus() and not self.search_input.hasFocus() and not self.results_list.hasFocus():
                self.hide_search()
        except Exception as e:
            self.logger.error(f"Focus check failed: {e}")
            self.hide_search()
            
    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore
        """Handles application close event and performs cleanup."""
        try:
            self.logger.debug("Search bar closing")
            self.window_manager.remove_change_callback(self.on_windows_changed)
            super().closeEvent(event)
        except Exception as e:
            log_exception(self.logger, e, "cleanup during close")
            super().closeEvent(event)
