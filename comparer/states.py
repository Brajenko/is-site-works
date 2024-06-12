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
from db.utils import create_new_website_state, get_last_state, get_tracking_by_id


def get_states_folder_name(tr: TrackingSchema) -> str:
    return str(tr.id) + str(urlparse(tr.url).hostname) + "/"


def update_state(tr: TrackingSchema) -> WebPageStateSchema | None:
    """Makes screenshot, compares it with previous and saves, if something changed"""
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
            asyncio.run(send_message(f"Сайт {tr.url} изменился", screenshot_path))
    return create_new_website_state(
        WebPageStateCreateSchema(
            tracking_id=tr.id,
            image_filename=screenshot_path,
        )
    )


def screenshot(tr: TrackingSchema) -> str:
    service = webdriver.ChromeService(executable_path=r"./chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    with webdriver.Chrome(options, service) as driver:
        driver.get(tr.url)
        scroll_w = driver.execute_script("return document.body.parentNode.scrollWidth")
        scroll_h = driver.execute_script("return document.body.parentNode.scrollHeight")
        if scroll_h != 0 and scroll_w != 0:
            driver.set_window_size(scroll_w, scroll_h)
        filepath = f'{config.screenshots_folder}{get_states_folder_name(tr)}{dt.datetime.now().strftime(r"%d-%m-%Y %H%M%S")}.png'
        driver.save_screenshot(filepath)
        return filepath


def create_states_folder(tr: TrackingSchema):
    folder_name = get_states_folder_name(tr)
    os.makedirs(config.screenshots_folder + folder_name, exist_ok=True)
