import cv2
import os
from modules.logger import logger

class Template:
    def __init__(self, filename: str):
        self.name = os.path.basename(filename).split('.')[0]
        img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        if img is None:
            logger.error(f"Failed to load template: {filename}")
            raise FileNotFoundError(f"Template file not found: {filename}")
        alpha = img[:, :, 3]
        coords = cv2.findNonZero(alpha)
        x, y, w, h = cv2.boundingRect(coords)
        self.rect = (x, y, w, h)
        cropped_img = img[y:y+h, x:x+w, :3]
        gray_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        _, self.image = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY)
        logger.debug(f"Loaded template '{self.name}' with rect {self.rect}.")

    def __str__(self):
        return self.name
    
    def match(self, screenshot, offset=10, similarity=0.85):
        if screenshot is None or self.image is None:
            return False
            
        x, y, w, h = self.rect
        
        h_img, w_img = screenshot.shape[:2]
        x1 = max(0, x - offset)
        y1 = max(0, y - offset)
        x2 = min(w_img, x + w + offset)
        y2 = min(h_img, y + h + offset)
        
        roi = screenshot[y1:y2, x1:x2]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, roi_bin = cv2.threshold(roi_gray, 200, 255, cv2.THRESH_BINARY)
            
        res = cv2.matchTemplate(roi_bin, self.image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        
        return max_val >= similarity



TAKE_BAIT = Template("./assets/templates/TAKE_BAIT.png")
HOOK = Template("./assets/templates/HOOK.png")
CLICK_BLANK = Template("./assets/templates/CLICK_BLANK.png")