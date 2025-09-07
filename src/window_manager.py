import psutil
import win32gui
import win32process
import win32con
import threading
import time
from typing import Callable, List

from window import Window
from logger import get_logger, log_exception, WindowManagerError

SYSTEM_PROCESSES = {
    'dwm.exe',
    'winlogon.exe',
    'csrss.exe',
    'TextInputHost.exe',
}

EXCLUDED_CLASSES = {
    'Shell_TrayWnd',
    'Progman',
    'WorkerW',
    'Button',
    'DV2ControlHost',
    'Windows.UI.Core.CoreWindow',
    'ApplicationFrameWindow',
}

MIN_WINDOW_WIDTH = 100
MIN_WINDOW_HEIGHT = 50


class WindowManager:
    """Manages window enumeration, filtering, and interaction on Windows."""

    def __init__(self, auto_start_monitoring: bool = True):
        self.logger = get_logger("window_manager")
        self._cached_windows = []
        self._last_refresh = 0
        self._refresh_interval = 2.0
        self._change_callbacks = []
        self._lock = threading.Lock()
        self._monitoring_thread = None
        self._stop_monitoring = False
        
        if auto_start_monitoring:
            self._start_monitoring()
            self._initial_load()
        
    def _initial_load(self):
        """Performs initial loading of windows during startup."""
        try:
            self.get_all_windows(force_refresh=True)
            self.logger.debug("Window manager initial load complete")
        except Exception as e:
            log_exception(self.logger, e, "initial window load")
            raise WindowManagerError("Failed to load initial windows") from e

    def _should_include_window(self, handle: int, process_name: str) -> bool:
        """Determines if a window should be included in the window list."""
        try:
            ex_style = win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE)
            if ex_style & (win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_NOACTIVATE):
                return False

            if win32gui.GetWindow(handle, win32con.GW_OWNER) != 0:
                return False

            style = win32gui.GetWindowLong(handle, win32con.GWL_STYLE)
            if not (style & win32con.WS_VISIBLE) or not (style & win32con.WS_CAPTION):
                return False

            class_name = win32gui.GetClassName(handle)
            if class_name in EXCLUDED_CLASSES or process_name in SYSTEM_PROCESSES:
                return False

            title = win32gui.GetWindowText(handle)
            if not title or not title.strip():
                return False

            if not win32gui.IsIconic(handle):
                    try:
                        rect = win32gui.GetWindowRect(handle)
                        width, height = rect[2] - rect[0], rect[3] - rect[1]
                        if width < MIN_WINDOW_WIDTH or height < MIN_WINDOW_HEIGHT:
                            return False
                    except Exception as e:
                        self.logger.error(f"Failed to get window rect for {handle}: {e}")
                        return False

            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check window properties for {handle}: {e}")
            return False

    def add_change_callback(self, callback: Callable[[], None]) -> None:
        """Adds a callback function to be called when window list changes."""
        self._change_callbacks.append(callback)
        
    def remove_change_callback(self, callback: Callable[[], None]) -> None:
        """Removes a previously added window change callback."""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
            
    def _notify_change_callbacks(self) -> None:
        """Notifies all registered callbacks about window list changes."""
        for callback in self._change_callbacks:
            try:
                callback()
            except Exception as e:
                log_exception(self.logger, e, "window change callback")
                
    def _start_monitoring(self) -> None:
        """Starts a background thread to monitor window changes."""
        def monitor_thread():
            """Background thread function that monitors window changes."""
            self.logger.debug("Window monitoring thread started")
            while not self._stop_monitoring:
                try:
                    time.sleep(self._refresh_interval)
                    
                    if self._stop_monitoring:
                        break
                        
                    if self._change_callbacks:
                        old_count = len(self._cached_windows)
                        self.get_all_windows(force_refresh=True)
                        new_count = len(self._cached_windows)
                        
                        if old_count != new_count:
                            self.logger.debug(f"Window count changed: {old_count} -> {new_count}")
                            self._notify_change_callbacks()
                            
                except Exception as e:
                    log_exception(self.logger, e, "window monitoring thread")
                    if not self._stop_monitoring:
                        time.sleep(3)
                    
        self._monitoring_thread = threading.Thread(target=monitor_thread, daemon=True)
        self._monitoring_thread.start()
        
    def stop_monitoring(self):
        """Stops the window monitoring thread."""
        self.logger.debug("Window monitoring stopping")
        self._stop_monitoring = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=1)
            if self._monitoring_thread.is_alive():
                self.logger.error("Monitor thread did not stop gracefully")
        
    def _get_windows_now(self) -> List[Window]:
        """Enumerates all current windows and returns filtered list."""
        windows = []

        def callback(handle: int, extra) -> bool:
            """Callback function for enumerating windows."""
            if win32gui.IsWindowVisible(handle):
                title = win32gui.GetWindowText(handle)
                if title:
                    try:
                        pid = win32process.GetWindowThreadProcessId(handle)[1]
                        process = psutil.Process(pid)
                        process_name = process.name()

                        if self._should_include_window(handle, process_name):
                            windows.append(Window(handle, title, pid, process_name))
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        self.logger.debug(f"Process access denied for window {handle}")
                    except Exception as e:
                        self.logger.error(f"Failed to get process info for window {handle}: {e}")
            return True

        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            log_exception(self.logger, e, "enumerating windows")
            raise WindowManagerError("Failed to enumerate windows") from e
            
        return windows

    def get_all_windows(self, force_refresh: bool = False) -> List[Window]:
        """Returns a list of all windows, using cache when possible."""
        try:
            with self._lock:
                current_time = time.time()
                
                if (force_refresh or not self._cached_windows or 
                    current_time - self._last_refresh > self._refresh_interval):
                    self._cached_windows = self._get_windows_now()
                    self._last_refresh = current_time
                    
                return self._cached_windows.copy()
        except Exception as e:
            log_exception(self.logger, e, "getting all windows")
            raise WindowManagerError("Failed to get window list") from e

    def switch_to_window(self, handle: int) -> bool:
        """Switches to the specified window by handle."""
        try:
            if not win32gui.IsWindow(handle) or not win32gui.IsWindowVisible(handle):
                self.logger.error(f"Cannot switch to invalid or invisible window {handle}")
                return False

            self.logger.debug(f"Switching to window {handle}")

            if win32gui.IsIconic(handle):
                win32gui.ShowWindow(handle, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(handle, win32con.SW_SHOW)

            win32gui.BringWindowToTop(handle)

            if not win32gui.SetForegroundWindow(handle):
                try:
                    win32gui.SetWindowPos(handle, win32con.HWND_TOP, 0, 0, 0, 0,
                                        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE |
                                        win32con.SWP_SHOWWINDOW)
                except Exception as pos_error:
                    self.logger.error(f"SetWindowPos failed {handle}: {pos_error}")
                    try:
                        win32gui.ShowWindow(handle, win32con.SW_SHOW)
                    except Exception as show_error:
                        self.logger.error(f"ShowWindow failed {handle}: {show_error}")
                        return False

            self.logger.info(f"Switched to window {handle}")
            return True

        except Exception as e:
            log_exception(self.logger, e, f"switching to window {handle}")
            return False
