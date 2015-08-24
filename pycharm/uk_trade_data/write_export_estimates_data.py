__author__ = 'Robin'
import pandas as pd
from .utils import get_fields_df
import trade_data_config


import logging
logger = logging.getLogger(__name__)


from .utils import get_fields_df, get_zipped_file_contents, get_specs_dict, build_from_spec
from my_database import engine
from my_models import Export_Estimate
from my_database import session

def raw_export_estimates_data_to_db(zipfile, url_info,rawfile):
    
    #Get dict of the contents of the file - including header record, filename etc
    contents = get_zipped_file_contents(zipfile)
    middle_records_specs_dict = get_specs_dict("specs/estimates_middle_record_specs.csv")
    middle_records_df = build_from_spec(contents["middle_records"], middle_records_specs_dict)

    rawfile.actual_file_name_in_child_zip = contents["actual_file_name_in_child_zip"]

    write_middle_records_to_db(middle_records_df,rawfile, middle_records_specs_dict)

    rows = session.query(Export_Estimate).count()
    logger.debug('there are now {} records in the export table'.format(rows))


def write_middle_records_to_db(df,rawfile, specs_dict):

    rows_dict = df[:trade_data_config.MAX_IMPORT_ROWS].to_dict(orient='records')

    for row in rows_dict:
        row["source_file_id"] = rawfile.id
        row["estimated_value_int"] = int(row["estimated_value"])


    engine.execute(
        Export_Estimate.__table__.insert(),
        rows_dict
    )