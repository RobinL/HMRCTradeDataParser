__author__ = 'Robin'

import json
def db_result_to_json_in_d3csv_format(dbresult):

    """
    Turn results into dict in preparation for jsonifying using the
    keys as column names
    https://www.python.org/dev/peps/pep-0249/#cursor-objects
    """

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


def all_arguments_populated(arguments):
    return_val = True

    for k in arguments:
        if arguments[k] == "":
            return_val = False

    return return_val

def get_join_info_products(cn_code_length):

    lookup = {
        "8": {"join_table": "eightdigitcodes", "product_name_field": "mk_commodity_alpha_all", "join_column": "mk_comcode8"},
        "6": {"join_table": "combined_nomenclature", "product_name_field": "combined_nomenclature_6_desc", "join_column": "combined_nomenclature_6"},
        "4": {"join_table": "combined_nomenclature", "product_name_field": "combined_nomenclature_4_desc", "join_column": "combined_nomenclature_4"},
        "2": {"join_table": "combined_nomenclature", "product_name_field": "combined_nomenclature_2_desc", "join_column": "combined_nomenclature_2"},
        "1": {"join_table": "combined_nomenclature", "product_name_field": "combined_nomenclature_1_desc", "join_column": "combined_nomenclature_1"},
    }

    return lookup[cn_code_length]

