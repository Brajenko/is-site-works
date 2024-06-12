import telegram

import config


async def send_message(msg: str, photo: str | None = None):
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
    bot = telegram.Bot(config.tg_bot_token)
    async with bot:
        try:
            await bot.send_message(
                chat_id=tg_id,
                text=msg,
            )
        except telegram.error.Forbidden:
            raise ValueError('User not found')


async def get_link():
    return f'https://t.me/{(await telegram.Bot(config.tg_bot_token).get_me()).username}'
