__author__ = 'Robin'


# url  = "https://www.uktradeinfo.com/Statistics/Documents/Forms/AllItems.aspx?SortField=Modified&SortDir=Desc"
#
# https://www.uktradeinfo.com/Statistics/Documents/SMKA121504.zip #control
# https://www.uktradeinfo.com/Statistics/Documents/SMKI191504.zip #imports
# https://www.uktradeinfo.com/Statistics/Documents/SIAI111504.zip #trader

import datetime

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from my_models import RawFileLog
from my_database import session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound



def get_urls(specific_url_part):

    base_url = "https://www.uktradeinfo.com/Statistics/Documents/"

    #Get all the different date combinations:
    now = datetime.datetime.now()

    #Create list of all files starting in Jan 2014 going to current month

    final_urls = []

    for y in range(2014,now.year):
        for m in range(1,13):
            url_part = str(y)[-2:]+'{num:02d}'.format(num=m)
            month = m
            year = y

            url_full = base_url + specific_url_part + url_part + ".zip"

            file_name = specific_url_part + url_part

            final_urls.append({"url_full": url_full, "file_name":file_name, "month":month, "year": year})

    for m in range(1, now.month):
        year = now.year
        month = m
        url_part =str(now.year)[-2:] + '{num:02d}'.format(num=m)

        url_full = base_url + specific_url_part + url_part + ".zip"

        file_name = specific_url_part + url_part

        final_urls.append({"url_full": url_full, "file_name":file_name, "month":month, "year": year})


    return final_urls


from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen


def unzip_url(url):
    url = urlopen(url)
    zipfile = ZipFile(StringIO(url.read()))
    return zipfile


from write_country_data import download_and_insert_country_data, download_and_insert_port_data


from write_control_data import raw_control_data_to_database
from write_importer_data import raw_importer_data_to_database
from write_import_data import raw_import_data_to_database
from write_meta_data import write_meta_data_to_db

from zipfile import BadZipfile

def find_new_files_and_add_to_database():

    write_meta_data_to_db()
    download_and_insert_country_data()
    download_and_insert_port_data()

    # Start with control files

    def get_and_iterate_urls(specific_url_part, add_to_database_function):
        
        urls = get_urls(specific_url_part)

        for url_info in urls[:2]:

            logger.debug("file: {}".format(url_info["url_full"]))
          

            try:
                r = session.query(RawFileLog).filter(RawFileLog.file_name == url_info["file_name"]).one()
                logger.debug("The file {} is already in the database".format(url_info["file_name"]))
            except NoResultFound:

                try:
                    zip_file = unzip_url(url_info["url_full"])
                except BadZipfile:
                    logger.info("File from {} was a bad zip file".format(url_info["url_full"]))
                    continue
           
                

                add_to_database_function(zip_file, url_info)

                r = RawFileLog()
                r.file_name = url_info["file_name"]
                r.url = url_info["url_full"]

                session.add(r)
                session.commit()
            except MultipleResultsFound:
                logger.debug("The file {} seems to have been added to the database multiple times".format(file_name))

    #Control files

    get_and_iterate_urls("SMKI19", raw_import_data_to_database)

    get_and_iterate_urls("SMKA12", raw_control_data_to_database)

    get_and_iterate_urls("SIAI11", raw_importer_data_to_database)



   
