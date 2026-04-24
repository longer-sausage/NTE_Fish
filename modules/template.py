import cv2

class Template:
    def __init__(self, filename: str):
        img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        alpha = img[:, :, 3]
        coords = cv2.findNonZero(alpha)
        x, y, w, h = cv2.boundingRect(coords)
        self.rect = (x, y, w, h)
        self.image = img[y:y+h, x:x+w, :3]
    
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
            
        res = cv2.matchTemplate(roi, self.image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        
        return max_val >= similarity



TAKE_BAIT = Template("./assets/templates/TAKE_BAIT.png")
HOOK = Template("./assets/templates/HOOK.png")