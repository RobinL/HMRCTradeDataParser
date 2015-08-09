__author__ = 'Robin'

from uk_trade_data.create_derived_tables_sqlite import create_derived_country_products_month, create_derived_select_box, create_derived_country_products_month_eu,create_derived_importers_for_web
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


create_derived_country_products_month()
create_derived_select_box()
create_derived_country_products_month_eu()
create_derived_importers_for_web()

