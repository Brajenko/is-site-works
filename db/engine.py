from sqlalchemy import create_engine
from sqlalchemy.orm import create_session, Session

from .models import Base
import config

connection_string = f'mysql+mysqlconnector://{config.mysql_username}:{config.mysql_password}@{config.mysql_hostname}/{config.mysql_name}'
engine = create_engine(connection_string)

Base.metadata.create_all(engine)


def session_create() -> Session:
    return create_session(bind=engine)
