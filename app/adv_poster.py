from telethon import TelegramClient, sync, events
from telethon.tl.types import Message
from app.globals import Bot, BotConfig, PosterConfig
import datetime
import asyncio
from app.logger import *


@errors_catching_async
async def find_mess(userbot: TelegramClient, search_keyword: str, group_link: str):
    message = await userbot.get_messages(group_link, None, search=search_keyword)
    if message.total == 0:
        return False
    for mess in message:
        first_str = mess.message.split("\n")[0]
        if search_keyword in first_str:
            return mess
    return False

@errors_catching_async
async def adv_send(userbot: TelegramClient, poster: PosterConfig):
    start_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    errors = []
    list_post = None
    adv_post = None
    try:
        list_post = await find_mess(userbot, poster.group_list_keyword, poster.group_link)
        if not list_post:
            errors.append(f"Не найден пост со списком групп по фразе '{poster.group_list_keyword}'")
    except Exception as e:
        errors.append(f"Проблема доступа к группе {poster.group_link} Ошибка '{e}'")
    try:
        adv_post = await find_mess(userbot, poster.adv_post_keyword, poster.group_link)
        if not adv_post:
            errors.append(f"Не найден пост с рекламой по фразе '{poster.adv_post_keyword}'")
    except Exception as e:
        pass

    if not errors:
        errors = await send_to_groups(userbot, list_post, adv_post)
    
    end_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    log = f"Отправка начата в {start_time}\n"
    log += f"От имени '{bot.userbot_fio}'\n"
    log += "Параметры отправки:\n"
    log += f"   поиск списка групп по '{poster.group_list_keyword}'\n"
    log += f"   поиск рекламы по '{poster.adv_post_keyword}'\n"
    if errors:
        log += f"Ошибки отправки:\n"
        log += "\n".join(errors)+"\n"
    log += f"Отправка завершена в {end_time}\n"    
    if errors or (int(poster.debug) == 1):
        await userbot.send_message(entity = poster.report_reciever, message = log)
    return errors
    
@errors_catching_async
async def send_to_groups(userbot: TelegramClient, list_post: Message, adv_post: Message) -> list:
    errors = []
    grups_urls = list_post.message.split("\n")[1:]
    str_num=1
    for url in grups_urls:
        str_num+=1
        try:
            await userbot.send_message(entity=url, message=adv_post.message)
        except Exception as e:
            errors.append(f"адрес '{url}' в строке '{str_num}' -- {e}")

    return errors
