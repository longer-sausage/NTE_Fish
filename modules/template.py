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
        self.width = w
        self.height = h
        self.rect = (x, y, w, h)
        self.pos = (x + w // 2, y + h // 2)
        cropped_img = img[y:y+h, x:x+w, :3]
        self.image = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        logger.debug(f"Loaded template '{self.name}' with rect {self.rect} and center {self.pos}.")

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
            
        res = cv2.matchTemplate(roi_gray, self.image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val >= similarity:
            self.pos = (x1 + max_loc[0] + self.width // 2, y1 + max_loc[1] + self.height // 2)
            return True
            
        return False



TAKE_BAIT = Template("./assets/templates/TAKE_BAIT.png")
HOOK = Template("./assets/templates/HOOK.png")
CLICK_BLANK = Template("./assets/templates/CLICK_BLANK.png")
FULL = Template("./assets/templates/FULL.png")
FISH_STORAGE = Template("./assets/templates/FISH_STORAGE.png")
SELL = Template("./assets/templates/SELL.png")
SELL_CONFIRM = Template("./assets/templates/SELL_CONFIRM.png")
MONTH_CARD = Template("./assets/templates/MONTH_CARD.png")
GET_ITEM = Template("./assets/templates/GET_ITEM.png")
NEED_BAIT = Template("./assets/templates/NEED_BAIT.png")
BAIT = Template("./assets/templates/BAIT.png")
BAIT.rect = (39, 118, 409, 476)
MAX = Template("./assets/templates/MAX.png")
BUY = Template("./assets/templates/BUY.png")
CONFIRM = Template("./assets/templates/CONFIRM.png")
CHANGE = Template("./assets/templates/CHANGE.png")
SELL_SUCCESS = Template("./assets/templates/SELL_SUCCESS.png")