from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc


#get connection string from .env
import os
env_path = r".env"
if os.path.exists(env_path):
    for line in open(env_path):
        var = line.strip().split('=',1)
        if len(var) == 2:
            os.environ[var[0]] = var[1]

CONNECTION_STRING = os.environ.get('CONNECTION_STRING')




import urllib

#params = urllib.quote_plus('DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=TRADEDATA;Trusted_Connection=Yes')
# params = urllib.quote_plus(CONNECTION_STRING)
# engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
#engine = create_engine('mssql+pyodbc://SQLEXPRESS/TRADEDATA;Trusted_Connection=Yes')

p = r"C:\Users\Robin\Desktop\trade data working\HMRCTradeDataParser\trade_data_new_mega.db"
engine = create_engine('sqlite:///' + p)

# def connect():
#     return pyodbc.connect(CONNECTION_STRING)
# engine = sqlalchemy.create_engine('mssql://', creator=connect)


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




