__author__ = 'Robin'

from uk_trade_data.write_control_data import write_xls_heirarchy_to_otherdigitcodes

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from uk_trade_data.my_database import init_db
init_db(remove=False)
write_xls_heirarchy_to_otherdigitcodes()