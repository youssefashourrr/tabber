import psutil
import win32gui
import win32process
import win32con
import threading
import time
from typing import Callable, List

from window import Window

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

    def __init__(self, auto_start_monitoring: bool = True):
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
        try:
            self.get_all_windows(force_refresh=True)
        except Exception as e:
            print(f"Error in initial window load: {e}")

    def _should_include_window(self, handle: int, process_name: str) -> bool:
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
                except:
                    return False

            return True
            
        except Exception:
            return False

    def add_change_callback(self, callback: Callable[[], None]) -> None:
        self._change_callbacks.append(callback)
        
    def remove_change_callback(self, callback: Callable[[], None]) -> None:
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
            
    def _notify_change_callbacks(self) -> None:
        for callback in self._change_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in window change callback: {e}")
                
    def _start_monitoring(self) -> None:
        def monitor_thread():
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
                            self._notify_change_callbacks()
                            
                except Exception as e:
                    print(f"Error in window monitoring thread: {e}")
                    if not self._stop_monitoring:
                        time.sleep(3)
                    
        self._monitoring_thread = threading.Thread(target=monitor_thread, daemon=True)
        self._monitoring_thread.start()
        
    def stop_monitoring(self):
        self._stop_monitoring = True
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=1)
        
    def _get_windows_now(self) -> List[Window]:
        windows = []

        def callback(handle: int, extra) -> bool:
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
                        pass
            return True

        try:
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            print(f"Error enumerating windows: {e}")
            
        return windows

    def get_all_windows(self, force_refresh: bool = False) -> List[Window]:
        with self._lock:
            current_time = time.time()
            
            if (force_refresh or not self._cached_windows or 
                current_time - self._last_refresh > self._refresh_interval):
                self._cached_windows = self._get_windows_now()
                self._last_refresh = current_time
                
            return self._cached_windows.copy()

    def switch_to_window(self, handle: int) -> bool:
        try:
            if not win32gui.IsWindow(handle) or not win32gui.IsWindowVisible(handle):
                return False

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
                except:
                    win32gui.ShowWindow(handle, win32con.SW_SHOW)

            return True

        except Exception as e:
            print(f"Error switching to window {handle}: {e}")
            return False
