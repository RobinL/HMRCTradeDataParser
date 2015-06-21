from flask import render_template,  url_for, current_app, request
from . import myapp
from . import db




import logging
import traceback
logger = logging.getLogger(__name__)


def get_selection_box_data():

    sql = """

    select distinct  'product' as select_box, mk_comcode8 as key,mk_comcode8 || " -  " || mk_commodity_alpha_all as value
    from eightdigitcodes
    where cast(substr(mk_comcode8,1,2) as integer) < 23 and mk_comcode8 in (select distinct maf_comcode8 from imports)

    union all

    select distinct  'port' as select_box, alpha_code key,port_name as value
    from ports

    union all

    select distinct 'country' as select_box, alpha_code as key, country_name as value
    from countries

    union all

    select distinct 'date' as select_box, maf_account_ccyy || " " || maf_account_mm as key, maf_account_ccyy || " " || maf_account_mm as value
    from imports

    order by select_box, value



    """

    result = db.session.execute(sql)

    return result

def get_imports_data():

    sql = """

    select  country_name as country,mk_commodity_alpha_all as product,e.mk_comcode8 as product_code,  port_name as port,  sum(cast(maf_value as integer)) as quantity
    from imports as i
    left join eightdigitcodes as e
    on i.maf_comcode8 = e.mk_comcode8

    left join countries as c

    on i.maf_coo_alpha = c.alpha_code

    left join ports as p
    on p.alpha_code = i.maf_port_alpha
    where country_name is not null and mk_commodity_alpha_all is not null and port_name is not null and maf_value is not null
    and cast(substr(e.mk_comcode8,1,2) as integer) < 23

    group by country_name, mk_commodity_alpha_all, port_name

    limit 0


    """

    result = db.session.execute(sql)

    return result

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
def get_imports_data2(countries_list,ports_list,products_list,dates_list):




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


    #You can't parametize the in keyword in sqlite which makes using parametized sql very hard for the queries i'm trying to run
    #http://stackoverflow.com/questions/14512228/sqlalchemy-raw-sql-parameter-substitution-with-an-in-clause

    #We need some way of santizing the SQL.  Make sure that the length of all of the lists is right.  They're all short so this should be relatively secure.

    products_all = ""
    countries_all = ""
    ports_all = ""
    months_all = ""
    years_all = ""


    def quotify(my_list):
        return (', '.join('"' + item + '"' for item in my_list))

    def check_no_injection(my_list):
        if len(my_list)>8:
            return

    check_no_injection(years_list)
    check_no_injection(months_list)
    check_no_injection(products_list)
    check_no_injection(ports_list)
    check_no_injection(countries_list)

    years_list = quotify(years_list)
    months_list = quotify(months_list)
    products_list = quotify(products_list)
    ports_list = quotify(ports_list)
    countries_list = quotify(countries_list)




    sql = """
    select  country_name as country,mk_commodity_alpha_all as product,e.mk_comcode8 as product_code,  port_name as port, sum(cast(maf_value as integer)) as quantity
    from imports as i

    left join eightdigitcodes as e
    on i.maf_comcode8 = e.mk_comcode8

    left join countries as c
    on i.maf_coo_alpha = c.alpha_code

    left join ports as p
    on p.alpha_code = i.maf_port_alpha

    where country_name is not null
    and mk_commodity_alpha_all is not null
    and port_name is not null
    and maf_value is not null
    and cast(substr(e.mk_comcode8,1,2) as integer) < 23



    {queryconditions}



    group by country_name, mk_commodity_alpha_all, port_name
    limit 500

    """






    queryconditions = ""
    for i in [[countries_all, countries_list, "and c.alpha_code in ({countries_list})"],
              [ports_all, ports_list, 'and p.alpha_code in ({ports_list})'],
              [products_all, products_list, "and i.maf_comcode8 in ({products_list})"],
              [months_all, months_list, "and i.maf_account_mm in ({months_list})"],
              [years_all,years_list,"and i.maf_account_ccyy in ({years_list})"]]:

        if "All" not in i[1]:

            queryconditions += " " + i[2]

    sql2 = sql.format(queryconditions=queryconditions)

    sql3 = sql2.format(**{"products_list": products_list,
                                      "ports_list": ports_list,
                                      "countries_list": countries_list,
                                      "years_list": years_list,
                                      "months_list": months_list,
                                      })


    #protect against injection attack
    result = db.session.execute(sql3)


    print sql3

    return result

import json
def db_result_to_json_in_d3csv_format(dbresult):

    fa = dbresult.fetchall()
    k  = dbresult.keys()

    def to_dict(result_row):
        my_tuples = zip(k,result_row)
        my_dict = dict((x,y) for x,y in my_tuples)
        return my_dict

    final = map(to_dict,fa)
    print json.dumps(final)
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

@myapp.route('/importsdata.json', methods=["GET","POST"])
def get_imports_json():
    result = get_imports_data()
    result = db_result_to_json_in_d3csv_format(result)


    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp

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
        result =  {"csv_like_data":[]}


    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp


@myapp.route('/selectboxdata.json', methods=["GET","POST"])
def get_select_box_json():
    result = get_selection_box_data()
    result = db_result_to_json_in_d3csv_format(result)


    resp = jsonify(csv_like_data = result)
    resp.status_code = 200

    return resp