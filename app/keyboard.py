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
    debug = 'Выкл.' if poster.debug else 'Вкл.'
    btns = []
    btns.append([Button.inline('🖅Название рассылки', 'poster_name'),
                 Button.inline('❌Удалить рассылку', 'poster_del')])
    btns.append([Button.inline('🗎Скопировать рассылку', 'poster_copy')])
    btns.append([Button.inline('🔍Фраза поиска списка', 'poster_list'),
                 Button.inline('🔎Фраза поиска рекламы', 'poster_adv')])
    btns.append([Button.inline('🔗Группа с рекламой', 'poster_link'),
                 Button.inline('⏰Расписание рассылки', 'poster_schedule')])
    btns.append([Button.inline(f'🛠{debug} отладку', 'poster_debug'),
                 Button.inline('✏Группа для отчетов', 'poster_recieverchange')])
    btns.append([Button.inline('▶Запустить разово', 'poster_start')])             
    btns.append([btn_back])
    return btns

def get_bot_adm_btns(curr_user_link: str):
    btns = []
    for id, admin in enumerate(bot.config.admins):
        if curr_user_link == admin:
            continue
        btns.append([Button.inline('❌' + admin, f'admin_del-{id}')])
    btns.append([Button.inline('🆕Добавить администратора', 'admin_add')])
    btns.append([Button.inline('💓Активировать бота', 'activate_bot')])
    btns.append([btn_back])
    return btns

btn_back = Button.inline('⬅Назад', 'back')
btn_cancel = Button.inline('🗙Отмена', 'cancel')
btn_phone = Button.request_phone('Отправить телефон', resize=True, single_use=True)