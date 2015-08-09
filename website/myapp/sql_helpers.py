__author__ = 'Robin'

def quotify_list(my_list):
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


#This code gets a suitable 'where' condition
def get_where_query_part(countries_list=None,ports_list=None,products_list=None,dates_list=None):

    query_dict = {}

    if countries_list:
        query_dict["countries_list"] = {"list": countries_list, "sql" : "and country_code in ({countries_list})"}

    if ports_list:
        query_dict["ports_list"] = {"list": ports_list, "sql" : "and port_code in ({ports_list})"}

    if products_list:
        query_dict["products_list"] = {"list": products_list, "sql" : "and product_code in ({products_list})" }


    queryconditions = ""

    for key in query_dict:
        check_injection(query_dict[key]["list"])
        query_dict[key]["quotify"] = quotify_list(query_dict[key]["list"])
        if "All" not in query_dict[key]["quotify"]:

            queryconditions += " " + query_dict[key]["sql"]


    if dates_list:
        d = get_years_months_list(dates_list)
        months_list = d["months_list"]
        years_list = d["years_list"]


    if dates_list and "All" not in months_list:

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



    sql2 = queryconditions

    format_dict = {k: query_dict[k]["quotify"] for k in query_dict}

    sql3 = sql2.format(**format_dict)

    return sql3


if __name__ == "__main__":
    print get_where_query_part(countries_list=["c_1","c_2"])
    print get_where_query_part(countries_list=["c_1","c_2"], dates_list=["2015 06", "2104 05"])

