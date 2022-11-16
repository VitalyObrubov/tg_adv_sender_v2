import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz, datetime, typing, asyncio


# from app.adv_poster import adv_send 
from app.globals import Bot, PosterConfig  


class BotScheduler(AsyncIOScheduler):
   
    def __init__(self, *args, **kwargs):
        super().__init__()

    async def update_jobs(self, bot):
        pass
    #     self.delete_jobs()
    #     for poster in bot.posters:
    #         for time in poster.schedule:
    #             start_time = datetime.datetime.strptime(time, "%H:%M")
    #             job = self.daily(start_time, adv_send, args=(poster,))
    #             poster.schedule[time] = job

    async def update_poster_jobs(self, poster, schedule: list):
        pass
    #     for job in poster.schedule.values():
    #         self.delete_job(job)
    #     poster.schedule = {}
    #     for time in schedule:
    #         start_time = datetime.datetime.strptime(time, "%H:%M")
    #         job = self.daily(start_time, adv_send, args=(poster,))
    #         poster.schedule[time] = job
