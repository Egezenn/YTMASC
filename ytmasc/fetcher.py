"""
Provides a function to get the library page on YouTube.
"""

import webbrowser
from inspect import currentframe
from os import path
from platform import system

from pyautogui import click, hotkey, moveTo, press, sleep, typewrite
from pygetwindow import getWindowsWithTitle

from ytmasc.utility import (
    current_path,
    debug_print,
    get_current_file,
    get_current_function,
    library_page_path,
)

current_file = get_current_file(__file__)


def fetch(
    resend_amount=60,
    inbetween_delay=0.2,
    dialog_wait_delay=0.5,
    opening_delay=6,
    closing_delay=3,
    save_page_as_index_on_right_click=5,
):
    "Fetches library page while emulating user interaction."
    current_function = get_current_function(currentframe())

    systemInfo = system()
    if systemInfo == "Windows":
        # initializing the browser
        webbrowser.open_new_tab("https://music.youtube.com/playlist?list=LM")
        sleep(opening_delay)
        hotkey("winleft", "up")
        sleep(dialog_wait_delay)

        # scrolling the page down and getting to save dialog
        for amount in range(resend_amount):
            press(["end"])
            sleep(inbetween_delay)
        moveTo(0, 540)
        click(button="right")
        sleep(dialog_wait_delay)
        press(["down"] * save_page_as_index_on_right_click, interval=0.1)
        sleep(dialog_wait_delay)
        press("enter")
        sleep(dialog_wait_delay)

        # saving the files and exiting the browser
        getWindowsWithTitle("Save As")[0].activate()
        sleep(dialog_wait_delay)
        hotkey("ctrl", "a")
        sleep(dialog_wait_delay)
        typewrite(path.join(current_path, library_page_path))
        press("enter")
        sleep(closing_delay)
        hotkey("ctrl", "w")
        sleep(dialog_wait_delay)

    else:
        debug_print(
            current_file,
            current_function,
            "e",
            f"System is {systemInfo}, currently {current_file} doesn't support this OS.",
            error_type="UnsupportedConfiguration",
        )
