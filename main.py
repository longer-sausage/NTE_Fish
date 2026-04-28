import time
import ctypes
import sys
from modules.logger import logger

if not ctypes.windll.shell32.IsUserAnAdmin():
    logger.error("This script must be run as administrator.")
    sys.exit(1)

from modules.controller import Controller
from modules.fish_bar import FishBar
from modules.template import *
from modules.keyboard import Keyboard

logger.info("Initializing controllers...")
controller = Controller()
fish_bar = FishBar(controller)
keyboard = Keyboard()
keyboard.start_stop_listener()
logger.info("Initialization complete. Starting main loop.")

def wait_until_appear(template, timeout):
    logger.debug(f"Waiting for {template} with timeout {timeout}s...")
    start_time = time.time()
    for frame in controller.loop():
        if template.match(frame):
            logger.debug(f"Found {template}.")
            controller.sleep(0.1)
            return
        if time.time() - start_time > timeout:
            logger.warning(f"Wait for {template} timeout after {timeout}s.")
            raise TimeoutError(f"Wait for {template} failed after {timeout}s.")
    
while True:
    try:
        wait_until_appear(HOOK, 3)
        logger.info("Spinning rod...")
        keyboard.click('f')

        wait_until_appear(TAKE_BAIT, 10)
        logger.info("Taking bait...")
        keyboard.click('f')
        fish_bar.start()
        
        wait_until_appear(CLICK_BLANK, 10)
        logger.info("Clicking blank...")
        controller.mouse_click()
    except TimeoutError as e:
        controller.mouse_click()
        logger.warning(f"{e} Restarting main loop.")
        continue