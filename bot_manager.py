import logging
from app.logger import errors_catching, errors_catching_async
from app.handlers.main_handlers import register_handlers
from app.globals import Bot, bot
from app.scheduler import BotScheduler
from app.handlers.activate_userbot import activate_userbot
from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest 
from app.keyboard import *
from app.fsm import *
import pytz


logging.basicConfig(level=logging.INFO, filename="logs/py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s") 


@errors_catching_async
async def start():
    # Создаем планировщика
    bot.scheduler = BotScheduler(tzinfo=pytz.timezone('Europe/Moscow'),
                              n_threads=4)
    # Подключиться к серверу
    await bot.connect()    
    # Войти через токен. Метод sign_in возвращает информацию о боте. Мы сразу сохраним её в bot.me
    bot.me = await bot.sign_in(bot_token=bot.config.token)
    # Проверяет загруженные ссылки админов, удаляет нерабочие, сохраняет кофиг
    if await bot.check_admins(): 
        bot.save_bot_config()    
    register_handlers()  
    bot.userbot = TelegramClient('config/session_name_adv', bot.config.api_id, bot.config.api_hash)
    bot.userbot.parse_mode = 'HTML'
    await bot.userbot.connect()
    try: # на всякий случай
        full = await bot.userbot(GetFullUserRequest("me"))
        bot.userbot_fio = f"{full.users[0].first_name} {full.users[0].last_name} {full.users[0].username}"
    except:
        pass   
    # Начать получать апдейты от Телеграма и запустить все хендлеры
    print(f"Bot username: @{bot.me.username}")
    print(f"Bot name: {bot.me.first_name}")
    print('(Press Ctrl+C to stop this)')    
    await bot.run_until_disconnected()




if __name__ == '__main__':
  
    logging.info("Start bot pooling")

    bot.loop.run_until_complete(start())
   
