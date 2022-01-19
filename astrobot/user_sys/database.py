import os
import sqlalchemy
from sqlalchemy import Column, String, Integer
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

class BugItem_DB(_base):
    __tablename__ = 'astro_bugs'

    timestamp = Column(String)
    reporter = Column(String)
    description = Column(String)
    reproduction_steps = Column(String)
    bot_version = Column(String)
    screenshot_url = Column(String)
    status = Column(String)
    priority = Column(String)
    assigned_to = Column(String)
    bug_id = Column(String, primary_key=True)

Session = sqlalchemy.orm.sessionmaker(db, future=True)
session: sqlalchemy.orm.Session = Session()

_base.metadata.create_all(db)