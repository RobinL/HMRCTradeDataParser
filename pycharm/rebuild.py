__author__ = 'Robin'
from uk_trade_data.web_to_db import rebuild_from_file
from uk_trade_data.write_export_estimates_data import raw_export_estimates_data_to_db

rebuild_from_file(specific_url_part="SESX16",
	path_to_replacement_zip=r"backups_of_broken_website_files\sesx161408.zip",
	file_type= "export_estimates",
	month=8,
	year=2014,
	add_to_database_function=raw_export_estimates_data_to_db)


# from uk_trade_data.my_models import RawFileLog
# from uk_trade_data.my_database import session
# from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

# rawfile = session.query(RawFileLog).filter(RawFileLog.url=="C:\Users\Robin\Downloads\smkx461406.zip").delete()
# session.commit()

from uk_trade_data.create_derived_tables_sqlite import create_derived_country_products_month, create_derived_select_box, create_derived_country_products_month_eu, create_derived_importers_for_web


# create_derived_country_products_month()
# create_derived_select_box()
# create_derived_country_products_month_eu()
# create_derived_importers_for_web()