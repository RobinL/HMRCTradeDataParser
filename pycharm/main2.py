__author__ = 'Robin'

from uk_trade_data.web_to_db import find_new_files_and_add_to_database

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from uk_trade_data.my_database import init_db
init_db(remove=False)
find_new_files_and_add_to_database()