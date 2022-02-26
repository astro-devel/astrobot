import os
from time import sleep
import sqlalchemy
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

db = sqlalchemy.create_engine(
    os.environ["DATABASE_URL"], future=True, pool_pre_ping=True
)
_base = declarative_base()


class SpotifyUserToken__Obj(_base):
    __tablename__ = "spotify_users"

    user_id = Column(String, primary_key=True)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(String)
    default_device_id = Column(String, nullable=True)


Session = sqlalchemy.orm.sessionmaker(db, future=True)
session: sqlalchemy.orm.Session = Session()

while True:
    try:
        _base.metadata.create_all(db)
        break
    except sqlalchemy.exc.DBAPIError:
        print("Could not connect to the database, is it on? Retrying in 5 seconds...")
        sleep(5)
