from asyncio import futures
import os
import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

import sqlalchemy
from sqlalchemy import Table, Column, String, MetaData, Integer
from sqlalchemy.ext.declarative import declarative_base

_db = sqlalchemy.create_engine(os.environ["DATABASE_URL"], future=True)
_base = declarative_base()

class BugItem_DB(_base):
    __tablename__ = 'astro_bugs'

    reporter = Column(Integer)
    description = Column(String)
    bot_version = Column(String)
    screenshot_url = Column(String)
    status = Column(String)
    assigned_to = Column(Integer)
    bug_id = Column(String, primary_key=True)

Session = sqlalchemy.orm.sessionmaker(_db, future=True)  
session: sqlalchemy.orm.Session = Session()


_base.metadata.create_all(_db)

class DatabaseStuffs(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot