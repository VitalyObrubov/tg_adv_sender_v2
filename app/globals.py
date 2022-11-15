import os, yaml, asyncio
from telethon import TelegramClient
from telethon.tl.types import User as tgUser
from app.scheduler import BotScheduler
class Bot(TelegramClient):
    config: "BotConfig"
    posters: list["PosterConfig"]
    userbot: TelegramClient
    userbot_fio: str
    me: tgUser
    scheduler: BotScheduler
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
    
    def add_poster(self):
        self.posters.append(PosterConfig())
        self.save_poster_config()

    def save_poster_config(self):
        # Меняем значения конфиг. файла.
        posters = [{f"poster{index}":vars(poster)} for index,poster in enumerate(self.posters)]
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
    def __init__(self, poster = None) -> None:
        if poster:
            self.name = poster.get("name")
            self.group_list_keyword = poster.get("group_list_keyword")
            self.adv_post_keyword = poster.get("adv_post_keyword")
            self.debug = poster.get("debug")
            self.sending_on = poster.get("sending_on")
            self.group_link = poster.get("group_link")
            self.schedule = {time:None for time in poster["schedule"]}
            self.report_reciever = poster.get("report_reciever")
        else:
            self.name = "Рассылка ХХХ"
            self.group_list_keyword = "Ввести фразу поиска"
            self.adv_post_keyword = "Ввести фразу поиска"
            self.debug = 0
            self.sending_on = 0
            self.group_link = "Ссылка на группу"
            self.schedule = {} 
            self.report_reciever = "Ссылка на группу"           
    
    def __str__(self) -> str:
        res = f'Рассылка: "{self.name}"\n'
        res += f'Поиск списка по: "{self.group_list_keyword}"\n'
        res += f'Поиск рекламы по: "{self.adv_post_keyword}"\n'
        res += f'Ссылка на группу с рекламой: "{self.group_link}"\n'
        schedule = ', '.join(self.schedule)
        res += f'Время рассылки: "{schedule}"\n'
        res += f'Получатель отчетов: "{self.report_reciever}"\n'
        debug = 'вкл.' if self.debug else 'выкл.'
        res += f'Отладка: "{debug}"\n'
        return res

bot = Bot()
bot.parse_mode = 'HTML'



