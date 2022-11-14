from telethon.tl.types import Message
import datetime, typing
from app.logger import errors_catching, errors_catching_async

if typing.TYPE_CHECKING:
    from app.globals import Bot, BotConfig, PosterConfig

@errors_catching_async
async def find_mess(search_keyword: str, group_link: str, bot: Bot):
    message = await bot.userbot.get_messages(group_link, None, search=search_keyword)
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
        list_post = await find_mess(bot.userbot, poster.group_list_keyword, poster.group_link, bot)
        if not list_post:
            errors.append(f"Не найден пост со списком групп по фразе '{poster.group_list_keyword}'")
    except Exception as e:
        errors.append(f"Проблема доступа к группе с рекламой {poster.group_link} Ошибка '{e}'")
    try:
        adv_post = await find_mess(bot.userbot, poster.adv_post_keyword, poster.group_link)
        if not adv_post:
            errors.append(f"Не найден пост с рекламой по фразе '{poster.adv_post_keyword}'")
    except Exception as e:
        pass

    if not errors:
        errors = await send_to_groups( list_post, adv_post, bot)
    
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
        await bot.userbot.send_message(entity = poster.report_reciever, message = log)
    return errors
    
@errors_catching_async
async def send_to_groups(list_post: Message, adv_post: Message, bot: Bot) -> list:
    errors = []
    grups_urls = list_post.message.split("\n")[1:]
    str_num=1
    for url in grups_urls:
        str_num+=1
        try:
            await bot.userbot.send_message(entity=url, message=adv_post.message)
        except Exception as e:
            errors.append(f"адрес '{url}' в строке '{str_num}' -- {e}")

    return errors
