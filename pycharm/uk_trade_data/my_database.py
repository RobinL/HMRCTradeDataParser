from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc

p = r"trade_data.db"
engine = create_engine('sqlite:///' + p)

DBSession = sessionmaker(bind=engine)
session = DBSession()

Base = declarative_base()

#Note this just creates the databse, it isn't needed if it already exists
def init_db(remove=True):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    import os
    try:
        if remove:
            os.remove(p)
    except:
        pass
    import my_models
    Base.metadata.create_all(bind=engine)

from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()