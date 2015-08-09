from flask import render_template,  url_for, current_app, request
from . import myapp
from . import db

import logging
logger = logging.getLogger(__name__)

from results import get_non_eu_data, get_importers_data
from other_helpers import  db_result_to_json_in_d3csv_format, all_arguments_populated


@myapp.route('/' ,methods=["GET","POST"])
def home():
    return render_template('home.html')

@myapp.route('/imports', methods=["GET","POST"])
def imports_view():
    return render_template('imports.html')


@myapp.route('/importers', methods=["GET","POST"])
def importers_view():
    return render_template('importers.html')



#All json routes are below
from flask import jsonify

from results import get_eu_data
@myapp.route('/eu_imports.json', methods=["GET","POST"])
def get_eu_imports_json():

    arguments = request.args


    if all_arguments_populated(arguments):
        result = get_eu_data(arguments, "imports")
        result = db_result_to_json_in_d3csv_format(result)

    else:
        result =  []

    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp

@myapp.route('/non_eu_imports.json', methods=["GET","POST"])
def get_non_eu_imports_json():

    arguments = request.args

    if all_arguments_populated(arguments):
        result = get_non_eu_data(arguments, "imports")
        result = db_result_to_json_in_d3csv_format(result)

    else:
        result =  []

    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp

@myapp.route('/non_eu_exports.json', methods=["GET","POST"])
def get_non_eu_exports_json():

    arguments = request.args

    if all_arguments_populated(arguments):
        result = get_non_eu_data(arguments, "exports")
        result = db_result_to_json_in_d3csv_format(result)

    else:
        result =  []

    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp


from results import get_selection_box_data
@myapp.route('/selectboxdata.json', methods=["GET","POST"])
def get_select_box_json():
    arguments = request.args

    try:
        type= arguments["type"]
    except:
        type = ""

    result = get_selection_box_data(type)
    result = db_result_to_json_in_d3csv_format(result)


    resp = jsonify(csv_like_data = result, encoding="windows-1252")
    resp.status_code = 200

    return resp


from results import get_non_eu_timeseries_data
@myapp.route('/timeseries_imports.json', methods=["GET","POST"])
def get_timeseries_json():

    arguments = request.args

    if all_arguments_populated(arguments):
        result = get_non_eu_timeseries_data(arguments, "imports")
    else:
        result =  {}

    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp

import re
import datetime


@myapp.route('/importers.json', methods=["GET","POST"])
def get_importers_json():

    
    arguments = request.args
    codes = arguments.getlist("codes[]")


    if len(codes):

      
        result = get_importers_data(codes)
        result = db_result_to_json_in_d3csv_format(result)

        fields_list = ["ia_name",
        "ia_addr_1",
        "ia_addr_2",
        "ia_addr_3",
        "ia_addr_4",
        "ia_addr_5"]


        new_results = []
    
        for this_result in result:

            new_result = {}
            new_result["full_address"] = ", ".join([this_result[a].strip().title() for a in fields_list])
            new_result["full_address"]  = new_result["full_address"] + ", " + this_result["ia_pcode"].strip()

            new_result["full_address"] = re.sub(r"\s{2,100}",r" ",new_result["full_address"])
            new_result["full_address"] = re.sub(r"(, ){2,100}",r", ",new_result["full_address"])

            new_result["date"] = datetime.datetime(int(this_result["year"]), int(this_result["month"]), 1).date().isoformat()
            new_result["product"] = this_result["product_code"]


            new_result["lat"] = this_result["lat"]
            new_result["lng"] = this_result["lng"]

            new_results.append(new_result)
        result = new_results

        new_results = {}
        for this_result in result:

            f_a = this_result["full_address"]
            pr = this_result["product"]
            da = this_result["date"]
            da = datetime.datetime.strptime(da,"%Y-%m-%d")

            lat = this_result["lat"]
            lng = this_result["lng"]

            #da = datetime.datetime.strftime(da, "%b %Y")


            if f_a not in new_results:
                new_results[f_a] = {"products": {pr}, "dates": [da], "lat": lat, "lng":lng }
            else:
                new_results[f_a]["products"].update([pr])
                new_results[f_a]["dates"].append(da)


        final_results = []

        def date_string(dates_list):

            dates_list.sort()
            if len(dates_list) ==1:
                return datetime.datetime.strftime(dates_list[0], "%b %Y")
            else:
                return "{} months between {} and {}".format(len(dates_list), datetime.datetime.strftime(dates_list[0], "%b %Y"),datetime.datetime.strftime(dates_list[-1], "%b %Y"))

        def lat_exists(lat):
            if lat:
                return True
            else:
                return False


        for key in new_results:

            this_result = new_results[key]

            final_results.append({"full_address":key, "products": list(this_result["products"]), "dates": this_result["dates"], "lat":this_result["lat"],"lng": this_result["lng"]})


        for this_result in final_results:
            this_result["date_count"] = len(this_result["dates"])
            this_result["latest_date"] = max(this_result["dates"])
            this_result["dates"] = date_string(this_result["dates"])
            this_result["on_map"] = lat_exists(this_result["lat"])



        result = sorted(final_results,key = lambda x: (x["lat"], datetime.datetime.now() - x["latest_date"]))

        for d in result:
            del d['latest_date']


    else:
        result =  []


    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp
