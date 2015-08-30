__author__ = 'Robin'
import pandas as pd
from .utils import get_fields_df, get_zipped_file_contents, get_specs_dict, build_from_spec
from my_models import EightDigitCode, CombinedNomenclature
from my_database import session
from my_database import engine
import trade_data_config
import logging
logger = logging.getLogger(__name__)




def raw_control_data_to_database(zipfile, url_info,rawfile):


    #Get dict of the contents of the file - including header record, filename etc
    contents = get_zipped_file_contents(zipfile)
    middle_records_specs_dict = get_specs_dict("specs/control_file_middle_specs.csv")
    middle_records_df = build_from_spec(contents["middle_records"], middle_records_specs_dict)

    rawfile.actual_file_name_in_child_zip = contents["actual_file_name_in_child_zip"]

    write_middle_records_to_db(middle_records_df,rawfile)

    rows = session.query(EightDigitCode).count()
    logger.debug("there are now {} records in the eightdigitcode table".format(rows))




from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound



def write_middle_records_to_db(df,rawfile):

    counter = 0
    #This assumes we iterate backwards through the files to make sure the files on record are the 'most recent'
    #First get a list of all the existing eight digit codes

    existing_codes = session.query(EightDigitCode.mk_comcode8).all()
    codes_set = set([c[0] for c in existing_codes])


    for row in df[:trade_data_config.MAX_IMPORT_ROWS].iterrows():

        counter +=1
        if counter % 500 ==0:
            logger.debug("done {} rows".format(counter))
            session.flush()

        r = row[1]

        if r["comcode8"] in codes_set:
            continue

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
        ed.mk_commodity_alpha_all = r["mk_commodity_alpha_all"].strip()

        ed.mk_comcode8 = r["comcode8"]

        ed.rawfile = rawfile

        session.add(ed)

        codes_set = codes_set.union(r["comcode8"])


    session.commit()


from my_models import Lookup_Code_1, Lookup_Code_2, Lookup_Code_4, Lookup_Code_6
def write_code_lookup_tables():

    df = pd.read_csv("specs/lookup_codes_1.csv", dtype={"code": str, "code_2":str}, encoding="utf-8")
    rows_dict = df.to_dict(orient="records")

    engine.execute(
        Lookup_Code_1.__table__.insert(),
        rows_dict
    )

    df = pd.read_csv("specs/lookup_codes_2.csv", dtype={"code" : str}, encoding="utf-8")
    rows_dict = df.to_dict(orient="records")

    engine.execute(
        Lookup_Code_2.__table__.insert(),
        rows_dict
    )

    df = pd.read_csv("specs/lookup_codes_4.csv", dtype={"code" : str}, encoding="utf-8")
    rows_dict = df.to_dict(orient="records")

    engine.execute(
        Lookup_Code_4.__table__.insert(),
        rows_dict
    )

    df = pd.read_csv("specs/lookup_codes_6.csv", dtype={"code" : str}, encoding="utf-8")
    rows_dict = df.to_dict(orient="records")

    engine.execute(
        Lookup_Code_6.__table__.insert(),
        rows_dict
    )