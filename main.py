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
    try:
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
            controller.sleep(2)
            controller.mouse_click()
            controller.sleep(0.5)
            keyboard.click('esc')
            wait_until_appear(HOOK, 5)
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
            wait_until_appear(HOOK, 5)
            return True

        logger.warning("Unknown event. Maybe failed to fish.")
    except Exception as e:
        logger.error(f"Failed to handle event: {e}, skipped.")

    return False

def handle_stuck():
    logger.info("Handling stuck...")
    start_time = time.time()
    for frame in controller.loop(interval=2):
        if HOOK.match(frame):
            logger.info("Found hook.")
            return True
        if START.match(frame):
            logger.info("Found start.")
            controller.mouse_click(START.pos)
            continue
        
        if time.time() - start_time >= 10:
            logger.error("Failed to handle stuck.")
            raise RuntimeError("Unrecoverable error happened. Request for human takeover.")
            
        keyboard.click('esc')

def main():
    logger.info("Initialization complete. Waiting for HOOK...")
    wait_until_appear(HOOK, 300)
    logger.info("Hook found, starting main loop...")
    last_time = time.time()


    begin_fish_time = None

    for frame in controller.loop():
        keyboard.click('f')
        controller.mouse_click()

        if FISH_ICON.match(frame):

            if not begin_fish_time:
                begin_fish_time = time.time()

            fish_bar.set_rect(FISH_ICON.pos)
            fish_bar.start()
            last_time = time.time()

            if config.TIMER_FINISHED_MINUTES and time.time() - begin_fish_time >= config.TIMER_FINISHED_MINUTES * 60:
                logger.info("Arrival end time.")
                config.POWER_OFF and os.system("shutdown /s /t 1")
                break

        if time.time() - last_time >= 20:
            logger.warning("No fish icon found for 20 seconds.")
            handle_event() or handle_stuck()
            last_time = time.time()
                

if __name__ == '__main__':
    main()