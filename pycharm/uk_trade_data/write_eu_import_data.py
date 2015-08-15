__author__ = 'Robin'
import pandas as pd
from .utils import get_fields_df, get_zipped_file_contents, get_specs_dict, build_from_spec
from my_database import engine


import trade_data_config
import logging
logger = logging.getLogger(__name__)



def raw_eu_import_data_to_database(zipfile, url_info,rawfile):


    #Get dict of the contents of the file - including header record, filename etc
    contents = get_zipped_file_contents(zipfile)
    middle_records_specs_dict = get_specs_dict("specs/eu_import_middle.csv")
    middle_records_df = build_from_spec(contents["middle_records"], middle_records_specs_dict)

    rawfile.actual_file_name_in_child_zip = contents["actual_file_name_in_child_zip"]

    write_middle_records_to_db(middle_records_df,rawfile, middle_records_specs_dict)

    rows = session.query(Import_EU).count()
    logger.debug("there are now {} records in the eu_import table".format(rows))


from my_models import Import_EU
from my_database import session




def write_middle_records_to_db(df,rawfile, specs_dict):

    rows_dict = df[:trade_data_config.MAX_IMPORT_ROWS].to_dict(orient="records")
    for row in rows_dict:
        row["smk_stat_value_int"]   = int(row["smk_stat_value"])
        row["smk_nett_mass_int"]    =  int(row["smk_nett_mass"])
        row["smk_no_of_consignments_int"] = int(row["smk_no_of_consignments"])
        row["smk_supp_unit_int"] = int(row["smk_supp_unit"])
        row["source_file_id"] = rawfile.id

    engine.execute(
        Import_EU.__table__.insert(),
        rows_dict
    )

    

