from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



p = r"C:\Users\Robin\Desktop\trade_data\trade_data.db"



import urllib

params = urllib.quote_plus('DRIVER={SQL Server};SERVER=.\SQLEXPRESS;DATABASE=TRADEDATA;Trusted_Connection=Yes')
engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
#engine = create_engine('mssql+pyodbc://SQLEXPRESS/TRADEDATA;Trusted_Connection=Yes')

#engine = create_engine('sqlite:///' + p)

DBSession = sessionmaker(bind=engine)
session = DBSession()

Base = declarative_base()


#Note this just creates the databse, it isn't needed if it already exists
def init_db(remove=False):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    import os
    if remove:
        os.remove(p)
    import my_models
    Base.metadata.create_all(bind=engine)




