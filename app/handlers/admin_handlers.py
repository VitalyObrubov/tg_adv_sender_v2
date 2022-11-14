from telethon import events
from telethon.tl.custom import Button
from telethon.events import StopPropagation

from app.globals import Bot, bot
from app.logger import errors_catching, errors_catching_async
from app.keyboard import *
from app.fsm import *

@errors_catching_async
@allowed_states(CommonState.WAIT_ON_START)
async def manage_bot_click(event: events.CallbackQuery, who: int):
    sender_link = f'https://t.me/{event._sender.username}'
    text = f"Отправка осуществляется от имени '{bot.userbot_fio}'\n"
    text += str(bot.config)
    text += f"\nBot username: @{bot.me.username}"
    text += f"\nBot name: {bot.me.first_name}" 
    text += "\nНажмите кнопку для изменения параметра"
    await event.edit(text, buttons = get_bot_adm_btns(sender_link), link_preview = False)
    fsm.set_state(who, EditBotState.WAIT_COMMAND)
    raise StopPropagation

@errors_catching_async
@allowed_states(EditBotState.WAIT_COMMAND)
async def back_to_start(event: events.CallbackQuery, who: int):
    fsm_data = fsm.get_data(who)    
    fsm.set_state(who, CommonState.WAIT_ON_START)
    fsm_data['main_event'] = event
    fsm.set_data(who,fsm_data)
    await event.edit('Вас приветствует бот управления рассылками',  buttons = get_posters_btns())
    raise StopPropagation #Останавливает дальнейшую обработку

@errors_catching_async
@allowed_states(EditBotState.WAIT_COMMAND)
async def del_admin(event: events.CallbackQuery, who: int):
    admin_id = int(event.data.decode( "utf-8" ).split("-")[-1])
    bot.config.admins.pop(admin_id)
    bot.save_bot_config()
    text = str(bot.config.admins)
    sender_link = f'https://t.me/{event._sender.username}'
    text += "\nНажмите кнопку для изменения параметра"
    await event.edit(text, buttons = get_bot_adm_btns(sender_link), link_preview = False)
    raise StopPropagation

@errors_catching_async
@allowed_states(EditBotState.WAIT_COMMAND)
async def add_admin_click(event: events.CallbackQuery, who: int):
    fsm_data = fsm.get_data(who)     
    text = "Введите ссылку на пользователя телеграмм в формате https://t.me/username"
    await event.edit(text, buttons = [btn_cancel], link_preview = False)
    fsm_data['main_event'] = event
    fsm.set_state(who, EditBotState.WAIT_INPUT_PARAM)  
    fsm.set_data(who,fsm_data)
    raise StopPropagation

@errors_catching_async
@allowed_states(EditBotState.WAIT_INPUT_PARAM)
async def save_admin(event: events.NewMessage, who: int):
    await bot.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
    fsm_data = fsm.get_data(who)    
    main_event = fsm_data['main_event']
    value = event.message.message
    try:
        entity = await bot.get_entity(value)
    except:
        text = "<b>Введенные данные не являются ссылкой телеграмм.</b> Повторите ввод"
        try: # выдает ошибку если пытаемся отправить то же текст
            await main_event.edit(text, buttons = [btn_cancel])
        except:
            pass
        raise StopPropagation
    link = f'https://t.me/{entity.username}'          
    if not link in bot.config.admins:
        bot.config.admins.append(link)
        bot.save_bot_config()
    sender_link = f'https://t.me/{event._sender.username}'
    text = f"Отправка осуществляется от имени '{bot.userbot_fio}'\n"
    text += str(bot.config)
    text += "\nНажмите кнопку для изменения параметра"
    await main_event.edit(text, buttons = get_bot_adm_btns(sender_link), link_preview = False)
    fsm.set_state(who, EditBotState.WAIT_COMMAND)    
    raise StopPropagation

@errors_catching_async
@allowed_states(EditBotState.WAIT_INPUT_PARAM)
async def cancel_add_admin(event: events.CallbackQuery, who: int):
    text = f"Отправка осуществляется от имени '{bot.userbot_fio}'\n"
    text += str(bot.config)
    sender_link = f'https://t.me/{event._sender.username}'
    text += "\nНажмите кнопку для изменения параметра"
    await event.edit(text, buttons = get_bot_adm_btns(sender_link), link_preview = False)
    fsm.set_state(who, EditBotState.WAIT_COMMAND)
    raise StopPropagation


@errors_catching
def register_handlers():
    bot.add_event_handler(manage_bot_click, events.CallbackQuery(pattern='^manage_bot$'))
    bot.add_event_handler(del_admin, events.CallbackQuery(pattern='^admin_del-'))
    bot.add_event_handler(add_admin_click, events.CallbackQuery(pattern='^admin_add$'))
    bot.add_event_handler(back_to_start, events.CallbackQuery(pattern='^back$'))
    bot.add_event_handler(cancel_add_admin, events.CallbackQuery(pattern='^cancel$'))

    bot.add_event_handler(save_admin, events.NewMessage(chats=bot.config.admins, incoming=True)) 

