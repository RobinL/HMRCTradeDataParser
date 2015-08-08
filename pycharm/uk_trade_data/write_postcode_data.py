__author__ = 'Robin'

import pandas as pd
from my_models import Postcode
from my_database import session
from my_database import engine
import trade_data_config

def write_postcode_data_to_db():

    postcode_data = pd.read_csv("specs/ukpostcodes.csv", encoding="utf8", nrows=trade_data_config.POSTCODE_ROWS)
    postcode_data.columns = ["id","postcode", "lat","lng"]
    rows_dict = postcode_data[:trade_data_config.MAX_IMPORT_ROWS].to_dict(orient="records")

    engine.execute(
        Postcode.__table__.insert(),
        rows_dict
    )