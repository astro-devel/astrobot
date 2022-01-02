import os
import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

import sqlalchemy
from sqlalchemy import Column, String, Integer, JSON, PickleType, Sequence
from sqlalchemy.ext.declarative import declarative_base

db = sqlalchemy.create_engine(os.environ["DATABASE_URL"], future=True)
_base = declarative_base()

class UserMod__Obj(_base):
    __tablename__ = 'user_moderation'

    user_id = Column(String, primary_key=True)
    guild_id = Column(String)
    ban_count = Column(Integer)
    kick_count = Column(Integer)
    warn_count = Column(Integer)
    mute_count = Column(Integer)

class CommandLog__Obj(_base):
    __tablename__ = 'command_logs'

    id = Column(Integer, Sequence('command_logs_seq'), primary_key=True)
    user_id = Column(String)
    timestamp = Column(String)
    command = Column(PickleType)

Session = sqlalchemy.orm.sessionmaker(db, future=True)  
session: sqlalchemy.orm.Session = Session()

_base.metadata.create_all(db)