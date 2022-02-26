import os
from time import sleep
import sqlalchemy
from sqlalchemy import Column, Sequence, String, Integer, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base

db = sqlalchemy.create_engine(
    os.environ["DATABASE_URL"], future=True, pool_pre_ping=True
)
_base = declarative_base()


class GuildUser__Obj(_base):
    __tablename__ = "guild_user_obj"

    id = Column(Integer, Sequence("guild_user_obj_sequence"), primary_key=True)
    user_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    moderation_info = Column(JSON)

    @classmethod
    def blank_obj(cls, user_id, guild_id):
        return cls(
            user_id=user_id,
            guild_id=guild_id,
            moderation_info={"warn": 0, "ban": 0, "kick": 0, "mute": 0},
        )


class BugItem_DB(_base):
    __tablename__ = "astro_bugs"

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

while True:
    try:
        _base.metadata.create_all(db)
        break
    except sqlalchemy.exc.DBAPIError:
        print("Could not connect to the database, is it on? Retrying in 5 seconds...")
        sleep(5)
