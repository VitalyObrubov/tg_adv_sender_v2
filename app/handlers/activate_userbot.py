import logging
from app.logger import errors_catching, errors_catching_async
from app.globals import Bot, bot
from telethon import TelegramClient, events
from telethon.events import StopPropagation
from telethon.tl.functions.users import GetFullUserRequest 
from app.keyboard import *
from app.fsm import *
import pytz


@errors_catching_async
async def activate_userbot(bot: Bot, event = None, who = 1):
    fsm_data = fsm.get_data(who)
    if not await bot.userbot.is_user_authorized():
        text = 'Для авторизации введите свой телефонный номер пользователя в телеграм в формате +7ХХХХХХХХХХ' 
        admin = bot.config.admins[0]
        tmp = await bot.send_message(admin, text)       
        fsm.set_data(tmp.chat_id, fsm_data)
        fsm.set_state(tmp.chat_id,CommonState.WAIT_INPUT_PHONE)
    else:
        try: # на всякий случай
            full = await bot.userbot(GetFullUserRequest("me"))
            bot.userbot_fio = f"{full.users[0].first_name} {full.users[0].last_name} {full.users[0].username}"
        except:
            pass


@errors_catching_async
@allowed_states(CommonState.WAIT_INPUT_PHONE)
async def send_phone(event: events.NewMessage, who: int):
    await bot.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
    fsm_data = fsm.get_data(who)
    phone = event.message.message 

    try: 
        await bot.userbot.send_code_request(phone) 
        text = 'В телеграм вам пришел код (не СМС). Введите его в формате ХХ-ХХХ\n' 
        text += 'Дефис добавьте обязательно. Иначе код не примется' 
        admin = bot.config.admins[0]
        await bot.send_message(admin, text)
        fsm_data['phone'] = phone
        fsm.set_state(who, CommonState.WAIT_INPUT_CODE)
        fsm.set_data(who,fsm_data)       
    except Exception as e:
        text = f'{e}. Введите телефон заново в виде +7ХХХХХХХХХХ\n'
        text+= f'Вы ввели: {phone}' 
        admin = bot.config.admins[0]
        await bot.send_message(admin, text)
    raise StopPropagation #Останавливает дальнейшую обработку


@errors_catching_async
@allowed_states(CommonState.WAIT_INPUT_CODE)
async def send_code(event: events.NewMessage, who: int):

    await bot.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
    fsm_data = fsm.get_data(who)
    phone = fsm_data['phone']    
    code = event.message.message.replace('-', '')
    try: 
        me = await bot.userbot.sign_in(phone, code)
        full = await bot.userbot(GetFullUserRequest("me"))
        try: # на всякий случай
            bot.userbot_fio = f"{full.users[0].first_name} {full.users[0].last_name} @{full.users[0].username}"
        except:
            pass
        text = f'Подключение прошло удачно под именем "{bot.userbot_fio}"'           
    except Exception as e:
        text = f'\n{e}\n<b>Что-то пошло не так. Попробуйте сначала</b>' 

    admin = bot.config.admins[0]
    await bot.send_message(admin, text) 
    state = fsm_data['start_state'] 
    fsm.set_state(who,state)
    raise StopPropagation #Останавливает дальнейшую обработку


@errors_catching
def register_handlers():
    bot.add_event_handler(send_phone, events.NewMessage(chats=bot.config.admins, incoming=True))  
    bot.add_event_handler(send_code, events.NewMessage(chats=bot.config.admins, incoming=True)) 
