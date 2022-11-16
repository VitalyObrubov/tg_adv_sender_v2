import logging, sys, asyncio
from app.logger import errors_catching, errors_catching_async
from app.globals import Bot, bot
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest 
from app.adv_poster import adv_send


logging.basicConfig(level=logging.INFO, filename="logs/py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s") 


@errors_catching_async
async def start():
    bot.userbot = TelegramClient('config/session_name_adv', bot.config.api_id, bot.config.api_hash)
    bot.userbot.parse_mode = 'HTML'
    await bot.userbot.start()
    try: # на всякий случай
        full = await bot.userbot(GetFullUserRequest("me"))
        bot.userbot_fio = f"{full.users[0].first_name} {full.users[0].last_name} {full.users[0].username}"
    except:
        pass    
    poster = bot.posters[poster_num]
    await adv_send(bot, poster)

if __name__ == '__main__':
    if len (sys.argv) > 1:
        poster_num = int(sys.argv[1])
        logging.info("Start bot pooling")

        bot.loop.run_until_complete(start())
        print("Finised")
    else:
        print("Не указан номер постера") 
        logging.error("Exception", exc_info="Не указан номер постера") 
