__author__ = 'Robin'

from uk_trade_data.web_to_db import find_new_files_and_add_to_database

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

#from create_db import init_db
find_new_files_and_add_to_database()