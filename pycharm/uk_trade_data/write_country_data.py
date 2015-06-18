__author__ = 'Robin'


from my_models import Country, Port
from my_database import session
import pandas as pd

def download_and_insert_country_data():
    #Create table of countries and their ISO equivalents

    url = "https://www.uktradeinfo.com/CodesAndGuides/Documents/Country_alpha.xls"
    df = pd.read_excel(url)

    df.fillna("")

    for row in df.iterrows():

        r = row[1]
        c = Country()
        c.country_name = r["Country Name"]
        c.alpha_code = r["Alpha Code"]
        c.sequence_code = r["Sequence Code"]
        c.comments = r["Comments"]

        session.add(c)

    session.commit()

def download_and_insert_port_data():
    url = "https://www.uktradeinfo.com/CodesAndGuides/Documents/Port_codes.xls"
    df_air = pd.read_excel(url, "Airport codes")
    df_sea = pd.read_excel(url, "Seaport codes")
    df_air = df_air[["Name", "Alpha Code","Sequence Code"]]
    df_sea = df_sea[["Name", "Alpha Code","Sequence Code"]]
    df = pd.concat([df_air, df_sea])
    df["Name"] = df["Name"].str.title()

    df.fillna("")

    for row in df.iterrows():
        r = row[1]
        p = Port()
        p.port_name = r["Name"]
        p.alpha_code = r["Alpha Code"]
        p.sequence_code = r["Sequence Code"]

        session.add(p)

