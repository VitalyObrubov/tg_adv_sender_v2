from telethon import events
from telethon.tl.custom import Button
from telethon.events import StopPropagation

from app.globals import Bot, bot
from app.fsm import *
from app.logger import errors_catching, errors_catching_async
from app.keyboard import get_posters_btns
from app.handlers.poster_handlers import register_handlers as register_handlers_posters
from app.handlers.admin_handlers import register_handlers as register_handlers_admins

@errors_catching_async
async def start(event: events.NewMessage):
    bot.save_bot_config()
    who = event.sender_id
    fsm.set_state(who, CommonState.WAIT_ON_START)
    await bot.delete_messages(entity=event.chat_id, message_ids=[event.message.id])
    await event.respond('Вас приветствует бот управления рассылками',  buttons = get_posters_btns(), link_preview = False)
    raise StopPropagation #Останавливает дальнейшую обработку


async def unknown_callback(event: events.CallbackQuery):
    await event.respond('Unknown clicking {}!'.format(event.data))

async def unknown_message(event: events.NewMessage):
    await event.respond('Неизвестная команда')
    raise StopPropagation

@errors_catching
def register_handlers():
    register_handlers_posters()
    register_handlers_admins() 
    bot.add_event_handler(start, events.NewMessage(chats=bot.config.admins, incoming=True, pattern='/start'))
    # Обрабатывает нераспознаные события, должен быть последним в списке
    bot.add_event_handler(unknown_message, events.NewMessage(chats=bot.config.admins, incoming=True)) 
    bot.add_event_handler(unknown_callback, events.CallbackQuery)