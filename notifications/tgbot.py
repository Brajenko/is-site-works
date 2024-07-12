import telegram

import config


async def send_message(msg: str, photo: str | None = None):
    """
    Send a message or a photo with a caption to a predefined Telegram user.

    This function sends a text message or a photo with a caption to the Telegram user specified
    by the user ID in the configuration. If a photo URL is provided, the photo is sent with the
    message as its caption. Otherwise, only the text message is sent.

    Args:
        msg: The message to be sent as text.
        photo: The URL of the photo to be sent. Optional.

    Raises:
        ValueError: If the message could not be delivered to the user.
    """
    bot = telegram.Bot(config.tg_bot_token)
    async with bot:
        try:
            if photo:
                await bot.send_photo(
                    chat_id=config.tg_user_tg_id,
                    photo=photo,
                    caption=msg,
                )
            else:
                await bot.send_message(
                    chat_id=config.tg_user_tg_id,
                    text=msg,
                )
        except telegram.error.Forbidden:
            raise ValueError('User not found')


async def check_id(tg_id: int, msg: str):
    """
    Send a message to a specified Telegram user to check if the user ID is valid.

    This function attempts to send a message to a Telegram user specified by the `tg_id`. It is
    used to verify if the provided user ID is valid and the bot has permission to send messages
    to this user.

    Args:
        tg_id: The Telegram user ID to which the message is sent.
        msg: The message to be sent as text.

    Raises:
        ValueError: If the message could not be delivered to the user (e.g., user not found).
    """
    bot = telegram.Bot(config.tg_bot_token)
    async with bot:
        try:
            await bot.send_message(
                chat_id=tg_id,
                text=msg,
            )
        except telegram.error.Forbidden:
            raise ValueError('User not found')


async def get_link() -> str:
    """
    Retrieve the public link to the bot's Telegram profile.

    This function generates and returns a URL to the bot's Telegram profile using the bot's
    username. This allows users to easily access the bot's profile on Telegram.

    Returns:
        A string containing the URL to the bot's Telegram profile.
    """
    return f'https://t.me/{(await telegram.Bot(config.tg_bot_token).get_me()).username}'
