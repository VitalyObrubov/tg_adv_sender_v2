from telethon import TelegramClient, events
from telethon.tl.custom import Button
from telethon.events import StopPropagation

from app.globals import PosterConfig, Bot, bot
from app.logger import errors_catching, errors_catching_async
from app.keyboard import *
from app.fsm import *
from app.utils import check_shedule


@errors_catching_async
async def manage_poster_click(event: events.CallbackQuery):
    who = event.sender_id
    state = fsm.get_state(who)
    fsm_data = fsm.get_data(who)
    if state != CommonState.WAIT_ON_START:
        return
    poster_id = event.data.decode( "utf-8" ).split("-")[-1]

    
    if poster_id == "add":
        bot.add_poster()
        poster_id = len(bot.posters) - 1
    else:
        poster_id = int(poster_id)
    poster = bot.posters[poster_id]
    text = str(poster)
    text += "\nНажмите кнопку для изменения параметра"
    await event.edit(text, buttons = get_poster_btns(poster))
    fsm.set_state(who, EditSenderState.WAIT_COMMAND)
    fsm_data['poster_id'] = poster_id
    fsm.set_data(who,fsm_data)
    raise StopPropagation

@errors_catching_async
async def back_to_start(event: events.CallbackQuery):
    who = event.sender_id
    state = fsm.get_state(who)
    fsm_data = fsm.get_data(who)    
    if state != EditSenderState.WAIT_COMMAND:
        return
    fsm.set_state(who, CommonState.WAIT_ON_START)
    await event.edit('Вас приветствует бот управления рассылками',  buttons = get_posters_btns())
    raise StopPropagation #Останавливает дальнейшую обработку

@errors_catching_async
async def change_poster_param(event: events.CallbackQuery):
    who = event.sender_id
    state = fsm.get_state(who)
    fsm_data = fsm.get_data(who)
    
    if state != EditSenderState.WAIT_COMMAND:
        return
    payload = event.data.decode( "utf-8" )
    poster_id = fsm_data['poster_id']
    param = payload.split("_")[1]
    poster = bot.posters[poster_id]
    if param == 'name':
        text = "Введите название расссылки"
        await event.edit(text, buttons = [btn_cancel])       
    elif param == 'list':
        text = "Введите фразу поиска списка получателей"
        await event.edit(text, buttons = [btn_cancel])       
    elif param == 'adv':
        text = "Введите фразу поиска поста с рекламой"
        await event.edit(text, buttons = [btn_cancel])       
    elif param == 'link':
        text = "Введите ссылку на группу с данными"
        await event.edit(text, buttons = [btn_cancel])
    elif param == 'schedule':
        text = "Введите расписание рассылки в формате: 10:20,12:30,16:40"
        await event.edit(text, buttons = [btn_cancel])        
    elif param == 'debug':
        poster.debug ^= 1
        bot.save_poster_config()
        text = str(poster)
        text += "\nНажмите кнопку для изменения параметра"
        await event.edit(text, buttons = get_poster_btns(poster))
        raise StopPropagation #Останавливает дальнейшую обработку
        return
    elif param == 'report':
        poster.recieve_reports ^= 1
        bot.save_poster_config()
        text = str(poster)
        text += "\nНажмите кнопку для изменения параметра"
        await event.edit(text, buttons = get_poster_btns(poster))
        raise StopPropagation #Останавливает дальнейшую обработку
        return
    elif param == 'del': 
        bot.posters.remove(poster)      
        fsm.set_state(who, CommonState.WAIT_ON_START)
        await event.edit('Вас приветствует бот управления рассылками',  buttons = get_posters_btns())
        bot.save_poster_config()
        raise StopPropagation #Останавливает дальнейшую обработку
        return
    elif param == 'start':
        userbot = TelegramClient('config/session_name_adv', bot.config.api_id, bot.config.api_hash)
        await userbot.connect()
        if not await userbot.is_user_authorized():
            text = 'Для авторизации введите свой телефонный номер пользователя в телеграм в формате +7ХХХХХХХХХХ' 
            await event.edit(text, buttons = [btn_cancel])
            fsm_data['main_event'] = event
            fsm_data['param'] = "phone"
            fsm_data['userbot'] = userbot
            fsm.set_state(who, EditSenderState.WAIT_INPUT_PHONE)
            fsm.set_data(who,fsm_data)
            raise StopPropagation #Останавливает дальнейшую обработку

        else:
            text = 'Идет рассыылка. Ожидайте' 
            await event.edit(text) 
            err_text = await post_advertisement(userbot, poster) 
            text = str(poster)
            text += "\nНажмите кнопку для изменения параметра\n"
            text += err_text
            await event.edit(text, buttons = get_poster_btns(poster))
            fsm.set_state(who, EditSenderState.WAIT_COMMAND)     
            raise StopPropagation #Останавливает дальнейшую обработку


    fsm.set_state(who, EditSenderState.WAIT_INPUT_PARAM)
    fsm_data['main_event'] = event
    fsm_data['param'] = param
    fsm.set_data(who,fsm_data)
    raise StopPropagation

@errors_catching_async
async def update_param(event: events.NewMessage):
    await bot.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
    who = event.sender_id
    state = fsm.get_state(who)
    fsm_data = fsm.get_data(who)    
    if state != EditSenderState.WAIT_INPUT_PARAM:
        return
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
    elif param == 'schedule':
        schedule = value.split(',')
        res = check_shedule(schedule)
        if res:
            await main_event.edit(res, buttons = [btn_cancel])
            raise StopPropagation
            return
        else:
            poster.schedule = schedule

    bot.save_poster_config()
    text = str(poster)
    text += "\nНажмите кнопку для изменения параметра"
    await main_event.edit(text, buttons = get_poster_btns(poster))
    fsm.set_state(who, EditSenderState.WAIT_COMMAND)    
    raise StopPropagation

@errors_catching_async
async def send_phone(event: events.NewMessage):
    await bot.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
    who = event.sender_id
    state = fsm.get_state(who)
    fsm_data = fsm.get_data(who)
    if state != EditSenderState.WAIT_INPUT_PHONE:
        return
    main_event = fsm_data['main_event']
    userbot = fsm_data['userbot']   
    phone = event.message.message 
    try: 
        await userbot.send_code_request(phone) 
        text = 'В телеграм вам пришел код (не СМС). Введите его в формате ХХ-ХХХ\n' 
        text += 'Дефис добавьте обязательно. Иначе код не примется' 
        await main_event.edit(text, buttons = [btn_cancel]) 
        fsm_data['phone'] = phone
        fsm.set_state(who, EditSenderState.WAIT_INPUT_CODE)
        fsm.set_data(who,fsm_data)       
    except Exception as e:
        text = f'{e}. Введите телефон заново в виде +7ХХХХХХХХХХ\n'
        text+= f'Вы ввели: {phone}' 

        await main_event.edit(text, buttons = [btn_cancel]) 
    raise StopPropagation #Останавливает дальнейшую обработку

@errors_catching_async
async def send_code(event: events.NewMessage):
    await bot.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
    who = event.sender_id
    state = fsm.get_state(who)
    fsm_data = fsm.get_data(who)
    if state != EditSenderState.WAIT_INPUT_CODE:
        return
    param = fsm_data['param'] 
    poster = bot.posters[fsm_data['poster_id']] 
    main_event = fsm_data['main_event']
    userbot = fsm_data['userbot']
    phone = fsm_data['phone']    
    code = event.message.message.replace('-', '')
    try: 
        me = await userbot.sign_in(phone, code)
        text = 'Идет рассыылка. Ожидайте' 
        await main_event.edit(text)         
        err_text = await post_advertisement(userbot, poster)     
    except Exception as e:
        err_text = f'\n{e}\n<b>Что-то пошло не так. Попробуйте сначала</b>' 

    text = str(poster)
    text += "\nНажмите кнопку для изменения параметра\n"
    text += err_text
    await main_event.edit(text, buttons = get_poster_btns(poster))
    fsm.set_state(who, EditSenderState.WAIT_COMMAND)     
    raise StopPropagation #Останавливает дальнейшую обработку

@errors_catching_async
async def cancel_update_param(event: events.CallbackQuery):
    who = event.sender_id
    state = fsm.get_state(who)
    fsm_data = fsm.get_data(who)   
    states =  [EditSenderState.WAIT_INPUT_PARAM, EditSenderState.WAIT_INPUT_PHONE, EditSenderState.WAIT_INPUT_CODE]
    if state in states:
        poster = bot.posters[fsm_data['poster_id']]
        text = str(poster)
        text += "\nНажмите кнопку для изменения параметра"
        await event.edit(text, buttons = get_poster_btns(poster))
        fsm.set_state(who, EditSenderState.WAIT_COMMAND)    
        raise StopPropagation

@errors_catching
def register_handlers():
    bot.add_event_handler(manage_poster_click, events.CallbackQuery(pattern='^poster-'))
    bot.add_event_handler(change_poster_param, events.CallbackQuery(pattern='^poster_'))
    bot.add_event_handler(back_to_start, events.CallbackQuery(pattern='^back$'))
    bot.add_event_handler(cancel_update_param, events.CallbackQuery(pattern='^cancel$'))
    bot.add_event_handler(update_param, events.NewMessage(chats=bot.config.admins, incoming=True))
    bot.add_event_handler(send_phone, events.NewMessage(chats=bot.config.admins, incoming=True))  
    bot.add_event_handler(send_code, events.NewMessage(chats=bot.config.admins, incoming=True))  


async def post_advertisement(userbot: TelegramClient, poster: PosterConfig):

    pass