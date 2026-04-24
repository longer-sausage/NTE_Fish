import bettercam
import win32api
import win32gui
import win32con
import time


class Controller:
    def __init__(self, window_name='异环  '):
        self.camera = bettercam.create(output_color="BGR")
        self.window_name = window_name
        self._ensure_hwnd()

    def _ensure_hwnd(self):
        while True:
            self.hwnd = win32gui.FindWindow(None, self.window_name)
            if self.hwnd:
                break

    def screenshot(self):
        if not win32gui.IsWindow(self.hwnd):
            self._ensure_hwnd()

        if win32gui.GetForegroundWindow() != self.hwnd:
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.5)

        rect = win32gui.GetWindowRect(self.hwnd)
        left, top, right, bottom = rect
        w, h = right - left, bottom - top
        
        screen_w = self.camera.width
        screen_h = self.camera.height

        is_out_of_screen = (left < 0 or top < 0 or right > screen_w or bottom > screen_h)
        
        if is_out_of_screen:
            new_x = (screen_w - w) // 2
            new_y = (screen_h - h) // 2
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, new_x, new_y, 0, 0, win32con.SWP_NOSIZE)
            time.sleep(0.2)
            rect = win32gui.GetWindowRect(self.hwnd)
            left, top, right, bottom = rect

        frame = self.camera.grab(region=(rect[0], rect[1], rect[2], rect[3]))
        return frame

    def loop(self, interval=0.1):
        while True:
            try:
                s = self.screenshot()
            except Exception:
                pass
            else:
                if s is not None:
                    yield s
            time.sleep(interval)

    def mouse_click(self, pos=(650, 700)):
        if not win32gui.IsWindow(self.hwnd):
            self._ensure_hwnd()

        if win32gui.GetForegroundWindow() != self.hwnd:
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.5)

        x, y = win32gui.ClientToScreen(self.hwnd, pos)
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)