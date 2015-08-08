__author__ = 'Robin'
import pandas as pd

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_fields_df(df, column_name = "Item Name"):
    df = df[~df[column_name].str.upper().str.contains("DELIMITER")]
    df = df[["From","To",column_name]]
    return df

def get_zipped_file_contents(zipfile):
    this_file = zipfile.filelist[0]

    try:
        with zipfile.open(this_file) as fh:
            actual_file_name_in_child_zip = this_file.filename
            lines = fh.readlines()
            header_records = [l.decode("windows-1252") for l in lines[0:1]]
            middle_records = [l.decode("windows-1252") for l in lines[1:-1]]
            tail_records = [l.decode("windows-1252") for l in lines[-1:]]  
    except:
        logger.debug("Something went wrong with opening zipile")

    return {"actual_file_name_in_child_zip" : actual_file_name_in_child_zip,
            "header_records" : header_records,
            "middle_records" : middle_records,
            "tail_records" : tail_records}


def get_specs_dict(file_path):
    #Middle records - this is the bulk of the data
    middle_record_specs = pd.read_csv(file_path)
    middle_record_specs = get_fields_df(middle_record_specs)
    middle_record_specs_dict = middle_record_specs.to_dict(orient="records")
    return middle_record_specs_dict

def build_from_spec(datalines, spec_dict):
    df = pd.DataFrame(datalines,columns=["all"])

    for col in spec_dict:
        df[col["Item Name"]] = df["all"].str.slice(col["From"]-1,col["To"])

    df.columns = [c.lower().replace("-","_") for c in df.columns]
    df = df.drop(["all"],axis=1)

    return df
