from logging import getLogger
from os import path
from platform import system
from webbrowser import open_new_tab

from pyautogui import hotkey, press, sleep, typewrite
from pygetwindow import getWindowsWithTitle

from ytmasc.utility import current_path, library_page_path

logger = getLogger(__name__)


def fetch(
    resend_amount=60,
    inbetween_delay=0.2,
    dialog_wait_delay=0.5,
    opening_delay=6,
    closing_delay=3,
    save_page_as_index_on_right_click=5,
):
    systemInfo = system()
    if systemInfo == "Windows":
        # initializing the browser
        open_new_tab("https://music.youtube.com/playlist?list=LM")
        sleep(opening_delay)

        # scrolling the page down and getting to save dialog
        for _ in range(resend_amount):
            press(["end"])
            sleep(inbetween_delay)
        press("apps")
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
        sleep(dialog_wait_delay)
        press("enter")
        sleep(closing_delay)
        hotkey("ctrl", "w")
        sleep(dialog_wait_delay)

    else:
        logger.error(
            f"[UnsupportedConfiguration] System is {systemInfo}, fetcher script doesn't support this OS."
        )
        pass
