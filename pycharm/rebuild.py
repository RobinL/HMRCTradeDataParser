__author__ = 'Robin'
from uk_trade_data.web_to_db import rebuild_from_file
from uk_trade_data.write_eu_export_data import raw_eu_export_data_to_database

# rebuild_from_file(specific_url_part="SMKX46",
# 	path_to_replacement_zip=r"C:\Users\Robin\Downloads\smkx461406.zip",
# 	file_type= "eu_exports",
# 	month=6,
# 	year=2014,
# 	add_to_database_function=raw_eu_export_data_to_database)


# from uk_trade_data.my_models import RawFileLog
# from uk_trade_data.my_database import session
# from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

# rawfile = session.query(RawFileLog).filter(RawFileLog.url=="C:\Users\Robin\Downloads\smkx461406.zip").delete()
# session.commit()

from uk_trade_data.create_derived_tables_sqlite import create_derived_country_products_month, create_derived_select_box, create_derived_country_products_month_eu, create_derived_importers_for_web


create_derived_country_products_month()
create_derived_select_box()
create_derived_country_products_month_eu()
create_derived_importers_for_web()