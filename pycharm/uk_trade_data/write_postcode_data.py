__author__ = 'Robin'

import pandas as pd
from my_models import Postcode
from my_database import session

def write_postcode_data_to_db():

    postcode_data = pd.read_csv("specs/ukpostcodes.csv", encoding="utf8")

    session.query(Postcode).delete()
    session.commit()

    counter = 0
    for row in postcode_data.iterrows():

        counter +=1
        r = row[1]
        p = Postcode()

        p.postcode = r["postcode"]
        p.lat = r["latitude"]
        p.lng = r["longitude"]

        session.add(p)

        if counter % 50000 ==0:
            print counter*1.0/len(postcode_data)
            session.commit()