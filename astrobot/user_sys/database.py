import os
import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

import sqlalchemy
from sqlalchemy import Table, Column, String, MetaData, Integer, BigInteger, Boolean, JSON
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

class MutedUsers__Obj(_base):
    __tablename__ = 'muted_users'

    timestamp = Column(String)
    unmute_at = Column(String)
    user_id = Column(String, primary_key=True)
    guild_id = Column(String)
    roles = Column(JSON)
    

class CommandLog__Obj(_base):
    __tablename__ = 'command_logs'

    user_id = Column(String, primary_key=True)
    timestamp = Column(String)
    command = Column(JSON)

Session = sqlalchemy.orm.sessionmaker(db, future=True)  
session: sqlalchemy.orm.Session = Session()

_base.metadata.create_all(db)