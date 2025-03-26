import logging
import os
import platform
import webbrowser

import pyautogui
import pygetwindow

from ytmasc.utility import current_path, library_page_path

logger = logging.getLogger(__name__)


def fetch_lib_page(
    resend_amount=60,
    inbetween_delay=0.2,
    dialog_wait_delay=0.5,
    opening_delay=6,
    closing_delay=3,
    save_page_as_index_on_right_click=5,
):
    systemInfo = platform.system()
    if systemInfo == "Windows":
        # initializing the browser
        webbrowser.open_new_tab("https://music.youtube.com/playlist?list=LM")
        pyautogui.sleep(opening_delay)

        # scrolling the page down and getting to save dialog
        for _ in range(resend_amount):
            pyautogui.press(["end"])
            pyautogui.sleep(inbetween_delay)
        pyautogui.press("apps")
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.press(["down"] * save_page_as_index_on_right_click, interval=0.1)
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.press("enter")
        pyautogui.sleep(dialog_wait_delay)

        # saving the files and exiting the browser
        pygetwindow.getWindowsWithTitle("Save As")[0].activate()
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.typewrite(os.path.join(current_path, library_page_path))
        pyautogui.sleep(dialog_wait_delay)
        pyautogui.press("enter")
        pyautogui.sleep(closing_delay)
        pyautogui.hotkey("ctrl", "w")
        pyautogui.sleep(dialog_wait_delay)

    else:
        logger.error(f"[UnsupportedConfiguration] System is {systemInfo}, fetcher script doesn't support this OS.")
        pass
