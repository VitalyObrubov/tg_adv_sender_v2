from telethon.tl.custom import Button
from app.globals import Bot, bot, PosterConfig


def get_posters_btns():
    btns = []
    for id, poster in enumerate(bot.posters):
        btns.append([Button.inline('🖅' + poster.name, f'poster-{id}')])
    btns.append([Button.inline('🆕Добавить рассылку', 'poster-add')])
    btns.append([Button.inline('🛠Настройки бота', 'manage_bot')])
    return btns

def get_poster_btns(poster: PosterConfig):
    reports = "не получать" if poster.recieve_reports else "получать"
    debug = '"выкл."' if poster.debug else '"вкл."'
    btns = []
    btns.append([Button.inline('🖅Название рассылки', 'poster_name'),
                 Button.inline('❌Удалить рассылку', 'poster_del')])
    btns.append([Button.inline('🔍Фраза поиска списка', 'poster_list'),
                 Button.inline('🔎Фраза поиска рекламы', 'poster_adv')])
    btns.append([Button.inline('🔗Ссылка на группу', 'poster_link'),
                 Button.inline('⏰Расписание рассылки', 'poster_schedule')])
    btns.append([Button.inline(f'🛠Отладка {debug}', 'poster_debug'),
                 Button.inline(f'📝Отчеты {reports}', 'poster_report')])
    btns.append([Button.inline('▶Запустить рассылку', 'poster_start')])             
    btns.append([btn_back])
    return btns

def get_bot_adm_btns(curr_user_link: str):
    btns = []

    for id, admin in enumerate(bot.config.admins):

        if curr_user_link == admin:
            continue
        btns.append([Button.inline('❌' + admin, f'admin_del-{id}')])

    btns.append([Button.inline('🆕Добавить администратора', 'admin_add')])
    btns.append([Button.inline('✏Изменить получателя отчетов', 'reciever_change')])
    btns.append([btn_back])
    return btns

btn_back = Button.inline('⬅Назад', 'back')
btn_cancel = Button.inline('🗙Отмена', 'cancel')
btn_phone = Button.request_phone('Отправить телефон', resize=True, single_use=True)