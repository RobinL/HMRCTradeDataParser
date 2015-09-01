__author__ = 'Robin'

import pandas as pd
import sqlite3
import json

def find_element(children_list,name):
    """
    Find element in children list
    if exists or return none
    """
    for i in children_list:
        if i["name"] == name:
            return i
    #If not found return None
    return None

def add_node(levels,row, value_field, nest):
    """
    The path is a list.  Each element is a name that corresponds
    to a level in the final nested dictionary.
    """

    #Get first name from level
    this_level = levels.pop(0)
    this_name = row[this_level["name"]]

    level_properties = this_level["properties"]

    #Does the element exist already?
    element = find_element(nest["children"], this_name)

    #If the element exists, we can use it, otherwise we need to create a new one
    if element:


        if len(levels)>0:
            add_node(levels, row, value_field, element)

    #Else it does not exist so create it and return its children
    else:
        new_child ={"name":this_name}
        for prop, rowkey in level_properties.iteritems():
            new_child[prop] = row[rowkey]

        if len(levels) == 0:

            new_child["value"] = row[value_field]
            nest["children"].append(new_child)
        else:
            #Add new element

            new_child["children"] = []
            nest["children"].append(new_child)

            #Get added element
            element = nest["children"][-1]

            #Still elements of path left so recurse
            add_node(levels, row, value_field, element)


def make_single_json(table_name, root_name, json_file_name):

    conn = sqlite3.connect(r"..\..\..\pycharm\trade_data.db")

    sql = """
    select
        code8,
        code6,
        code4,
        code2,
        l1.code as code1,
        l1.code_base as code0,
        mk_commodity_alpha_all as desc8,
        l6.desc as desc6,
        l4.desc as desc4,
        l2.desc as desc2,
        l1.desc as desc1,
        l1.desc_base as desc0,
        quantity
    from
        (select
            product_code as code8,
            substr(product_code,1,6) as code6,
            substr(product_code,1,4) as code4,
            substr(product_code,1,2) as code2,
            sum(quantity) as quantity
        from
            {}
        where year = 2014
        group by product_code)

        as s

    left join eightdigitcodes as l8
    on s.code8 = l8.mk_comcode8

    left join lookup_codes_6 as l6
    on s.code6 = l6.code

    left join lookup_codes_4 as l4
    on s.code4 = l4.code

    left join lookup_codes_2 as l2
    on s.code2 = l2.code

    left join lookup_codes_1 as l1
    on s.code2 = l1.code_2
    """

    df_all = pd.read_sql(sql.format(table_name), conn)

    d_all = {"name": root_name,
             "desc": "*",
    "children": []}


    my_levels = [{"name": "code0",
               "properties" : {"desc":"desc0"}},
             {"name": "code1",
               "properties" : {"desc":"desc1"}},
             {"name": "code2",
               "properties" : {"desc":"desc2"}},
             {"name": "code4",
               "properties" : {"desc":"desc4"}},
             {"name": "code6",
               "properties" : {"desc":"desc6"}},
             {"name": "code8",
               "properties" : {"desc":"desc8"}}]
               
    for row in df_all.iterrows():
        r = row[1]
        value_field = "quantity"
        levels_info = [i for i in my_levels]
        add_node(levels_info, r, value_field,d_all)

    with open('../static/treemap_{}.json'.format(table_name), 'w') as outfile:
        json.dump(d_all, outfile)

def make_all_json():
    
    make_single_json("der_exports_country_products_month_eu_8", "eu_exports","eu_exports")
    make_single_json("der_imports_country_products_month_eu_8", "eu_imports","eu_imports")
    make_single_json("der_exports_country_products_port_month_8", "exports","exports")
    make_single_json("der_imports_country_products_port_month_8", "imports","imports")

if __name__ == "__main__":
    make_all_json()