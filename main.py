import time
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Error: This script must be run as administrator.")
    sys.exit(1)


from modules.controller import Controller
from modules.fish_bar import FishBar
from modules.template import *

from modules.keyboard import Keyboard

controller = Controller()
fish_bar = FishBar(controller)
keyboard = Keyboard()
keyboard.start_stop_listener()

def wait_until_appear(template):
    for frame in controller.loop():
        if template.match(frame):
            break

while True:
    wait_until_appear(HOOK)
    keyboard.click('f')
    wait_until_appear(TAKE_BAIT)
    keyboard.click('f')
    fish_bar.start()
    time.sleep(2)
    controller.mouse_click()