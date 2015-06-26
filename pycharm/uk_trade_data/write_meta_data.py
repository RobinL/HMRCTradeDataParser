__author__ = 'Robin'

import pandas as pd
from my_models import MetaData
from my_database import session

def write_meta_data_to_db():

    meta_data_csv = pd.read_csv("specs/fields_meta_data.csv", encoding="utf8")

    session.query(MetaData).delete()
    session.commit()

    for row in meta_data_csv.iterrows():

        r = row[1]
        m = MetaData()

        m.field_name = r["field_name"]
        m.full_name = r["full_name"]
        m.description = r["description"]

        session.add(m)

    session.commit()