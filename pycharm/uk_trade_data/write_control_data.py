__author__ = 'Robin'
import pandas as pd
from utils import get_fields_df


MAX_IMPORT_ROWS = 10

def raw_control_data_to_database(zipfile,url_info):

    filename = url_info["file_name"]

    with zipfile.open(filename) as fh:
        lines = fh.readlines()
        header_record = lines[0].decode("windows-1252")
        middle_records = [l.decode("windows-1252") for l in lines[1:-1]]
        tail_record = lines[-1].decode("windows-1252")

    #Write the control record to the database
    header_record_specs = pd.read_csv("specs/control_file_header_specs.csv")

    header_record_specs = get_fields_df(header_record_specs)

    header_record_specs = header_record_specs[header_record_specs["Item Name"].isin(["MK-FILENAME","MK-MONTH", "MK-YEAR"])]

    header_record_dict = {}
    for row in header_record_specs.iterrows():
        r = row[1]
        key = r["Item Name"]
        value = header_record[r["From"]-1:r["To"]].strip()
        header_record_dict[key] = value
    hr_df = pd.DataFrame([header_record_dict])

    #Turn into columns for database
    my_cols = list(hr_df.columns)
    my_cols = [c.lower().replace("-","_") for c in my_cols]
    hr_df.columns = my_cols

    write_header_record_to_db(hr_df)





    #Write the main data to the database
    middle_record_specs = pd.read_csv("specs/control_file_middle_specs.csv")
    middle_record_specs = get_fields_df(middle_record_specs)
    middle_record_specs_dict = middle_record_specs.to_dict(orient="records")

    #Add in the 8 digit comcode - this isn't in the spec
    middle_record_specs_dict.append({'To': 8L, 'Item Name': 'MK-COMCODE8', 'From': 1L})


    middle_records_df = pd.DataFrame(middle_records,columns=["all"])

    for col in middle_record_specs_dict:
        middle_records_df[col["Item Name"]] = middle_records_df["all"].str.slice(col["From"]-1,col["To"])

    middle_records_df = middle_records_df.drop(["all"],axis=1)

    my_cols = list(middle_records_df.columns)
    my_cols = [c.lower().replace("-","_") for c in my_cols]
    middle_records_df.columns = my_cols

    middle_records_df["mk_commodity_alpha_all"] = middle_records_df["mk_commodity_alpha_all"].str.strip()

    write_middle_records_to_db(middle_records_df)





from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


from my_models import EightDigitCode
from my_database import session
def write_middle_records_to_db(df):

    for row in df[:MAX_IMPORT_ROWS].iterrows():
        r = row[1]

        try:
            session.query(EightDigitCode).filter(EightDigitCode.mk_comcode8 == r["mk_comcode8"]).one()
        except NoResultFound:

            ed = EightDigitCode()

            ed.mk_comcode = r["mk_comcode"]
            ed.mk_intra_extra_ind = r["mk_intra_extra_ind"]
            ed.mk_intra_mm_on = r["mk_intra_mm_on"]
            ed.mk_intra_yy_on = r["mk_intra_yy_on"]
            ed.mk_intra_mm_off = r["mk_intra_mm_off"]
            ed.mk_intra_yy_off = r["mk_intra_yy_off"]
            ed.mk_extra_mm_on = r["mk_extra_mm_on"]
            ed.mk_extra_yy_on = r["mk_extra_yy_on"]
            ed.mk_extra_mm_off = r["mk_extra_mm_off"]
            ed.mk_extra_yy_off = r["mk_extra_yy_off"]
            ed.mk_non_trade_id = r["mk_non_trade_id"]
            ed.mk_sitc_no = r["mk_sitc_no"]
            ed.mk_sitc_ind = r["mk_sitc_ind"]
            ed.mk_sitc_conv_a = r["mk_sitc_conv_a"]
            ed.mk_sitc_conv_b = r["mk_sitc_conv_b"]
            ed.mk_cn_q2 = r["mk_cn_q2"]
            ed.mk_supp_arrivals = r["mk_supp_arrivals"]
            ed.mk_supp_despatches = r["mk_supp_despatches"]
            ed.mk_supp_imports = r["mk_supp_imports"]
            ed.mk_supp_exports = r["mk_supp_exports"]
            ed.mk_sub_group_arr = r["mk_sub_group_arr"]
            ed.mk_item_arr = r["mk_item_arr"]
            ed.mk_sub_group_desp = r["mk_sub_group_desp"]
            ed.mk_item_desp = r["mk_item_desp"]
            ed.mk_sub_group_imp = r["mk_sub_group_imp"]
            ed.mk_item_imp = r["mk_item_imp"]
            ed.mk_sub_group_exp = r["mk_sub_group_exp"]
            ed.mk_item_exp = r["mk_item_exp"]
            ed.mk_qty1_alpha = r["mk_qty1_alpha"]
            ed.mk_qty2_alpha = r["mk_qty2_alpha"]
            ed.mk_commodity_alpha_1 = r["mk_commodity_alpha_1"]
            ed.mk_commodity_alpha_2 = r["mk_commodity_alpha_2"]
            ed.mk_commodity_alpha_all = r["mk_commodity_alpha_all"]

            ed.mk_comcode8 = r["mk_comcode8"]

            session.add(ed)
        except MultipleResultsFound:
            logger.debug("Multiple rows found for code {}".format(r["mk_comcode8"]))

    session.commit()

from my_models import EightDigitCodeHeader
def write_header_record_to_db(df):

    for row in df.iterrows():
        r = row[1]

        edh = EightDigitCodeHeader()

        edh.mk_filename = r["mk_filename"]
        edh.mk_month = r["mk_month"]
        edh.mk_year = r["mk_year"]

        session.add(edh)
    session.commit()



