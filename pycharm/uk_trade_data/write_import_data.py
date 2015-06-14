__author__ = 'Robin'
import pandas as pd
from .utils import get_fields_df

def raw_import_data_to_database(file_path):
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
    header_record_specs = pd.read_csv("specs/import_header_record_specs.csv")
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



    #Tail record - currently I don't write this out to db as I don't know what it contains
    #Using the specification of the tail record from https://www.uktradeinfo.com/Statistics/Documents/Tech_Spec_SMKE19.DOC
    tail_record_specs = pd.read_csv("specs/import_tail_record_specs.csv")
    tail_record_specs = get_fields_df(tail_record_specs)

    tail_record_dict = {}
    for row in tail_record_specs.iterrows():
        r = row[1]
        key = r["Item Name"]
        value = tail_record[r["From"]-1:r["To"]].strip()
        tail_record_dict[key] = value

    tail_record_df = pd.DataFrame([tail_record_dict])



    #Middle records - this is the bulk of the data

    middle_record_specs = pd.read_csv("specs/import_middle_record_specs.csv")
    middle_record_specs = get_fields_df(middle_record_specs)

    middle_record_specs_dict = middle_record_specs.to_dict(orient="records")

    middle_records_df = pd.DataFrame(middle_records,columns=["all"])

    for col in middle_record_specs_dict:
        middle_records_df[col["Item Name"]] = middle_records_df["all"].str.slice(col["From"]-1,col["To"])
    middle_records_df = middle_records_df.drop(["all", "MAF-ITEM-FIELDS"],axis=1)
    middle_records_df.columns = [c.lower().replace("-","_") for c in middle_records_df.columns]

    write_middle_records_to_db(middle_records_df)



from my_models import Import, ImportHeader
from my_database import session

def write_header_record_to_db(df):
    for row in df.iterrows():
        r = row[1]

        ihr = ImportHeader()

        ihr.maf_file_name = r["maf_file_name"]
        ihr.maf_month_alpha = r["maf_month_alpha"]
        ihr.maf_suite = r["maf_suite"]
        ihr.maf_year = r["maf_year"]

        session.add(ihr)
    session.commit()

def write_middle_records_to_db(df):

    for row in df.iterrows():
        r = row[1]

        i = Import()
        i.maf_comcode = r["maf_comcode"]
        i.maf_sitc = r["maf_sitc"]
        i.maf_record_type = r["maf_record_type"]
        i.maf_cod_sequence = r["maf_cod_sequence"]
        i.maf_cod_alpha = r["maf_cod_alpha"]
        i.maf_coo_sequence = r["maf_coo_sequence"]
        i.maf_coo_alpha = r["maf_coo_alpha"]
        i.maf_account_mm = r["maf_account_mm"]
        i.maf_account_ccyy = r["maf_account_ccyy"]
        i.maf_port_sequence = r["maf_port_sequence"]
        i.maf_port_alpha = r["maf_port_alpha"]
        i.maf_flag_sequence = r["maf_flag_sequence"]
        i.maf_flag_alpha = r["maf_flag_alpha"]
        i.maf_country_sequence_coo_imp = r["maf_country_sequence_coo_imp"]
        i.maf_country_alpha_coo_imp = r["maf_country_alpha_coo_imp"]
        i.maf_trade_indicator = r["maf_trade_indicator"]
        i.maf_container = r["maf_container"]
        i.maf_mode_of_transport = r["maf_mode_of_transport"]
        i.maf_inland_mot = r["maf_inland_mot"]
        i.maf_golo_sequence = r["maf_golo_sequence"]
        i.maf_golo_alpha = r["maf_golo_alpha"]
        i.maf_suite_indicator = r["maf_suite_indicator"]
        i.maf_procedure_code = r["maf_procedure_code"]
        i.maf_cb_code = r["maf_cb_code"]
        i.maf_value = r["maf_value"]
        i.maf_quantity_1 = r["maf_quantity_1"]
        i.maf_quantity_2 = r["maf_quantity_2"]
        session.add(i)
    session.commit()




