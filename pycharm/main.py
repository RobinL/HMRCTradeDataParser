__author__ = 'Robin'

from uk_trade_data.write_importer_data import  raw_importer_data_to_database
from uk_trade_data.write_import_data import raw_import_data_to_database
from uk_trade_data.write_control_data import raw_control_data_to_database
from uk_trade_data.write_meta_data import write_meta_data_to_db
from uk_trade_data.write_country_data import download_and_insert_country_data, download_and_insert_port_data

from create_db import init_db

init_db(remove=True)

download_and_insert_country_data()
download_and_insert_port_data()

write_meta_data_to_db()
raw_importer_data_to_database(r"data/SIAI111504")
raw_import_data_to_database(r"data/SMKI191504")
raw_control_data_to_database(r"data/SMKA121504")


