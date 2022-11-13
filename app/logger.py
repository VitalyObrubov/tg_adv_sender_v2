import logging
import functools
from telethon.events import StopPropagation
from app.globals import bot

def errors_catching_async(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except StopPropagation as e:
            raise
        except Exception as e:
            logging.error("Exception", exc_info=e) 
            print("Error has occurred. See log file")
            for admin in bot.config.admins:
                await bot.send_message(admin, f"Error has occurred. See log file {e}")
            return e
    return wrapper

def errors_catching(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error("Exception", exc_info=e) 
            print("Error has occurred. See log file")
            for admin in bot.config.admins:
                bot.send_message(admin, f"Error has occurred. See log file {e}")
            return e
    return wrapper