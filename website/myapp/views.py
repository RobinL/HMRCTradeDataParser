from flask import render_template,  url_for, current_app, request
from . import myapp
from . import db
import datetime




import logging
import traceback
logger = logging.getLogger(__name__)


def get_selection_box_data():

    sql = """
    select select_box, my_key, value
    from select_box_values
    """

    result = db.session.execute(sql)

    return result


# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def quotify(my_list):
        return (', '.join("'" + item + "'" for item in my_list))

def check_injection(my_list):
    if len(my_list)>8:
        return True
    else:
        return False    

def get_years_months_list(dates_list):

    years_list = []
    months_list = []

    for i in dates_list:
        if i == "All":
            years_list.append("All")
            months_list.append("All")
            continue
        d = i.split(" ")
        if d[0] not in years_list:
            years_list.append(d[0])

        if d[1] not in months_list:
            months_list.append(d[1])

    return {"years_list": years_list, "months_list":months_list}


def get_sql(sql, countries_list,ports_list,products_list,dates_list):

    d = get_years_months_list(dates_list)
    months_list = d["months_list"]
    years_list = d["years_list"]

    query_dict = {
    "countries_list" : {"list": countries_list, "sql" : "and country_code in ({countries_list})" } ,
    "ports_list" : {"list": ports_list, "sql" : "and port_code in ({ports_list})" },
    "products_list" : {"list": products_list, "sql" : "and product_code in ({products_list})" }

    }


    queryconditions = ""
    for key in query_dict:
        check_injection(query_dict[key]["list"])
        query_dict[key]["quotify"] = quotify(query_dict[key]["list"])
        if "All" not in query_dict[key]["quotify"]:

            queryconditions += " " + query_dict[key]["sql"]


    if "All" not in months_list:

        or_condition = "and ("
        counter = 0
        for d in dates_list:
            ds = d.split(" ")
            if counter ==0:
                or_condition = or_condition + " (year = '{}' and month = '{}') ".format(ds[0], ds[1])
            else:
                or_condition = or_condition + " or (year = '{}' and month = '{}') ".format(ds[0], ds[1])
            counter +=1

        or_condition = or_condition + ")"

        queryconditions += or_condition



    sql2 = sql.format(queryconditions=queryconditions)

    format_dict = {k: query_dict[k]["quotify"] for k in query_dict}

    sql3 = sql2.format(**format_dict)

    return sql3



def get_imports_data2(countries_list,ports_list,products_list,dates_list):




    #You can't parametize the in keyword in sqlite which makes using parametized sql very hard for the queries i'm trying to run
    #http://stackoverflow.com/questions/14512228/sqlalchemy-raw-sql-parameter-substitution-with-an-in-clause

    #We need some way of santizing the SQL.  Make sure that the length of all of the lists is right.  They're all short so this should be relatively secure.


    sql = """
    select country, country_code, product, product_code, port, port_code, sum(quantity) as quantity from
    country_products_port_month
    where country is not null
    and year > '2007'

    {queryconditions}

    group by country, country_code, product, product_code, port, port_code
    limit 100
    """

    sql_done = get_sql(sql, countries_list,ports_list,products_list,dates_list)





    #Need to do more to protect against sql injection attack.

    result = db.session.execute(sql_done)

    return result


def get_timeseries_data(countries_list,ports_list,products_list,dates_list,stack_by):


    #Check html injection on stack_by:
    if stack_by != "port" and stack_by != "country":
        return




    #You can't parametize the in keyword in sqlite which makes using parametized sql very hard for the queries i'm trying to run
    #http://stackoverflow.com/questions/14512228/sqlalchemy-raw-sql-parameter-substitution-with-an-in-clause

    #We need some way of santizing the SQL.  Make sure that the length of all of the lists is right.  They're all short so this should be relatively secure.
    sql = """
    select month, year, {stack_by} as stack_by, sum(quantity) as quantity from 
    country_products_port_month
    where country is not null
    and year > '2007'

    {{queryconditions}}

    group by {stack_by}, month, year
    limit 500
    """

    sql2 = sql.format(stack_by=stack_by)

    sql_done = get_sql(sql2, countries_list,ports_list,products_list,dates_list)



    #Need to do more to protect against sql injection attack.

    result = db.session.execute(sql_done)

    return result


def get_importers_data(countries_list,ports_list,products_list,dates_list):


    d = get_years_months_list(dates_list)
    months_list = d["months_list"]
    years_list = d["years_list"]


    #You can't parametize the in keyword in sqlite which makes using parametized sql very hard for the queries i'm trying to run
    #http://stackoverflow.com/questions/14512228/sqlalchemy-raw-sql-parameter-substitution-with-an-in-clause

    #We need some way of santizing the SQL.  Make sure that the length of all of the lists is right.  They're all short so this should be relatively secure.


    query_dict = {
    "products_list" : {"list": products_list, "sql" : "and e.comcode8 in ({products_list})" } ,
    "months_list" : {"list": months_list, "sql" : "and month_of_import in ({months_list})" } ,
    "years_list" : {"list": years_list, "sql" : "and year_of_import in ({years_list})" } 
    }


    queryconditions = ""
    for key in query_dict:
        check_injection(query_dict[key]["list"])
        query_dict[key]["quotify"] = quotify(query_dict[key]["list"])
        if "All" not in query_dict[key]["quotify"]:

            queryconditions += " " + query_dict[key]["sql"]


    sql = """
    select * from importerseightdigitcodes as e
    left join importers as i
    on i.id = e.importer_id 
    where e.importer_id is not null
    

    {queryconditions}


    limit 500
    """



    sql2 = sql.format(queryconditions=queryconditions)

    format_dict = {k: query_dict[k]["quotify"] for k in query_dict}

    sql3 = sql2.format(**format_dict)


    #Need to do more to protect against sql injection attack.

    result = db.session.execute(sql3)

    return result



import json
def db_result_to_json_in_d3csv_format(dbresult):

    fa = dbresult.fetchall()
    k  = dbresult.keys()

    # fa = [[word.decode("windows-1252") for word in sets] for sets in fa]



    def to_dict(result_row):
        my_tuples = zip(k,result_row)
        my_dict = dict((x,y) for x,y in my_tuples)
        return my_dict

    final = map(to_dict,fa)


    return final


@myapp.route('/' ,methods=["GET","POST"])
def home():

    app = current_app._get_current_object()

    logger.info(app.config["SQLALCHEMY_DATABASE_URI"])
    

    return render_template('home.html')

@myapp.route('/imports', methods=["GET","POST"])
def imports_view():

    return render_template('imports.html')






#All json routes are below
from flask import jsonify

@myapp.route('/importsdata2.json', methods=["GET","POST"])
def get_imports_json2():

    arguments = request.args

    all_arguments_populated = True

    for k in arguments:
        if request.args[k] == "":
            all_arguments_populated = False

    if all_arguments_populated:

        countries_list = arguments.getlist("countries[]")
        ports_list = arguments.getlist("ports[]")
        products_list = arguments.getlist("products[]")
        dates_list = arguments.getlist("dates[]")

        result = get_imports_data2(countries_list,ports_list,products_list,dates_list)
        result = db_result_to_json_in_d3csv_format(result)

    else:
        result =  []


    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp


@myapp.route('/selectboxdata.json', methods=["GET","POST"])
def get_select_box_json():
    result = get_selection_box_data()
    result = db_result_to_json_in_d3csv_format(result)


    resp = jsonify(csv_like_data = result, encoding="windows-1252")
    resp.status_code = 200

    return resp




@myapp.route('/timeseries.json', methods=["GET","POST"])
def get_timeseries_json():



    arguments = request.args

    all_arguments_populated = True

    for k in arguments:
        if request.args[k] == "":
            all_arguments_populated = False

    if all_arguments_populated:

        countries_list = arguments.getlist("countries[]")
        ports_list = arguments.getlist("ports[]")
        products_list = arguments.getlist("products[]")
        dates_list = arguments.getlist("dates[]")
        stack_by = arguments["stack_by"]

        result = get_timeseries_data(countries_list,ports_list,products_list,dates_list, stack_by)
        result = db_result_to_json_in_d3csv_format(result)

        new_results = []

        for this_result in result:

            new_result = {}


            new_result["date"] = datetime.datetime(int(this_result["year"]), int(this_result["month"]), 1).date().isoformat()
            new_result["stack_by"] = this_result["stack_by"]
            new_result["quantity"] = this_result["quantity"]

            new_results.append(new_result)
        result = new_results



    else:
        result =  {}


    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    print resp

    return resp

import re
@myapp.route('/importers.json', methods=["GET","POST"])
def get_importers_json():

    

    arguments = request.args

    all_arguments_populated = True

    for k in arguments:
        if request.args[k] == "":
            all_arguments_populated = False

    if all_arguments_populated:

        countries_list = arguments.getlist("countries[]")
        ports_list = arguments.getlist("ports[]")
        products_list = arguments.getlist("products[]")
        dates_list = arguments.getlist("dates[]")

        result = get_importers_data(countries_list,ports_list,products_list,dates_list)
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

            new_result["date"] = datetime.datetime(int(this_result["year_of_import"]), int(this_result["month_of_import"]), 1).date().isoformat()
            new_result["product"] = this_result["comcode8"]

            new_results.append(new_result)
        result = new_results








    else:
        result =  []


    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp
