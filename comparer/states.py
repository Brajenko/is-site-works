import datetime as dt
import os
import asyncio
from urllib.parse import urlparse

from PIL import Image, ImageChops
from selenium import webdriver

import config
from notifications.tgbot import send_message
from db.schemas import (
    TrackingSchema,
    WebPageStateCreateSchema,
    WebPageStateSchema,
)
from db.utils import create_new_website_state, get_tracking_by_id


def get_states_folder_name(tr: TrackingSchema) -> str:
    """
    Generates a folder name for storing webpage states based on the tracking ID and URL.

    This function constructs a folder name by concatenating the tracking ID and the hostname
    extracted from the tracking URL. This folder is used to store screenshots representing
    different states of the tracked webpage.

    Args:
        tr (TrackingSchema): The tracking information, including the ID and URL of the webpage.

    Returns:
        str: The name of the folder for storing webpage states.
    """
    return str(tr.id) + str(urlparse(tr.url).hostname) + '/'


def update_state(tr: TrackingSchema) -> WebPageStateSchema | None:
    """
    Updates the state of a tracked webpage by taking a new screenshot, comparing it with the
    previous state, and saving the new state if changes are detected.

    This function takes a screenshot of the webpage specified in the TrackingSchema, compares
    it with the last saved state, and updates the database with the new state if any changes
    are detected. If the webpage has changed, a notification is sent via Telegram.

    Args:
        tr (TrackingSchema): The tracking information for the webpage to be updated.

    Returns:
        WebPageStateSchema | None: The new webpage state if changes are detected and saved,
                                   otherwise None.
    """
    screenshot_path = screenshot(tr)
    tr_last = get_tracking_by_id(tr.id)
    if not tr_last:
        return
    if tr_last.last_state:
        # compare
        prev = Image.open(tr_last.last_state.image_filename)
        curr = Image.open(screenshot_path)
        diff = ImageChops.difference(prev, curr)
        is_different = bool(diff.getbbox())
        if not tr.save_all_screenshots and not is_different:
            os.remove(screenshot_path)
            screenshot_path = tr_last.last_state.image_filename
        if is_different:
            asyncio.run(
                send_message(f'Сайт {tr.url} изменился', screenshot_path)
            )
    return create_new_website_state(
        WebPageStateCreateSchema(
            tracking_id=tr.id,
            image_filename=screenshot_path,
        )
    )


def screenshot(tr: TrackingSchema) -> str:
    """
    Takes a screenshot of a webpage specified in the TrackingSchema.

    This function initializes a headless Chrome browser, navigates to the URL specified in the
    TrackingSchema, and takes a full-page screenshot of the webpage. The screenshot is saved
    to a file whose path is constructed based on the tracking information and current timestamp.

    Args:
        tr (TrackingSchema): The tracking information, including the URL of the webpage.

    Returns:
        str: The file path of the saved screenshot.
    """
    service = webdriver.ChromeService(executable_path=r'./chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    with webdriver.Chrome(options, service) as driver:
        driver.get(tr.url)
        scroll_w = driver.execute_script(
            'return document.body.parentNode.scrollWidth'
        )
        scroll_h = driver.execute_script(
            'return document.body.parentNode.scrollHeight'
        )
        if scroll_h != 0 and scroll_w != 0:
            driver.set_window_size(scroll_w, scroll_h)
        filepath = f'{config.screenshots_folder}{get_states_folder_name(tr)}{dt.datetime.now().strftime(r"%d-%m-%Y %H%M%S")}.png'
        driver.save_screenshot(filepath)
        return filepath


def create_states_folder(tr: TrackingSchema):
    """
    Creates a directory for storing screenshots of webpage states.

    This function creates a directory named after the tracking ID and webpage hostname, where
    screenshots representing different states of the tracked webpage will be stored. If the
    directory already exists, no action is taken.

    Args:
        tr (TrackingSchema): The tracking information, used to generate the directory name.
    """
    folder_name = get_states_folder_name(tr)
    os.makedirs(config.screenshots_folder + folder_name, exist_ok=True)
