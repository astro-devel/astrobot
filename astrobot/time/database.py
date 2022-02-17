import os
import sqlalchemy
from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

db = sqlalchemy.create_engine(os.environ["DATABASE_URL"], future=True, pool_pre_ping=True)
_base = declarative_base()


class Reminders(_base):
    __tablename__ = "user_reminders"

    id = Column(Integer, Sequence("user_reminders_sequence"), primary_key=True)
    user_id = Column(String)
    channel_id = Column(String)
    remind_at = Column(String)
    reminder_text = Column(String)


Session = sqlalchemy.orm.sessionmaker(db, future=True)
session: sqlalchemy.orm.Session = Session()

_base.metadata.create_all(db)
