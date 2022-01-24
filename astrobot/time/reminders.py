import time
from typing import Optional
import sqlalchemy
import discord
from discord.ext import commands
from astrobot.colors import MochjiColor
from astrobot import util
from . import database as db
from .timers import RemindersTimer

class Reminders(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: discord.Bot = bot
        self.emojis = None
    
    @staticmethod
    async def send_reminder(bot: discord.Bot, channel_id: int, member_id: int, reminder: str, timer: RemindersTimer=None, secs_late: Optional[int]=None):
        channel = await bot.fetch_channel(channel_id)
        apology = str()
        if secs_late:
            apology += f"(late by {secs_late} seconds) Sorry about that :("
        embed = discord.Embed(
            title=reminder,
            color=MochjiColor.white()
        )
        await channel.send(f"<@!{member_id}>, here's your reminder! {apology}", embed=embed)
        
        if timer:
            bot.remindme_timers[member_id].remove(timer)

        db.session.execute(
            sqlalchemy.delete(db.Reminders).where(db.Reminders.reminder_text == reminder).execution_options(synchronize_session="fetch")
        )
        db.session.commit()
        return
    
    @commands.command()
    async def remindme(self, ctx, remind_at: str, *, reminder: str):

        # create reminder timer
        seconds_until_reminder = util.convert_time(remind_at)[0]
        timer = RemindersTimer(seconds_until_reminder, self.send_reminder, self.bot, ctx.channel.id, ctx.author.id, reminder, reminder_text=reminder)
        self.bot.remindme_timers[ctx.author.id].append(timer)

        # add reminder to database
        db.session.add(db.Reminders(
            user_id=ctx.author.id.__str__(),
            channel_id=ctx.channel.id.__str__(),
            remind_at=(int(time.time()) + seconds_until_reminder).__str__(),
            reminder_text=reminder
        ))
        db.session.commit()

        await ctx.send(embed=discord.Embed(
            title=f"{self.emojis.success} Got it! Will remind you about: ***'{reminder}'*** on <t:{timer.expires_at}>"
        ))
        return
    
    @commands.command()
    async def reminders(self, ctx, *, args: str=None):
        if args:
            args = args.split()
        if args[0] == "list" or not args:
            timer_list = str()
            for timer in self.bot.remindme_timers[ctx.author.id]:
                timer_list += f"\'{timer.reminder_text}\' <t:{timer.expires_at}>\n"
            await ctx.send(embed=discord.Embed(
                title=f"Active reminders for {ctx.author}",
                description=timer_list
            ))
        elif args[0] == "delete" or args[0] == "del":
            item_to_delete = self.bot.remindme_timers[ctx.author.id][int(args[1]) - 1]
            item_to_delete.cancel()
            db.session.execute(
                sqlalchemy.delete(db.Reminders).where(db.Reminders.reminder_text == item_to_delete.reminder_text).execution_options(synchronize_session="fetch")
            )
            db.session.commit()
            self.bot.remindme_timers[ctx.author.id].pop(int(args[1]) - 1)
            await ctx.send(embed=discord.Embed(
                title=f"{self.emojis.success} **Successfully deleted timer!**"
            ))
        else:
            raise Exception(f"Command '{' '.join(args)}' not recognized...")
        return
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.emojis = self.bot.get_cog('MochjiMojis')