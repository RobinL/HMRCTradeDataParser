__author__ = 'Robin'

def get_fields_df(df, column_name = "Item Name"):
    df = df[~df[column_name].str.upper().str.contains("DELIMITER")]
    df = df[["From","To",column_name]]
    return df