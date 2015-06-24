__author__ = 'Robin'
import pandas as pd
from .utils import get_fields_df

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

MAX_IMPORT_ROWS = 50000000000000


def raw_importer_data_to_database_old(file_path):
    #Text file is split - first line is a header records (not column names)
    #Middle records are the data
    #Final record is also different

    with open(file_path) as fh:
        lines = fh.readlines()
        header_record = lines[0]
        middle_records =  lines[1:-1]
        tail_record = lines[-1]

    #Header record
    #The specification of the header record from https://www.uktradeinfo.com/Statistics/Documents/Tech_Spec_SMKE19.DOC
    header_record_specs = pd.read_csv("specs/importers_header_record_specs.csv")
    header_record_specs = get_fields_df(header_record_specs)


    header_record_dict = {}
    for row in header_record_specs.iterrows():
        r = row[1]
        key = r["Item Name"]
        value = header_record[r["From"]-1:r["To"]].strip()
        header_record_dict[key] = value

    header_record_df = pd.DataFrame([header_record_dict])
    header_record_df.columns = [c.lower().replace("-","_") for c in header_record_df.columns]
    write_header_record_to_db(header_record_df)




    #Middle records - this is the bulk of the data

    middle_record_specs = pd.read_csv("specs/importers_middle_record_specs.csv")
    middle_record_specs = get_fields_df(middle_record_specs)

    middle_record_specs_dict = middle_record_specs.to_dict(orient="records")

    middle_records_df = pd.DataFrame(middle_records,columns=["all"])

    for col in middle_record_specs_dict:
        middle_records_df[col["Item Name"]] = middle_records_df["all"].str.slice(col["From"]-1,col["To"])
    middle_records_df = middle_records_df.drop(["all"],axis=1)
    middle_records_df.columns = [c.lower().replace("-","_") for c in middle_records_df.columns]

    write_middle_records_to_db(middle_records_df)


def raw_importer_data_to_database(zipfile,url_info):
    #Text file is split - first line is a header records (not column names)
    #Middle records are the data
    #Final record is also different


    with zipfile.open(url_info["file_name"]) as fh:
        lines = fh.readlines()
        header_record = lines[0].decode("windows-1252")
        middle_records = [l.decode("windows-1252") for l in lines[1:-1]]
        tail_record = lines[-1].decode("windows-1252")

    #Header record
    #The specification of the header record from https://www.uktradeinfo.com/Statistics/Documents/Tech_Spec_SMKE19.DOC
    header_record_specs = pd.read_csv("specs/importers_header_record_specs.csv")
    header_record_specs = get_fields_df(header_record_specs)


    header_record_dict = {}
    for row in header_record_specs.iterrows():
        r = row[1]
        key = r["Item Name"]
        value = header_record[r["From"]-1:r["To"]].strip()
        header_record_dict[key] = value

    header_record_df = pd.DataFrame([header_record_dict])
    header_record_df.columns = [c.lower().replace("-","_") for c in header_record_df.columns]
    write_header_record_to_db(header_record_df)








    #Middle records - this is the bulk of the data

    middle_record_specs = pd.read_csv("specs/importers_middle_record_specs.csv")
    middle_record_specs = get_fields_df(middle_record_specs)

    middle_record_specs_dict = middle_record_specs.to_dict(orient="records")

    middle_records_df = pd.DataFrame(middle_records,columns=["all"])

    for col in middle_record_specs_dict:
        middle_records_df[col["Item Name"]] = middle_records_df["all"].str.slice(col["From"]-1,col["To"])
    middle_records_df = middle_records_df.drop(["all"],axis=1)
    middle_records_df.columns = [c.lower().replace("-","_") for c in middle_records_df.columns]

    write_middle_records_to_db(middle_records_df, url_info["month"], url_info["year"])




from my_models import Importer, ImporterHeader,ImporterEightDigitCodes
from my_database import session

def write_header_record_to_db(df):
    for row in df.iterrows():
        r = row[1]

        ihr = ImporterHeader()

        ihr.ia_runno = r["ia_runno"]
        ihr.ia_year = r["ia_year"]

        session.add(ihr)
    session.commit()

def write_middle_records_to_db(df,month, year):

    counter = 0
    for row in df[:MAX_IMPORT_ROWS].iterrows():

        counter +=1
        if counter % 500 == 0:
            logger.debug("processed {} records".format(counter))

        r = row[1]

        try:
            i = session.query(Importer).filter(Importer.ia_name == r["ia_name"]) \
                          .filter(Importer.ia_addr_1 == r["ia_addr_1"]) \
                          .filter(Importer.ia_addr_2 == r["ia_addr_2"]) \
                          .filter(Importer.ia_addr_3 == r["ia_addr_3"]) \
                          .filter(Importer.ia_addr_4 == r["ia_addr_4"]) \
                          .filter(Importer.ia_addr_5 == r["ia_addr_5"]) \
                          .filter(Importer.ia_pcode == r["ia_pcode"]) \
                          .one()

        except NoResultFound:

            i = Importer()

            i.ia_record_type = r["ia_record_type"]
            i.ia_name = r["ia_name"]
            i.ia_addr_1 = r["ia_addr_1"]
            i.ia_addr_2 = r["ia_addr_2"]
            i.ia_addr_3 = r["ia_addr_3"]
            i.ia_addr_4 = r["ia_addr_4"]
            i.ia_addr_5 = r["ia_addr_5"]
            i.ia_pcode = r["ia_pcode"]
            # i.ia_comcode_count = r["ia_comcode_count"]
            # i.ia_comcode = r["ia_comcode"]

            session.add(i)

        except MultipleResultsFound:
            logger.debug("Error, multiple results found for importer {} {} {} ".format(r["ia_name"],r["ia_addr_1"],r["ia_addr_2"]))



        write_importer_comcodes_to_db(i,r, month, year)

    session.commit()


def write_importer_comcodes_to_db(importer, row, month, year):

    comcodes = row["ia_comcode"]
    comcodes = comcodes.split("|")
    comcodes = [c.strip() for c in comcodes if len(c) > 6]

    for c in comcodes:

        ics = ImporterEightDigitCodes()
        ics.impoter = importer
        ics.comcode8 = c
        ics.month_of_import = month
        ics.year_of_import = year

        session.add(ics)





