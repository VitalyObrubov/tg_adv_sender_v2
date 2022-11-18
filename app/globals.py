import os, yaml
from telethon import TelegramClient
from telethon.tl.types import User as tgUser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

MoscowZone=pytz.timezone('Europe/Moscow')
class Bot(TelegramClient):
    config: "BotConfig"
    posters: list["PosterConfig"]
    userbot: TelegramClient
    userbot_fio: str
    me: tgUser
    scheduler: 'BotScheduler'
    def __init__(self, *args, **kwargs):        
        self.me = None
        self.userbot = None
        self.userbot_fio = None
        self.config = BotConfig()
        config_path = 'config/posters_config.yaml'
        with open(config_path, "r") as f:
            raw_config = yaml.safe_load(f)

        self.posters = []
        for poster in raw_config:
            self.posters.append(PosterConfig(list(poster.values())[0]))

        super().__init__('config/session_name_bot',self.config.api_id,self.config.api_hash)
    
    async def userbot_is_autorised(self):
        if await self.userbot.is_user_authorized():   
            res = "\nБот авторизацию прошел"
        else:
            res = "\nБот авторизацию не прошел" 
        return res       
    
    def __str__(self) -> str:
        res = f'Настройки бота:"\n'
        res += f"Отправка осуществляется от имени '{self.userbot_fio}'\n" 
        res += str(self.config)
        res += f"\nBot username: @{bot.me.username}"
        res += f"\nBot name: {bot.me.first_name}"         
        return res
    
    def add_poster(self, old_poster: "PosterConfig" = None):
        self.posters.append(PosterConfig(old_poster))
        self.save_poster_config()

    def save_poster_config(self):
        # Меняем значения конфиг. файла.
        posters_copy =[]
        for poster in self.posters:
            poster_copy = PosterConfig(poster, new = False)
            poster_copy.cronjob = None
            posters_copy.append(poster_copy)

        posters = [{f"poster{index}":vars(poster)} for index,poster in enumerate(posters_copy)]
        with open(r'config/posters_config.yaml', 'w', encoding="utf-8") as file: 
            yaml.dump(posters, file, indent=4, default_flow_style=False, allow_unicode=True)
    
    def save_bot_config(self):
        # Меняем значения конфиг. файла.
        config = {"bot":vars(self.config)}
        with open(r'config/bot_config.yaml', 'w', encoding="utf-8") as file: 
            yaml.dump(config, file, indent=4, default_flow_style=False, allow_unicode=True)

    async def check_admins(self) -> bool:
        res = False
        new_admin_list = []
        for admin in self.config.admins:
            try:
                entity = await self.get_entity(admin)
                link = f'https://t.me/{entity.username}'
                new_admin_list.append(link)
            except Exception as e:
                res = True

        self.config.admins = new_admin_list
        return res

class BotConfig:
    def __init__(self) -> None:
        config_path = 'config/bot_config.yaml'
        with open(config_path, "r") as f:
            raw_config = yaml.safe_load(f)
        # Вставляем api_id и api_hash
        self.api_id = raw_config["bot"]["api_id"]
        self.api_hash = raw_config["bot"]["api_hash"]
        self.token = raw_config["bot"]["token"]
        self.admins = [admin for admin in raw_config["bot"]["admins"]]
    
    def __str__(self) -> str:
        # res = f'Настройки бота:"\n'
        # res += f'API_ID: "{self.api_id}"\n'
        # res += f'API_HASH: "{self.api_hash}"\n'
        # res += f'TOKEN: "{self.token}"\n'
        admins = '\n'.join(self.admins)
        res = f'Администраторы бота:\n{admins}\n'    
        return res

class PosterConfig:
    def __init__(self, poster = None, new = True) -> None:
        if type(poster) == dict: # Загрузка из конфига
            self.name = poster.get("name")
            self.group_list_keyword = poster.get("group_list_keyword")
            self.adv_post_keyword = poster.get("adv_post_keyword")
            self.debug = poster.get("debug")
            self.sending_on = 1 if poster.get("sending_on") else 0
            self.group_link = poster.get("group_link")
            self.schedule = poster["schedule"]
            self.report_reciever = poster.get("report_reciever")
            self.cronjob = None
        elif type(poster) == PosterConfig: # Копирование существующего
            self.name = "<b>!!!__Новая рассылка__!!!</b>" if new else  poster.name
            self.group_list_keyword = poster.group_list_keyword
            self.adv_post_keyword = poster.adv_post_keyword
            self.debug = poster.debug
            self.sending_on = poster.sending_on
            self.group_link = poster.group_link
            self.schedule = poster.schedule
            self.report_reciever = poster.report_reciever
            self.cronjob = None
        else: # Создание нового
            self.name = "<b>!!!__Новая рассылка__!!!</b>"
            self.group_list_keyword = "Ввести фразу поиска"
            self.adv_post_keyword = "Ввести фразу поиска"
            self.debug = 0
            self.sending_on = 0
            self.group_link = "Ссылка на группу"
            self.schedule = "0,20,40 * * * *"
            self.report_reciever = "Ссылка на группу"
            self.cronjob = None           
    
    def __str__(self) -> str:
        res = f'Рассылка: "{self.name}"\n'
        res += f'Поиск списка по: "{self.group_list_keyword}"\n'
        res += f'Поиск рекламы по: "{self.adv_post_keyword}"\n'
        res += f'Ссылка на группу с рекламой: "{self.group_link}"\n'        
        res += f'Время рассылки: "{self.schedule}"\n'
        res += f'Получатель отчетов: "{self.report_reciever}"\n'
        debug = 'вкл.' if self.debug else 'выкл.'
        res += f'Отладка: "{debug}"\n'
        sending = 'вкл.' if self.sending_on else 'выкл.'
        res += f'Рассылка по расписанию: "{sending}"\n'
        return res



bot = Bot()
bot.parse_mode = 'HTML'


class BotScheduler(AsyncIOScheduler):
   
    def __init__(self, *args, **kwargs):
        super().__init__()

    def update_jobs(self, func, bot: Bot):
        self.remove_all_jobs()
        for poster in bot.posters:
            shed = self.parse_string(poster.schedule)
            if shed:                      
                job = self.add_job(func,'cron', minute = shed["minute"], hour = shed["hour"], 
                                day = shed["day"], month = shed["month"], 
                                day_of_week  = shed["day_of_week"], args=(bot, poster,),misfire_grace_time=600)
                if not poster.sending_on:
                    job.pause()
                poster.cronjob = job
            else:
                poster.sending_on = 0

    def update_poster_job(self, func, poster: PosterConfig, bot: Bot):
        if poster.cronjob:
            poster.cronjob.remove()
            shed = self.parse_string(poster.schedule)
            job = self.add_job(func,'cron', minute = shed["minute"], hour = shed["hour"], 
                            day = shed["day"], month = shed["month"], 
                            day_of_week  = shed["day_of_week"], args=(bot, poster),
                            misfire_grace_time=600, name = poster.name)
            if not poster.sending_on:
                job.pause()
            poster.cronjob = job
           
    
    def parse_string(self, crontab_string: str):
        filds = ["minute","hour","day","month","day_of_week"]
        if crontab_string:
            crontab_lst = crontab_string.split()
        else:
            return False
        if len(crontab_lst) !=5:
            return False
        else:
            return dict(zip(filds,crontab_lst))
