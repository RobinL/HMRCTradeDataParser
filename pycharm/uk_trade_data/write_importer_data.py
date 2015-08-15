__author__ = 'Robin'
import pandas as pd
from .utils import get_fields_df

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .utils import get_fields_df, get_zipped_file_contents, get_specs_dict, build_from_spec
import trade_data_config

from my_models import Importer, ImporterEightDigitCodes
from my_database import session, engine
import hashlib

import logging
logger = logging.getLogger(__name__)


def raw_importer_data_to_database(zipfile, url_info,rawfile):
    
    #Get dict of the contents of the file - including header record, filename etc
    contents = get_zipped_file_contents(zipfile)
    middle_records_specs_dict = get_specs_dict("specs/importers_middle_record_specs.csv")
    middle_records_df = build_from_spec(contents["middle_records"], middle_records_specs_dict)
    rawfile.actual_file_name_in_child_zip = contents["actual_file_name_in_child_zip"]

    write_middle_records_to_db(middle_records_df, url_info["month"], url_info["year"], rawfile)

    rows = session.query(Importer).count()
    logger.debug("there are now {} records in the importer table".format(rows))


def write_middle_records_to_db(df,month, year,rawfile):

    counter = 0

    #Get a table of all the hashes that are already in the database
    existing_hashes = session.query(Importer.importer_hash, Importer.id).all()

    hashes_dict = {c[0]:c[1] for c in existing_hashes}

    importer_comcodes_bulk_insert_list = []


    for row in df[:trade_data_config.MAX_IMPORT_ROWS].iterrows():

        counter +=1
        if counter % 500 == 0:
            logger.debug("processed {} records".format(counter))
            session.flush()

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
            new_inserts = get_importer_comcodes_bulk_insert_dict(importer_id,r, month, year,rawfile)
            importer_comcodes_bulk_insert_list += new_inserts
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

            i.postcode_nospace = r["ia_pcode"].strip().replace(' ','')

            i.importer_hash = this_hash

            i.rawfile = rawfile

            session.add(i)
            session.flush()
            importer_id = i.id
            hashes_dict[this_hash] = importer_id

            new_inserts = get_importer_comcodes_bulk_insert_dict(importer_id,r, month, year,rawfile)
            importer_comcodes_bulk_insert_list += new_inserts

    session.commit()

    engine.execute(
        ImporterEightDigitCodes.__table__.insert(),
        importer_comcodes_bulk_insert_list
    )



def get_importer_comcodes_bulk_insert_dict(importer_id, row, month, year, rawfile):

    comcodes = row["ia_comcode"]
    comcodes = comcodes.split("|")
    comcodes = [c.strip() for c in comcodes if len(c) > 6]

    add_to_db_list = []
    template_dict = {"importer_id": importer_id,
                     "month_of_import": month,
                     "year_of_import": year,
                     "source_file_id": rawfile.id}

    for c in comcodes:
        template_dict["comcode8"] = c
        add_to_db_list.append(template_dict)

    return add_to_db_list