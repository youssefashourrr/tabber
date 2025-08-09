import psutil
import win32gui
import win32process
import win32con

from window import Window

SYSTEM_PROCESSES = {
    'dwm.exe',
    'winlogon.exe',
    'csrss.exe',
    'TextInputHost.exe',
}

class WindowManager:
    def __init__(self):
        self.windows = []
    
    def _should_include_window(self, handle, process_name):
        try:
            ex_style = win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE)
            if ex_style & win32con.WS_EX_TOOLWINDOW:
                return False
            
            owner = win32gui.GetWindow(handle, win32con.GW_OWNER)
            if owner != 0:
                return False
            
            style = win32gui.GetWindowLong(handle, win32con.GWL_STYLE)
            if not (style & win32con.WS_VISIBLE):
                return False
            
            if process_name in SYSTEM_PROCESSES:
                return False
            
            return True
        except:
            return False
    
    def get_all_windows(self):
        windows = []
        def callback(handle, extra):
            if win32gui.IsWindowVisible(handle):
                title = win32gui.GetWindowText(handle)
                if title:
                    try:
                        pid = win32process.GetWindowThreadProcessId(handle)[1]
                        process_name = psutil.Process(pid).name()
                        if self._should_include_window(handle, process_name):
                            windows.append(Window(handle, title, pid, process_name))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            return True
        win32gui.EnumWindows(callback, None)
        self.windows = windows
        return windows
