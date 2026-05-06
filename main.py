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
import config

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
            controller.sleep(0.2)
            return
        if time.time() - start_time > timeout:
            logger.warning(f"Wait for {template} timeout after {timeout}s.")
            raise TimeoutError(f"Wait for {template} failed after {timeout}s.")

def handle_event():
    logger.info("Try to handle event...")
    keyboard.click('f')
    controller.sleep(0.5)
    image = controller.screenshot()
    
    if FULL.match(image):
        logger.info("Found fish storage full.")
        if not config.SELL_FISH:
            logger.info("Sell fish is disabled. Stopping script...")
            sys.exit(0)
        controller.sleep(2)
        keyboard.click('q')
        wait_until_appear(FISH_STORAGE, 2)
        controller.sleep(0.5)
        controller.mouse_click(FISH_STORAGE.pos)
        wait_until_appear(SELL, 2)
        controller.sleep(0.5)
        controller.mouse_click(SELL.pos)
        wait_until_appear(SELL_CONFIRM, 2)
        controller.sleep(0.5)
        controller.mouse_click(SELL_CONFIRM.pos)
        wait_until_appear(SELL_SUCCESS, 10)
        controller.sleep(0.5)
        controller.mouse_click()
        while True:
            try:
                wait_until_appear(HOOK, 3)
                break
            except TimeoutError:
                keyboard.click('esc')
        return True

    if MONTH_CARD.match(image):
        logger.info("Found month card UI.")
        controller.mouse_click()
        wait_until_appear(GET_ITEM, 5)
        controller.mouse_click()
        return True

    if NEED_BAIT.match(image):
        logger.info("Found lack of bait.")
        if not config.BUY_BAIT:
            logger.info("Buy bait is disabled. Stopping script...")
            sys.exit(0)
        controller.sleep(2)
        keyboard.click('r')
        wait_until_appear(BAIT, 5)
        controller.mouse_click(BAIT.pos)
        img = controller.screenshot()
        MAX.match(img)
        BUY.match(img)
        for _ in range(config.BUY_BAIT_STACK_COUNT):
            controller.mouse_click(MAX.pos)
            controller.sleep(0.2)
            controller.mouse_click(BUY.pos)
            wait_until_appear(CONFIRM, 5)
            controller.mouse_click(CONFIRM.pos)
            wait_until_appear(GET_ITEM, 5)
            controller.mouse_click()
            wait_until_appear(BAIT, 5)
        keyboard.click('esc')
        wait_until_appear(HOOK, 5)
        keyboard.click('e')
        wait_until_appear(CHANGE, 5)
        controller.mouse_click(CHANGE.pos)
        return True

    logger.warning("Unknown event. Maybe failed to fish.")
    return False

def main():
    while True:
        try:
            wait_until_appear(HOOK, 3)
            keyboard.click('f')

            wait_until_appear(TAKE_BAIT, 10)
            keyboard.click('f')
            fish_bar.start()
            
            wait_until_appear(CLICK_BLANK, 10)
            controller.mouse_click()
        except TimeoutError:
            handle_event()
            continue

if __name__ == '__main__':
    main()