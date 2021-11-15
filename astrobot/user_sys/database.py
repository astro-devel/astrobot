import os
import discord
from discord.ext import commands
from astrobot.colors import MochjiColor

import sqlalchemy
from sqlalchemy import Table, Column, String, MetaData, Integer
from sqlalchemy.ext.declarative import declarative_base

db = sqlalchemy.create_engine(os.environ["DATABASE_URL"], future=True)
_base = declarative_base()

class UserMod__Obj(_base):
    __tablename__ = 'user_moderation'

    user_id = Column(Integer, primary_key=True)
    ban_count = Column(Integer)
    kick_count = Column(Integer)
    warn_count = Column(Integer)
    mute_count = Column(Integer)

Session = sqlalchemy.orm.sessionmaker(db, future=True)  
session: sqlalchemy.orm.Session = Session()

_base.metadata.create_all(db)