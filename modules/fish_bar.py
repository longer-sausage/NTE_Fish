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
        
        cv2.rectangle(debug_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        green_bar = self._get_green_bar(screenshot)
        cursor = self._get_yellow_cursor(screenshot)
        
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
    
    def _get_green_bar(self, screenshot):
        x, y, w, h = self.rect
        roi = screenshot[y:y+h, x:x+w]
        
        target = np.array(self.GREEN_BAR, dtype=np.int16)
        dist = np.sum(np.abs(roi.astype(np.int16) - target), axis=2)
        
        threshold = 10
        mask = dist < threshold
        cols = np.where(np.any(mask, axis=0))[0]
        if cols.size > 0:
            left, right = cols[0] + x, cols[-1] + x
            width = right - left
            return (int(left + width * self.GREEN_BAR_LEFT), int(left + width * self.GREEN_BAR_RIGHT))
        return None

    def _get_yellow_cursor(self, screenshot):
        x, y, w, h = self.rect
        roi = screenshot[y:y+h, x:x+w]
        
        target = np.array(self.YELLOW_CURSOR, dtype=np.int16)
        dist = np.sum(np.abs(roi.astype(np.int16) - target), axis=2)
        
        threshold = 10 
        mask = dist < threshold
        cols = np.where(np.any(mask, axis=0))[0]
        if cols.size > 0:
            return int((cols[0] + cols[-1]) // 2 + x)
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
        for frame in self.controller.loop():
            if FISH_ICON.match(frame):
                self.set_rect(FISH_ICON.pos)
                break
        
        missing_green_bar_count = 0
        for frame in self.controller.loop(interval=0):
            green_bar = self._get_green_bar(frame)
            
            if green_bar is None:
                missing_green_bar_count += 1
                if missing_green_bar_count > 10: # 连续 10 帧检测不到绿条才认为结束
                    break
                continue
            
            missing_green_bar_count = 0
            left, right = green_bar
            cursor = self._get_yellow_cursor(frame)

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