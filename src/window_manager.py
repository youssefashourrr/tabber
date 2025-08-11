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
        self._windows = []

    def _should_include_window(self, handle: int, process_name: str) -> bool:
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

            if not (style & win32con.WS_CAPTION):
                return False

            class_name = win32gui.GetClassName(handle)
            if not class_name:
                return False

            excluded_classes = {
                'Shell_TrayWnd',
                'Progman',
                'WorkerW',
                'Button',
                'DV2ControlHost',
                'Windows.UI.Core.CoreWindow',
                'ApplicationFrameWindow',
            }
            if class_name in excluded_classes:
                return False

            try:
                rect = win32gui.GetWindowRect(handle)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                if width < 100 or height < 50:
                    return False
            except:
                return False

            if process_name in SYSTEM_PROCESSES:
                return False

            title = win32gui.GetWindowText(handle)
            if not title or title.strip() == "":
                return False

            if ex_style & win32con.WS_EX_NOACTIVATE:
                return False

            return True
        except:
            return False

    def get_all_windows(self) -> list[Window]:
        windows = []

        def callback(handle: int, extra) -> bool:
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
        self._windows = windows
        return windows

    def switch_to_window(self, handle: int) -> bool:
        try:
            if not win32gui.IsWindow(handle):
                return False

            if not win32gui.IsWindowVisible(handle):
                return False

            if win32gui.IsIconic(handle):
                win32gui.ShowWindow(handle, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(handle, win32con.SW_SHOW)

            win32gui.BringWindowToTop(handle)

            success = win32gui.SetForegroundWindow(handle)
            if not success:
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
