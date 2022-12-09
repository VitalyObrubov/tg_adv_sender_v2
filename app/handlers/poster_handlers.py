from telethon import TelegramClient, events
from telethon.events import StopPropagation 

from app.globals import PosterConfig, Bot, bot
from app.logger import errors_catching, errors_catching_async
from app.keyboard import *
from app.fsm import *
from app.utils import check_shedule
from app.adv_poster import adv_send, find_mess

@errors_catching_async
@allowed_states(CommonState.WAIT_ON_START)
async def manage_poster_click(event: events.CallbackQuery, who: int):
    fsm_data = fsm.get_data(who)
    poster_id = event.data.decode( "utf-8" ).split("-")[-1]
    if poster_id == "add":
        bot.add_poster()
        poster_id = len(bot.posters) - 1
    else:
        poster_id = int(poster_id)
    poster = bot.posters[poster_id]
    text = await poster_string(poster)
    text += "\nНажмите кнопку для изменения параметра"
    await event.edit(text, buttons = get_poster_btns(poster), link_preview = False)
    fsm.set_state(who, EditSenderState.WAIT_COMMAND)
    fsm_data['poster_id'] = poster_id
    fsm.set_data(who,fsm_data)
    raise StopPropagation

@errors_catching_async
@allowed_states(EditSenderState.WAIT_COMMAND)
async def back_to_start(event: events.CallbackQuery, who: int):
    fsm.set_state(who, CommonState.WAIT_ON_START)
    text = 'Вас приветствует бот управления рассылками'
    await event.edit(text, buttons = get_posters_btns(), link_preview = False)
    raise StopPropagation #Останавливает дальнейшую обработку

@errors_catching_async
@allowed_states(EditSenderState.WAIT_COMMAND)
async def change_poster_param(event: events.CallbackQuery, who: int):
    fsm_data = fsm.get_data(who)
    payload = event.data.decode( "utf-8" )
    poster_id = fsm_data['poster_id']
    param = payload.split("_")[1]
    poster = bot.posters[poster_id]
    buttons = get_poster_btns(poster)
    buttons.append([btn_cancel])
    buttons.remove([btn_back])
    if param == 'name':
        text = "Введите название расссылки"
        await event.edit(text, buttons = buttons, link_preview = False)       
    elif param == 'list':
        text = "Введите фразу поиска списка получателей"
        await event.edit(text, buttons = buttons, link_preview = False)        
    elif param == 'adv':
        text = "Введите фразу поиска поста с рекламой"
        await event.edit(text, buttons = buttons, link_preview = False)        
    elif param == 'link':
        text = "Введите ссылку канал или группу телеграмм в формате https://t.me/namedlink"
        await event.edit(text, buttons = buttons, link_preview = False) 
    elif param == 'recieverchange':
        text = "Введите ссылку на пользователя, канал или группу телеграмм в формате https://t.me/namedlink"
        await event.edit(text, buttons = buttons, link_preview = False) 
    elif param == 'schedule':
        text = "Введите расписание рассылки в формате crontab"
        await event.edit(text, buttons = buttons, link_preview = False)         
    elif param == 'debug':
        poster.debug ^= 1
        bot.save_poster_config()
        text = await poster_string(poster)
        text += "\nНажмите кнопку для изменения параметра"
        await event.edit(text, buttons = get_poster_btns(poster), link_preview = False)
        raise StopPropagation #Останавливает дальнейшую обработку
        return
    elif param == 'startschedule':
        if poster.cronjob:
            poster.sending_on ^= 1
            bot.save_poster_config()
            if poster.sending_on:
                poster.cronjob.resume()
                txt = "\n<b>Задача запущена </b>"
            else:
                poster.cronjob.pause()
                txt = "\n<b>Задача остановлена </b>"
            text = await poster_string(poster)
            text += "\nНажмите кнопку для изменения параметра"
            text += txt
            await event.edit(text, buttons = get_poster_btns(poster), link_preview = False)
        else:
            text = await poster_string(poster)
            text += "\n<b>Нет существующих задач для запуска </b>"
            text += "\nНажмите кнопку для изменения параметра"
            await event.edit(text, buttons = get_poster_btns(poster), link_preview = False)

        raise StopPropagation #Останавливает дальнейшую обработку
    elif param == 'del': 
        bot.posters.remove(poster)      
        fsm.set_state(who, CommonState.WAIT_ON_START)
        await event.edit('Вас приветствует бот управления рассылками',  buttons = get_posters_btns())
        bot.save_poster_config()
        raise StopPropagation #Останавливает дальнейшую обработку
    elif param == 'copy':
        bot.add_poster(poster)
        new_poster_id = len(bot.posters) - 1        
        new_poster = bot.posters[new_poster_id]
        text = str(new_poster)
        text += "\nНажмите кнопку для изменения параметра"
        await event.edit(text, buttons = get_poster_btns(poster), link_preview = False)
        fsm.set_state(who, EditSenderState.WAIT_COMMAND)
        fsm_data['poster_id'] = poster_id
        fsm.set_data(who,fsm_data)
        raise StopPropagation
    elif param == 'start':
        if not await bot.userbot.is_user_authorized():
            text = "Userbot для рассылки не активирован. Активируйте его из административного меню"
            await event.edit(text, buttons = get_poster_btns(poster))
            raise StopPropagation #Останавливает дальнейшую обработку    
        text = 'Идет рассыылка. Ожидайте'    
        fsm.set_state(who, EditSenderState.WAIT_SEND_FINISH)
        await event.edit(text, buttons = get_poster_btns(poster), link_preview = False) 
        err_text = await adv_send(bot, poster)
        text = await poster_string(poster)
        text += "\nНажмите кнопку для изменения параметра\n"
        text += "<b>"+",".join(err_text)+"</b>"
        await event.edit(text, buttons = get_poster_btns(poster), link_preview = False)
        fsm.set_state(who, EditSenderState.WAIT_COMMAND)     
        raise StopPropagation #Останавливает дальнейшую обработку
    fsm.set_state(who, EditSenderState.WAIT_INPUT_PARAM)
    fsm_data['main_event'] = event
    fsm_data['param'] = param
    fsm.set_data(who,fsm_data)
    raise StopPropagation

@errors_catching_async
@allowed_states(EditSenderState.WAIT_INPUT_PARAM)
async def update_param(event: events.NewMessage, who: int):
    await bot.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
    fsm_data = fsm.get_data(who)    
    param = fsm_data['param'] 
    poster = bot.posters[fsm_data['poster_id']] 
    main_event = fsm_data['main_event']
    value = event.message.message  
    if param == 'name':
        poster.name = value       
    elif param == 'list':
        poster.group_list_keyword = value
    elif param == 'adv':
        poster.adv_post_keyword = value       
    elif param == 'link':        
        poster.group_link = value
    elif param == 'recieverchange':              
        poster.report_reciever = value
    elif param == 'schedule':
        schedule = value
        res = check_shedule(schedule)
        if res:
            buttons = get_poster_btns(poster)
            buttons.append([btn_cancel])
            buttons.remove([btn_back])
            try: # выдает ошибку если пытаемся отправить то же текст
                await main_event.edit(res, buttons = buttons)
            except:
                pass
            raise StopPropagation
        else:
            poster.schedule = schedule
            bot.scheduler.update_poster_job(adv_send, poster, bot)

    bot.save_poster_config()
    text = await poster_string(poster)
    text += "\nНажмите кнопку для изменения параметра"
    await main_event.edit(text, buttons = get_poster_btns(poster), link_preview = False)
    fsm.set_state(who, EditSenderState.WAIT_COMMAND)    
    raise StopPropagation


@errors_catching_async
@allowed_states(EditSenderState.WAIT_INPUT_PARAM)
async def cancel_update_param(event: events.CallbackQuery, who: int):
    fsm_data = fsm.get_data(who)   
    poster = bot.posters[fsm_data['poster_id']]
    text = await poster_string(poster)
    text += "\nНажмите кнопку для изменения параметра"
    await event.edit(text, buttons = get_poster_btns(poster), link_preview = False)
    fsm.set_state(who, EditSenderState.WAIT_COMMAND)    
    raise StopPropagation

   

@errors_catching
def register_handlers():
    bot.add_event_handler(manage_poster_click, events.CallbackQuery(pattern='^poster-'))
    bot.add_event_handler(change_poster_param, events.CallbackQuery(pattern='^poster_'))
    bot.add_event_handler(back_to_start, events.CallbackQuery(pattern='^back$'))
    bot.add_event_handler(cancel_update_param, events.CallbackQuery(pattern='^cancel$'))
    bot.add_event_handler(update_param, events.NewMessage(chats=bot.config.admins, incoming=True))


async def poster_string(poster: PosterConfig):
    res = f'Рассылка: "{poster.name}"\n'
    res += f'Поиск списка по: "{poster.group_list_keyword}"\n'
    res += await check_post(poster.group_list_keyword, poster.group_link, bot)
    res += f'Поиск рекламы по: "{poster.adv_post_keyword}"\n'
    res += await check_post(poster.adv_post_keyword, poster.group_link, bot)
    res += f'Ссылка на группу с рекламой: "{poster.group_link}"\n'        
    res += f'Время рассылки: "{poster.schedule}"\n'
    res += f'Получатель отчетов: "{poster.report_reciever}"\n'
    debug = 'вкл.' if poster.debug else 'выкл.'
    res += f'Отладка: "{debug}"\n'
    sending = 'вкл.' if poster.sending_on else 'выкл.'
    res += f'Рассылка по расписанию: "{sending}"\n'
    return res

@errors_catching_async
async def check_post(search_keyword: str, group_link: str, bot) -> str:
    mess = await find_mess(search_keyword, group_link, bot)
    if mess:
        res = f"<a href='{group_link}/{mess.id}'>Ссылка на пост</a>\n"
    else:
        res = "Пост не найден\n"
    return res