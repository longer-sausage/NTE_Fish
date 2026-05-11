import numpy as np
import cv2
import time

from modules.controller import Controller
from modules.keyboard import Keyboard
from modules.logger import logger
from modules.template import *
import config
import os

class FishBar:
    GREEN_BAR = (173, 202, 42)  # BGR range
    YELLOW_CURSOR = (157, 246, 254) # BGR
    GREEN_BAR_LEFT = 0.5 - config.GREEN_BAR_SAFE_PROPORTION / 2
    GREEN_BAR_RIGHT = 0.5 + config.GREEN_BAR_SAFE_PROPORTION / 2

    def __init__(self, controller: Controller):
        self.controller = controller
        self.keyboard = Keyboard()
        self.current_key = None

        self.green_lower = np.clip(np.array(self.GREEN_BAR) - 10, 0, 255).astype(np.uint8)
        self.green_upper = np.clip(np.array(self.GREEN_BAR) + 10, 0, 255).astype(np.uint8)
        self.yellow_lower = np.clip(np.array(self.YELLOW_CURSOR) - 10, 0, 255).astype(np.uint8)
        self.yellow_upper = np.clip(np.array(self.YELLOW_CURSOR) + 10, 0, 255).astype(np.uint8)

    def set_rect(self, base_pos):
        x, y = base_pos
        x += 40
        y -= 10
        self.rect = (x, y, 495, 18)

    def save_debug_image(self, screenshot):
        if not hasattr(self, 'rect'):
            return
            
        x, y, w, h = self.rect
        debug_img = screenshot.copy()
        
        roi = screenshot[y:y+h, x:x+w]
        cv2.rectangle(debug_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        green_bar = self._get_green_bar(roi, x)
        cursor = self._get_yellow_cursor(roi, x)
        
        if green_bar:
            left, right = green_bar
            cv2.line(debug_img, (left, y), (left, y + h), (0, 255, 0), 2)
            cv2.line(debug_img, (right, y), (right, y + h), (0, 255, 0), 2)
            
            overlay = debug_img.copy()
            cv2.rectangle(overlay, (left, y), (right, y + h), (0, 255, 0), -1)
            cv2.addWeighted(overlay, 0.3, debug_img, 0.7, 0, debug_img)
            
        if cursor:
            cv2.line(debug_img, (cursor, y - 10), (cursor, y + h + 10), (0, 255, 255), 2)
            
        os.makedirs('screenshots', exist_ok=True)
        timestamp = int(time.time() * 1000)
        filename = f"screenshots/debug_fish_bar_{timestamp}.png"
        cv2.imwrite(filename, debug_img)
        logger.debug(f"Saved debug image: {filename}")
    
    def _get_green_bar(self, roi, x_offset):
        mask = cv2.inRange(roi, self.green_lower, self.green_upper)
        cols = np.where(np.any(mask, axis=0))[0]
        if cols.size > 0:
            left, right = cols[0] + x_offset, cols[-1] + x_offset
            width = right - left
            return (int(left + width * self.GREEN_BAR_LEFT), int(left + width * self.GREEN_BAR_RIGHT))
        return None

    def _get_yellow_cursor(self, roi, x_offset):
        mask = cv2.inRange(roi, self.yellow_lower, self.yellow_upper)
        cols = np.where(np.any(mask, axis=0))[0]
        if cols.size > 0:
            return int((cols[0] + cols[-1]) // 2 + x_offset)
        return None

    def _press(self, key):
        if self.current_key == key:
            return
        
        self._release_all()
        if key:
            logger.debug(f"Pressing '{key}'")
            self.keyboard.press(key)
            self.current_key = key

    def _release_all(self):
        if self.current_key:
            logger.debug(f"Releasing '{self.current_key}'")
            self.keyboard.release(self.current_key)
            self.current_key = None

    def start(self):
        missing_green_bar_count = 0
        x, y, w, h = self.rect
        for frame in self.controller.loop(interval=0):
            roi = frame[y:y+h, x:x+w]
            green_bar = self._get_green_bar(roi, x)
            
            if green_bar is None:
                missing_green_bar_count += 1
                if missing_green_bar_count > 10: # 连续 10 帧检测不到绿条才认为结束
                    break
                continue
            
            missing_green_bar_count = 0
            left, right = green_bar
            cursor = self._get_yellow_cursor(roi, x)

            if cursor is None:
                continue

            if config.SAVE_FISH_BAR_DEBUG_IMAGE:
                self.save_debug_image(frame)
            if cursor < left:
                self._press('d')
            elif cursor > right:
                self._press('a')
            else:
                self._release_all()

        self._release_all()