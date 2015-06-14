__author__ = 'Robin'

from uk_trade_data.write_import_data import raw_import_data_to_database
from uk_trade_data.write_control_data import raw_control_data_to_database

from create_db import init_db

init_db(remove=True)


raw_import_data_to_database(r"data/SMKI191504")
raw_control_data_to_database(r"data/SMKA121504")


