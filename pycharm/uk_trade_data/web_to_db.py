__author__ = 'Robin'

MAX_URLS = 50000

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

    for y in range(2015,now.year):
        for m in range(1,13):
            url_part = str(y)[-2:]+'{num:02d}'.format(num=m)
            month = m
            year = y

            url_full = base_url + specific_url_part + url_part + ".zip"

            file_name = specific_url_part + url_part
            file_name_zip = specific_url_part + url_part + ".zip"


            final_urls.append({"url_full": url_full, "file_name":file_name, "month":month, "year": year, "file_name_zip": file_name_zip})

    for m in range(1, now.month):
        year = now.year
        month = m
        url_part =str(now.year)[-2:] + '{num:02d}'.format(num=m)

        url_full = base_url + specific_url_part + url_part + ".zip"

        file_name = specific_url_part + url_part
        file_name_zip = specific_url_part + url_part + ".zip"

        final_urls.append({"url_full": url_full, "file_name":file_name, "month":month, "year": year,"file_name_zip": file_name_zip})

    final_urls = sorted(final_urls, key=lambda x: float(x["year"])*1000 + float(x["month"]), reverse=True)

    return final_urls[:MAX_URLS]


from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen



def unzip_url(url):
    url = urlopen(url)
    zipfile = ZipFile(StringIO(url.read()))
    return zipfile


from write_country_data import download_and_insert_country_data, download_and_insert_port_data


from write_control_data import raw_control_data_to_database, write_xls_heirarchy_to_otherdigitcodes
from write_importer_data import raw_importer_data_to_database
from write_import_data import raw_import_data_to_database
from write_meta_data import write_meta_data_to_db

from zipfile import BadZipfile

def find_new_files_and_add_to_database():

    write_meta_data_to_db()
    write_xls_heirarchy_to_otherdigitcodes()
    download_and_insert_country_data()
    download_and_insert_port_data()

    # Start with control files

    def get_and_iterate_urls(specific_url_part, add_to_database_function):
        
        urls = get_urls(specific_url_part)

        for url_info in urls:

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

                r = RawFileLog()
                r.file_name = url_info["file_name"]
                r.url = url_info["url_full"]
                r.processing_completed = False

                session.add(r)
                session.commit()
                

                add_to_database_function(zip_file, url_info,r)

                r.processing_completed = True

                session.add(r)
                session.commit()
            except MultipleResultsFound:
                logger.debug("The file {} seems to have been added to the database multiple times".format(file_name))


    #2015 records onwards
    get_and_iterate_urls("SMKA12", raw_control_data_to_database)
    get_and_iterate_urls("SIAI11", raw_importer_data_to_database)
    get_and_iterate_urls("SMKI19", raw_import_data_to_database)


    def get_and_iterate_historical(specific_url_part, add_to_database_function):

        urls = [r"https://www.uktradeinfo.com/Statistics/Documents/{}_{}archive.zip" \
                .format(specific_url_part, y) for y in range(2014,2007,-1)]

        #one of the archives has the wrong url - do a find and replace
        replace_this = r"https://www.uktradeinfo.com/Statistics/Documents/SIAI11_2011archive.zip"
        with_this = r"https://www.uktradeinfo.com/Statistics/Documents/SIAI_2011archive.zip"

        urls = [with_this if u == replace_this else u for u in urls]

        #Get zipfile and open 
        for url in urls:
            logger.debug("starting with zipfile at {}".format(url))
            zip_file = unzip_url(url)
            file_list = [f.filename for f in zip_file.filelist]
            final_files = []
            for f in file_list:

                this_f = {}
                this_f["file_name"] = f.replace(".zip", "")
                this_f["file_name_zip"] = f
                this_f["year"] = "20" + f[-8:-6]
                this_f["month"] = f[-6:-4]
                this_f["url_full"] = url
                final_files.append(this_f)

            try:
                final_files.sort(key=lambda x: int(x["month"]), reverse=True)
            except:
                logger.debug("failed to sort zipfile at url {}".format(url))


            for url_info in final_files:
                logger.debug("Processing file: {}".format(url_info["file_name_zip"]))
                

                try:
                    r = session.query(RawFileLog).filter(RawFileLog.file_name == url_info["file_name"]).one()
                    logger.debug("The file {} is already in the database".format(url_info["file_name"]))
                except NoResultFound:

                    try:
                        zip_file2 = StringIO(zip_file.read(url_info["file_name_zip"]))
                        zip_file2 = ZipFile(zip_file2)

                    except BadZipfile:
                        logger.info("File from {} was a bad zip file".format(url_info["url_full"]))
                        continue

                    r = RawFileLog()
                    r.file_name = url_info["file_name"]
                    r.url = url_info["url_full"]
                    r.processing_completed = False

                    session.add(r)
                    session.commit()
                    
                    try:
                        add_to_database_function(zip_file2, url_info,r)
                        r.processing_completed = True
                    except:
                        logger.debug("Something failed in adding the file {} to the database")

                    session.add(r)
                    session.commit()
                except MultipleResultsFound:
                    logger.debug("The file {} seems to have been added to the database multiple times".format(file_name))



    #get_and_iterate_historical("SMKA12", raw_control_data_to_database)
    #get_and_iterate_historical("SIAI11", raw_importer_data_to_database)
    #get_and_iterate_historical("SMKI19", raw_import_data_to_database)


    #historical records