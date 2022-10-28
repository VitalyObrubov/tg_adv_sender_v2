from telethon import TelegramClient, sync, events
from telethon.tl.types import Message
from app.globals import Bot, BotConfig, PosterConfig
import datetime
import asyncio
from app.logger import *

@errors_catching_async
async def adv_send(client: Bot):
    start_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    errors = []
    list_post = None
    adv_post = None
    message = await client.get_messages(bot_config.group_link, search=sender_config.group_list_keyword, reverse=True)
    if message.total > 0:
        list_post = message[0]
    else:
        errors.append("Не найден пост со списком групп")

    message = await client.get_messages(bot_config.group_link, search=sender_config.adv_post_keyword, reverse=True)
    if message.total > 0:
        adv_post = message[0] 
    else:
        errors.append("Не найден пост с рекламой")
    
    if not errors:
        errors = await send_to_groups(client, list_post, adv_post)
    
    end_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    log = f"Отправка начата в {start_time}\n"
    log += "Параметры отправки:\n"
    log += f"   поиск списка групп по '{sender_config.group_list_keyword}'\n"
    log += f"   поиск рекламы по '{sender_config.adv_post_keyword}'\n"
    if errors:
        log += f"Ошибки отправки:\n"
        log += "\n".join(errors)+"\n"
    log += f"Отправка завершена в {end_time}\n"    
    if errors or (sender_config.debug == '1'):
        await client.send_message(entity=bot_config.group_link, message=log)
    return errors
    
@errors_catching_async
async def send_to_groups(client: TelegramClient, list_post: Message, adv_post: Message) -> list:
    errors = []
    grups_urls = list_post.message.split("\n")[1:]
    str_num=1
    for url in grups_urls:
        str_num+=1
        try:
            await client.send_message(entity=url, message=adv_post.message)
        except Exception as e:
            errors.append(f"адрес '{url}' в строке '{str_num}'")

    return errors
