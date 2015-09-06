__author__ = 'Robin'

from uk_trade_data.web_to_db import check_for_updates, build_lookups, build_historical_data

import logging
logging.basicConfig(filename='mylog.log',
                            filemode='a',
                            level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',)


ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)



logger = logging.getLogger(__name__)

logger.addHandler(ch)

logger.debug("starting")

from uk_trade_data.my_database import init_db, session
init_db(remove=False)

build_lookups()
check_for_updates()
build_historical_data()

#Check the cascade deletes work
# from uk_trade_data.my_models import Import, RawFileLog
#Check the cascade deletion works
# rawfile = session.query(RawFileLog).filter(RawFileLog.id == 1).delete()
#session.commit()
#print session.query(Import).count()


from uk_trade_data.create_derived_tables_sqlite import create_derived_country_products_month, create_derived_select_box, create_derived_country_products_month_eu, create_derived_importers_for_web

#
# create_derived_country_products_month()
# create_derived_select_box()
# create_derived_country_products_month_eu()
# create_derived_importers_for_web()