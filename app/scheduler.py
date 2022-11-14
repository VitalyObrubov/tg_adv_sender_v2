from scheduler.asyncio import Scheduler
# import pytz, datetime
# from app.globals import Bot, bot

class BotScheduler(Scheduler):
    def __init__(self, *args, **kwargs):
        pass
    
    async def update_jobs(self):
        self.delete_jobs()
        # for poster in bot.posters:
        #     for time in poster.schedule:
        #         datetime.datetime.strptime(time, "%H:%M")