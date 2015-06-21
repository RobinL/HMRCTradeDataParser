__author__ = 'Robin'


# url  = "https://www.uktradeinfo.com/Statistics/Documents/Forms/AllItems.aspx?SortField=Modified&SortDir=Desc"
#
# https://www.uktradeinfo.com/Statistics/Documents/SMKA121504.zip #control
# https://www.uktradeinfo.com/Statistics/Documents/SMKI191504.zip #imports
# https://www.uktradeinfo.com/Statistics/Documents/SIAI111504.zip #trader

import datetime


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


from write_control_data import raw_control_data_to_database

from zipfile import BadZipfile

def find_new_files_and_add_to_database():

    #Start with control files

    urls = get_urls("SMKA12")

    for url in urls:
        url_full = url["url_full"]
        file_name = url["file_name"]

        print url_full

        try:
            zip_file = unzip_url(url_full)
        except BadZipfile:
            continue

        raw_control_data_to_database(zip_file, file_name)





    #Then importers


    #Then imports
