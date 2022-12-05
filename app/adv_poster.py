from telethon.tl.types import Message
import datetime, logging
from app.logger import errors_catching, errors_catching_async
from app.globals import Bot, BotConfig, PosterConfig

@errors_catching_async
async def find_mess(search_keyword: str, group_link: str, bot: Bot):
    try:
        message = await bot.userbot.get_messages(group_link, 30, search=search_keyword)
    except Exception as e:
        text = f"Error {e} in adv_poster.py proc find_mess"
        logging.error("Exception", exc_info=text)
        return False
    if message.total == 0:
        return False
    for mess in message:
        first_str = mess.message.split("\n")[0]
        if search_keyword in first_str:
            return mess
    return False

@errors_catching_async
async def adv_send(bot: Bot, poster: PosterConfig):
    start_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    errors = []
    if not await bot.userbot.is_user_authorized():
        errors.append("Userbot для рассылки не активирован. Активируйте его из административного меню")

    list_post = None
    adv_post = None
    try:
        list_post = await find_mess(poster.group_list_keyword, poster.group_link, bot)
        if not list_post:
            errors.append(f"Не найден пост со списком групп по фразе '{poster.group_list_keyword}'")
    except Exception as e:
        errors.append(f"Проблема доступа к группе с рекламой {poster.group_link} Ошибка '{e}'")
    try:
        adv_post = await find_mess(poster.adv_post_keyword, poster.group_link, bot)
        if not adv_post:
            errors.append(f"Не найден пост с рекламой по фразе '{poster.adv_post_keyword}'")
    except Exception as e:
        pass

    good_sends = []    
    if not errors:
        errors,good_sends = await send_to_groups( list_post, adv_post, bot)
    
    end_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    log = f"Отправка начата в {start_time}\n"
    log += f"От имени '{bot.userbot_fio}'\n"
    log += "Параметры отправки:\n"
    log += f"Поиск в группе '{poster.group_link}'\n"
    log += f"   поиск списка групп по '{poster.group_list_keyword}'\n"
    if list_post:
        log += f"<a href='{poster.group_link}/{list_post.id}'>Ссылка на пост с адресами</a>\n"
    log += f"   поиск рекламы по '{poster.adv_post_keyword}'\n"
    if adv_post:
        log += f"<a href='{poster.group_link}/{adv_post.id}'>Ссылка на пост с рекламой</a>\n"
    
    if errors:
        log += f"Ошибки отправки:\n"
        log += "\n".join(errors)+"\n"
    if good_sends:
        log += f"Удачные отправки:\n"
        log += "\n".join(good_sends)+"\n"
    log += f"Отправка завершена в {end_time}\n"    
    if errors or (int(poster.debug) == 1):
        await bot.userbot.send_message(entity = poster.report_reciever, message = log, link_preview = False)
    return errors
    
@errors_catching_async
async def send_to_groups(list_post: Message, adv_post: Message, bot: Bot) -> list:
    errors = []
    good_sends = []
    grups_urls = list_post.message.split("\n")[1:]
    str_num=1
    for url in grups_urls:
        str_num+=1
        try:
            await bot.userbot.send_message(entity=url, message=adv_post.message)
            good_sends.append(f"{url} - ok")
        except Exception as e:
            errors.append(f"адрес '{url}' в строке '{str_num}' -- {e}")

    return errors, good_sends

