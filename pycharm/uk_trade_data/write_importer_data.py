__author__ = 'Robin'
import pandas as pd
from .utils import get_fields_df

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

MAX_IMPORT_ROWS = 1000000000





def raw_importer_data_to_database(zipfile,url_info,rawfile):
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

    write_middle_records_to_db(middle_records_df, url_info["month"], url_info["year"],rawfile)

    rows = session.query(Importer).count()
    logger.debug("there are now {} records in the importer table".format(rows))




from my_models import Importer, ImporterHeader,ImporterEightDigitCodes
from my_database import session
import hashlib

def write_header_record_to_db(df):
    for row in df.iterrows():
        r = row[1]

        ihr = ImporterHeader()

        ihr.ia_runno = r["ia_runno"]
        ihr.ia_year = r["ia_year"]

        session.add(ihr)
    session.commit()

def write_middle_records_to_db(df,month, year,rawfile):

    counter = 0

    #Get a table of all the hashes that are already in the database
    existing_hashes = session.query(Importer.importer_hash, Importer.id).all()

    hashes_dict = {c[0]:c[1] for c in existing_hashes}


    for row in df[:MAX_IMPORT_ROWS].iterrows():

        counter +=1
        if counter % 500 == 0:
            logger.debug("processed {} records".format(counter))
            session.commit()

        r = row[1]

        #First compute the hash of this record.  We will use this to see whether the importer already exists
        string_to_hash =r["ia_addr_1"] \
                        + r["ia_addr_2"] \
                        + r["ia_addr_3"] \
                        + r["ia_addr_4"] \
                        + r["ia_addr_5"] \
                        + r["ia_pcode"]

        this_hash = hashlib.sha224(string_to_hash).hexdigest()

        if this_hash in hashes_dict:
            #Still need to add what they've imported
            importer_id = hashes_dict[this_hash]

            write_importer_comcodes_to_db_id(importer_id,r, month, year,rawfile)
        else:


            #We need an in-memory list of the hash and importer ids


            i = Importer()

            i.ia_record_type = r["ia_record_type"]
            i.ia_name = r["ia_name"]
            i.ia_addr_1 = r["ia_addr_1"]
            i.ia_addr_2 = r["ia_addr_2"]
            i.ia_addr_3 = r["ia_addr_3"]
            i.ia_addr_4 = r["ia_addr_4"]
            i.ia_addr_5 = r["ia_addr_5"]
            i.ia_pcode = r["ia_pcode"]

            i.importer_hash = this_hash

            i.rawfile = rawfile
            # i.ia_comcode_count = r["ia_comcode_count"]
            # i.ia_comcode = r["ia_comcode"]

            session.add(i)
            session.flush()

            importer_id = i.id

            hashes_dict[this_hash] = importer_id


            write_importer_comcodes_to_db(i,r, month, year,rawfile)

    session.commit()


def write_importer_comcodes_to_db(importer, row, month, year,rawfile):

    comcodes = row["ia_comcode"]
    comcodes = comcodes.split("|")
    comcodes = [c.strip() for c in comcodes if len(c) > 6]

    for c in comcodes:

        ics = ImporterEightDigitCodes()
        ics.impoter = importer
        ics.comcode8 = c
        ics.month_of_import = month
        ics.year_of_import = year
        ics.rawfile = rawfile

        session.add(ics)

def write_importer_comcodes_to_db_id(importer_id, row, month, year, rawfile):

    comcodes = row["ia_comcode"]
    comcodes = comcodes.split("|")
    comcodes = [c.strip() for c in comcodes if len(c) > 6]

    for c in comcodes:

        ics = ImporterEightDigitCodes()
        ics.importer_id = importer_id
        ics.comcode8 = c
        ics.month_of_import = month
        ics.year_of_import = year
        ics.rawfile = rawfile

        session.add(ics)






