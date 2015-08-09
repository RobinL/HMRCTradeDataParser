__author__ = 'Robin'


from . import db
from sql_helpers import get_where_query_part
from other_helpers import db_result_to_json_in_d3csv_format
import datetime

def get_selection_box_data(type = ""):

    sql = """
    select select_box, my_key, value
    from der_select_box_values
    {where}
    """

    if type != "":
        where = "where select_box = '{}'".format(type)
    else:
        where = ""

    result = db.session.execute(sql.format(where=where))

    return result

from other_helpers import get_join_info_products
def get_eu_data(arguments,importexport):

    countries_list = arguments.getlist("countries[]")
    products_list = arguments.getlist("products[]")
    dates_list = arguments.getlist("dates[]")
    cn_code_length = arguments["cn_code_length"]

    #Depending on the whether it's an 8,6,4,2,or 1 ditit code, we will need to do different joins
    join_info_products = get_join_info_products(cn_code_length)
    product_desc_field = join_info_products["product_name_field"]
    product_join_field = join_info_products["join_column"]
    product_join_table = join_info_products["join_table"]

    sql = """
    select c.country_name as country, country_code, pjt.{product_desc_field} as product, pjt.{product_join_field} as product_code, sum(quantity) as quantity from
    der_{imports_or_exports}_country_products_month_eu_{cn_code_length} as main

    left join {product_join_table} as pjt
    on
    main.product_code = pjt.{product_join_field}


    left join countries as c on
    main.country_code = c.alpha_code



    where country is not null
    and year > '2007'

    {{queryconditions}}

    group by country, country_code, product, product_code
    limit 1000
    """


    sql = sql.format(cn_code_length=cn_code_length,
                     imports_or_exports=importexport,
                     product_desc_field = product_desc_field,
                     product_join_field = product_join_field,
                     product_join_table=product_join_table)


    queryconditions = get_where_query_part(countries_list=countries_list,products_list=products_list,dates_list=dates_list)
    sql = sql.format(queryconditions=queryconditions)

    #Need to do more to protect against sql injection attack.

    result = db.session.execute(sql)

    return result

def get_non_eu_data(arguments,importexport):

    #You can't parametize the in keyword in sqlite which makes using parametized sql very hard for the queries i'm trying to run
    #http://stackoverflow.com/questions/14512228/sqlalchemy-raw-sql-parameter-substitution-with-an-in-clause

    #We need some way of santizing the SQL.  Make sure that the length of all of the lists is right.  They're all short so this should be relatively secure.

    countries_list = arguments.getlist("countries[]")
    ports_list = arguments.getlist("ports[]")
    products_list = arguments.getlist("products[]")
    dates_list = arguments.getlist("dates[]")
    cn_code_length = arguments["cn_code_length"]

    #Depending on the whether it's an 8,6,4,2,or 1 ditit code, we will need to do different joins
    join_info_products = get_join_info_products(cn_code_length)
    product_desc_field = join_info_products["product_name_field"]
    product_join_field = join_info_products["join_column"]
    product_join_table = join_info_products["join_table"]


    sql = """
    select c.country_name as country,
    country_code,
    pjt.{product_desc_field} as product,
    pjt.{product_join_field} as product_code,
    p.port_name as port,
    port_code,
    sum(quantity) as quantity

    from

    der_{imports_or_exports}_country_products_port_month_{cn_code_length} as main

    left join {product_join_table} as pjt
    on
    main.product_code = pjt.{product_join_field}


    left join countries as c on
    main.country_code = c.alpha_code

    left join ports as p on
    main.port_code = p.alpha_code


    where country is not null
    and port is not null
    and year > '2007'

    {{queryconditions}}

    group by country, country_code, product, product_code, port, port_code
    limit 1000
    """

    # sql = """
    # select country, country_code, product, product_code, port, port_code, sum(quantity) as quantity from
    # der_{imports_or_exports}_country_products_port_month_{cn_code_length}
    # where country is not null
    # and year > '2007'
    #
    # {{queryconditions}}
    #
    # group by country, country_code, product, product_code, port, port_code
    # limit 1000
    # """


    sql = sql.format(cn_code_length=cn_code_length,
                     imports_or_exports=importexport,
                     product_desc_field = product_desc_field,
                     product_join_field = product_join_field,
                     product_join_table=product_join_table)



    queryconditions = get_where_query_part(countries_list,ports_list,products_list,dates_list)
    sql = sql.format(queryconditions=queryconditions)

    print sql

    #Need to do more to protect against sql injection attack.

    result = db.session.execute(sql)

    return result


def get_non_eu_timeseries_data(arguments,importexport):

    countries_list = arguments.getlist("countries[]")
    ports_list = arguments.getlist("ports[]")
    products_list = arguments.getlist("products[]")
    dates_list = arguments.getlist("dates[]")
    stack_by = arguments["stack_by"]
    cn_code_length = arguments["cn_code_length"]

    #Check html injection on stack_by:
    if stack_by not in ["port", "country", "product_code"]:
        return

    stack_by_lookup = {"port":"p.port_name",
                       "country": "c.country_name",
                       "product_code":"product_code"}

    #You can't parametize the in keyword in sqlite which makes using parametized sql very hard for the queries i'm trying to run
    #http://stackoverflow.com/questions/14512228/sqlalchemy-raw-sql-parameter-substitution-with-an-in-clause

    sql = """
    select month, year, {stack_by} as stack_by, sum(quantity) as quantity from
    der_{importexport}_country_products_port_month_{cn_code_length} as main


    left join countries as c on
    main.country_code = c.alpha_code

    left join ports as p on
    main.port_code = p.alpha_code

    where country_code is not null
    and year > '2007'

    {{queryconditions}}

    group by {stack_by}, month, year
    limit 500
    """

    sql = sql.format(stack_by=stack_by_lookup[stack_by], cn_code_length=cn_code_length, importexport=importexport)

    queryconditions = get_where_query_part(countries_list,ports_list,products_list,dates_list)

    sql = sql.format(queryconditions=queryconditions)


    result = db.session.execute(sql)

    result = db_result_to_json_in_d3csv_format(result)

    new_results = []

    for this_result in result:

        new_result = {}
        new_result["date"] = datetime.datetime(int(this_result["year"]), int(this_result["month"]), 1).date().isoformat()
        new_result["stack_by"] = this_result["stack_by"]
        new_result["quantity"] = this_result["quantity"]

        new_results.append(new_result)

    return new_results


def get_importers_data(codes):

    if len(codes) ==0:
        return []

    codes = ["product_code = '{}'".format(c) for c in codes]

    sql = """
    select  * from der_importers_for_web
    where {}
    limit 1000
    """

    wherecondition = " or ".join(codes)

    sql_done = sql.format(wherecondition)



    #Need to do more to protect against sql injection attack.

    result = db.session.execute(sql_done)

    return result


def db_result_to_json_in_d3csv_format(dbresult):

    fa = dbresult.fetchall()
    k  = dbresult.keys()

    def decode_if_str(word):
        if type(word)==str:
            return word.decode("windows-1252")
        else:
            return word


    fa = [[decode_if_str(word) for word in sets] for sets in fa]



    def to_dict(result_row):
        my_tuples = zip(k,result_row)
        my_dict = dict((x,y) for x,y in my_tuples)
        return my_dict

    final = map(to_dict,fa)


    return final