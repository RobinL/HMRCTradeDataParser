 #!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Robin'

import datetime

import logging
logger = logging.getLogger(__name__)

from my_models import RawFileLog
from my_database import session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import trade_data_config

from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen

from write_country_data import download_and_insert_country_data, download_and_insert_port_data
from write_control_data import raw_control_data_to_database, write_xls_heirarchy_to_otherdigitcodes
from write_importer_data import raw_importer_data_to_database
from write_import_data import raw_import_data_to_database
from write_export_data import raw_export_data_to_database
from write_eu_import_data import raw_eu_import_data_to_database
from write_eu_export_data import raw_eu_export_data_to_database
from write_meta_data import write_meta_data_to_db
from uk_trade_data.write_postcode_data import write_postcode_data_to_db

from zipfile import BadZipfile

def get_urls_non_historical(specific_url_part):

    base_url = "https://www.uktradeinfo.com/Statistics/Documents/"

    #Get all the different date combinations:
    now = datetime.datetime.now()

    #Create list of all files starting in Jan 2014 going to current month

    final_urls = []

    for y in range(2015,now.year+1):
        for m in range(1,13):

            if y == now.year and m > now.month:
                break

            #Last two digits of year and month with zero padding
            url_part = str(y)[-2:]+'{num:02d}'.format(num=m)

            url_full = base_url + specific_url_part + url_part + ".zip"
            file_name = specific_url_part + url_part
            file_name_zip = specific_url_part + url_part + ".zip"
            final_urls.append({"url_full": url_full,
                               "file_name":file_name,
                               "month":m,
                               "year": y,
                               "file_name_zip": file_name_zip
                               })

    final_urls = sorted(final_urls, key=lambda x: float(x["year"])*1000 + float(x["month"]), reverse=True)

    return final_urls[:trade_data_config.MAX_URLS]


def specific_url_part_to_type(specific_url_part):

    lookup = {"SMKA12": "product_codes",
        "SIAI11": "importers",
        "SMKI19": "imports",
        "SMKE19": "exports",
        "SMKM46": "eu_imports",
        "SMKX46": "eu_exports"

    }

    return lookup[specific_url_part]


def unzip_url(url):
    url = urlopen(url)
    zipfile = ZipFile(StringIO(url.read()))
    #zipfile = ZipFile(r"C:\Users\Robin\Downloads\smkx461406.zip")
    #zipfile = ZipFile(r"C:\Users\rlinacre\Downloads\smkm461506.zip")
    #zipfile = ZipFile(r"C:\Users\rlinacre\Downloads\SMKI191506.zip")
    #zipfile = ZipFile(r"C:\Users\rlinacre\Downloads\SMKA121506.zip")
    #zipfile = ZipFile(r"C:\Users\rlinacre\Downloads\SMKE191506.zip")
    

    return zipfile



def unzip_file(file_path):
    zipfile = ZipFile(file_path)
    

    return zipfile




def get_and_iterate_urls(specific_url_part, add_to_database_function):
    
    urls = get_urls_non_historical(specific_url_part)

    for url_info in urls:

        logger.debug("file: {}".format(url_info["url_full"]))
      
        try:
            r = session.query(RawFileLog).filter(RawFileLog.expected_file_name_in_child_zip == url_info["file_name"]).one()
            logger.debug("The file {} is already in the database".format(url_info["file_name"]))
        
        except NoResultFound:

            try:
                zip_file = unzip_url(url_info["url_full"])
            except BadZipfile:
                logger.info("File from {} was a bad zip file".format(url_info["url_full"]))
                continue

            r = RawFileLog()
            r.parent_zip_file = "No parent"
            r.child_zip_file =  url_info["url_full"].rsplit('/',1)[1]
            r.expected_file_name_in_child_zip = url_info["file_name"]
            r.url = url_info["url_full"]
            r.processing_completed = False
            r.timestamp = datetime.datetime.now()
            r.file_type = specific_url_part_to_type(specific_url_part)
            r.month = url_info["month"]
            r.year = url_info["year"]

            session.add(r)
            session.commit()
            

            add_to_database_function(zip_file, url_info,r)

            r.processing_completed = True

            session.add(r)
            session.commit()


        except MultipleResultsFound:
            logger.debug("The file {} seems to have been added to the database multiple times".format(file_name))



def get_urls_historical(specific_url_part):


    urls = [r"https://www.uktradeinfo.com/Statistics/Documents/{}_{}archive.zip" \
            .format(specific_url_part, y) for y in range(2014,2012,-1)]

    #one of the archives has the wrong url - do a find and replace
    replace_this = r"https://www.uktradeinfo.com/Statistics/Documents/SIAI11_2011archive.zip"
    with_this = r"https://www.uktradeinfo.com/Statistics/Documents/SIAI_2011archive.zip"

    urls = [with_this if u == replace_this else u for u in urls]

    return urls


#This handles downloading the historical zip files and accessing their contents 
def get_and_iterate_historical(specific_url_part, add_to_database_function):

    urls = get_urls_historical(specific_url_part)

    #Get zipfile and open 
    for url in urls:
        logger.debug("starting with zipfile at {}".format(url))
        zip_file = unzip_url(url)


        #Note there's no ambiguity over the filename of the zipfiles which are in the zipfiles
        #But this also means we cannot be sure of the month and year because the file may be incorrectly named
        file_list = [f.filename for f in zip_file.filelist]
        final_files = []


        # for f in file_list:


        try:
            final_files.sort(key=lambda x: int(x["month"]), reverse=True)
        except:
            logger.debug("failed to sort zipfile at url {}".format(url))


        for file_info in final_files:
            logger.debug("Processing file: {}".format(file_info["file_name_zip"]))


            try:
                r = session.query(RawFileLog).filter(RawFileLog.expected_file_name_in_child_zip == file_info["file_name"]).one()
                logger.debug("The file {} is already in the database".format(file_info["file_name"]))
            except NoResultFound:

                try:
                    zip_file2 = StringIO(zip_file.read(file_info["file_name_zip"]))
                    zip_file2 = ZipFile(zip_file2)

                except BadZipfile:
                    logger.info("File from {} was a bad zip file".format(file_info["url_full"]))
                    continue

                r = RawFileLog()
                r.parent_zip_file = file_info["url_full"].rsplit('/',1)[1]
                r.child_zip_file =  file_info["file_name_zip"]
                r.expected_file_name_in_child_zip = file_info["file_name"]
                r.url = file_info["url_full"]
                r.processing_completed = False
                r.timestamp = datetime.datetime.now()
                r.file_type = specific_url_part_to_type(specific_url_part)
                r.month = file_info["month"]
                r.year = file_info["year"]

                session.add(r)
                session.commit()

                try:
                    add_to_database_function(zip_file2, file_info,r)
                    r.processing_completed = True
                except:
                    logger.debug("Something failed in adding the file {} to the database")

                session.add(r)
                session.commit()
            except MultipleResultsFound:
                logger.debug("The file {} seems to have been added to the database multiple times".format(file_info["url_full"]))


import os 
def rebuild_from_file(specific_url_part=None,path_to_replacement_zip=None, file_type=None,month=None,year=None, add_to_database_function=None):

    try:
        rawfile = session.query(RawFileLog).filter(RawFileLog.file_type == file_type).filter(RawFileLog.month == month).filter(RawFileLog.year == year).delete()
        session.commit()
    except:
        logger.debug("data not currently in database")
        return




    try:
        zip_file = unzip_file(path_to_replacement_zip)
    except BadZipfile:
        logger.info("File from {} was a bad zip file".format(path_to_replacement_zip))


    head, tail = os.path.split(path_to_replacement_zip)

    this_f = {}
    this_f["file_name"] =  tail
    this_f["file_name_zip"] = tail.replace(".zip","")
    if year:
       this_f["year"] = year
    else:
        this_f["year"] = "20" + tail[-8:-6]

    if month:
        this_f["month"] = month
    else:
        this_f["month"] = tail[-6:-4]

    this_f["url_full"] = path_to_replacement_zip


    r = RawFileLog()
    r.parent_zip_file = "No parent - manual addition after failure"
    r.child_zip_file =  tail
    r.expected_file_name_in_child_zip = tail.replace(".zip","")
    r.url = path_to_replacement_zip
    r.processing_completed = False
    r.timestamp = datetime.datetime.now()
    r.file_type = specific_url_part_to_type(specific_url_part)
    r.month = this_f["month"]
    r.year = this_f["year"]
    session.add(r)
    session.commit()
    

    add_to_database_function(zip_file, this_f,r)

    r.processing_completed = True

    session.add(r)
    session.commit()




def build_full_dataset():
    build_lookups()
    build_historical_data()
    check_for_updates()


def check_for_updates():
    get_and_iterate_urls("SMKA12", raw_control_data_to_database)
    get_and_iterate_urls("SIAI11", raw_importer_data_to_database)
    get_and_iterate_urls("SMKI19", raw_import_data_to_database)
    get_and_iterate_urls("SMKE19", raw_export_data_to_database)
    get_and_iterate_urls("SMKX46", raw_eu_export_data_to_database)
    get_and_iterate_urls("SMKM46", raw_eu_import_data_to_database)


def build_historical_data():

    get_and_iterate_historical("SMKA12", raw_control_data_to_database)
    get_and_iterate_historical("SIAI11", raw_importer_data_to_database)
    get_and_iterate_historical("SMKI19", raw_import_data_to_database)
    get_and_iterate_historical("SMKE19", raw_export_data_to_database)
    get_and_iterate_historical("SMKM46", raw_eu_import_data_to_database)
    get_and_iterate_historical("SMKX46", raw_eu_export_data_to_database)

def build_lookups():
    write_postcode_data_to_db()
    write_meta_data_to_db()
    write_xls_heirarchy_to_otherdigitcodes()
    download_and_insert_country_data()
    download_and_insert_port_data()