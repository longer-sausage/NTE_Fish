import bettercam
import win32api
import win32gui
import win32con
import time
import random
from modules.logger import logger

class Controller:
    def __init__(self, window_name='异环  '):
        self.camera = bettercam.create(output_color="BGR")
        self.camera.start(target_fps=120, video_mode=True)
        self.window_name = window_name
        self.last_check_time = 0
        self.rect = None
        self._ensure_hwnd()

    def _ensure_hwnd(self):
        while True:
            self.hwnd = win32gui.FindWindow(None, self.window_name)
            if self.hwnd:
                logger.debug(f"Found window '{self.window_name}' with hwnd {self.hwnd}.")
                break
            else:
                logger.warning(f"Window '{self.window_name}' not found, waiting...")
                time.sleep(1)

    def screenshot(self):
        current_time = time.time()
        
        # Limit expensive win32gui calls to every 0.5s for extreme speed
        if current_time - self.last_check_time > 0.5 or self.rect is None:
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
                logger.debug(f"Window is out of screen (rect: {rect}), moving to center.")
                new_x = (screen_w - w) // 2
                new_y = (screen_h - h) // 2
                win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOP, new_x, new_y, 0, 0, win32con.SWP_NOSIZE)
                time.sleep(0.2)
                rect = win32gui.GetWindowRect(self.hwnd)

            self.rect = rect
            self.last_check_time = time.time()

        # Fetch frame from background thread instead of blocking synchronous grab
        frame = self.camera.get_latest_frame()
        if frame is None:
            frame = self.camera.grab()
            if frame is None:
                return None
                
        left, top, right, bottom = self.rect
        screen_h, screen_w = frame.shape[:2]
        
        # Ensure crop bounds are valid
        left = max(0, min(left, screen_w))
        right = max(0, min(right, screen_w))
        top = max(0, min(top, screen_h))
        bottom = max(0, min(bottom, screen_h))

        cropped = frame[top:bottom, left:right]
        if cropped.shape[1] < 1290 or cropped.shape[1] > 1310:
            raise ValueError("窗口尺寸不支持。请确保游戏分辨率设置为 1280x720。")
        return cropped

    def loop(self, interval=0.1):
        while True:
            try:
                s = self.screenshot()
            except ValueError:
                raise
            except Exception as e:
                logger.error(f"Error during screenshot: {e}")
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
        logger.debug(f"Mouse click at client pos {pos} (screen pos {x}, {y}).")
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def sleep(self, seconds, variance=0.2):
        low = seconds * (1 - variance)
        high = seconds * (1 + variance)
        t = sum(random.uniform(low, high) for _ in range(3)) / 3
        logger.debug(f"Sleeping for {t:.3f}s (target: {seconds}s).")
        time.sleep(t)