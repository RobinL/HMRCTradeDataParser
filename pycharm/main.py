__author__ = 'Robin'

from uk_trade_data.web_to_db import check_for_updates

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from uk_trade_data.my_database import init_db, session
init_db(remove=True)

check_for_updates()

#Check the cascade deletes work
# from uk_trade_data.my_models import Import, RawFileLog
#Check the cascade deletion works
# rawfile = session.query(RawFileLog).filter(RawFileLog.id == 1).delete()
#session.commit()
#print session.query(Import).count()