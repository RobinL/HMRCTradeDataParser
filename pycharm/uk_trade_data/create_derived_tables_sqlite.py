from my_database import  session

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def create_derived_country_products_month():
    sql = """
    drop table if exists der_{import_or_export}_country_products_port_month_{code_detail};
    create table der_{import_or_export}_country_products_port_month_{code_detail} as
    select  
            country_name as country, 
            c.alpha_code as country_code, 
            {desc_column_name}{code_detail}_desc as product,
            {desc_column_name}{code_detail} as product_code, 
            port_name as port, 
            i_or_e.maf_port_alpha as port_code, 
            i_or_e.maf_account_mm as month, 
            i_or_e.maf_account_ccyy as year, 
            sum(maf_value_int) as quantity

    from {import_or_export} as i_or_e

    left join eightdigitcodes as e
    on i_or_e.comcode8 = e.mk_comcode8

    left join combined_nomenclature as cn

    on e.mk_comcode8 = cn.commodity_code_8

    left join countries as c
    on i_or_e.maf_{coo_or_cod}_alpha = c.alpha_code

    left join ports as p
    on p.alpha_code = i_or_e.maf_port_alpha

    where country_name is not null
    and mk_commodity_alpha_all is not null
    and port_name is not null
    and maf_value_int is not null

    group by country_name, {desc_column_name}{code_detail}_desc, port_name, i_or_e.maf_account_mm , i_or_e.maf_account_ccyy;

    CREATE  INDEX ix_{import_or_export}_cppm_product_code_{code_detail} ON der_{import_or_export}_country_products_port_month_{code_detail} (product_code );
    CREATE  INDEX ix_{import_or_export}_cppm_port_code_{code_detail} ON der_{import_or_export}_country_products_port_month_{code_detail} (port_code );
    CREATE  INDEX ix_{import_or_export}_cppm_country_code_{code_detail} ON der_{import_or_export}_country_products_port_month_{code_detail} (country_code );

    """

    for imp_exp in [("coo","imports"),("cod","exports")]:

        for code_detail in ["1","2","4","6"]:

                sql2 = sql.format(import_or_export = imp_exp[1],
                                    code_detail = code_detail,
                                    desc_column_name = "combined_nomenclature_",
                                    coo_or_cod = imp_exp[0])
                
                sql_list = sql2.split(";")
                for my_sql in sql_list:
                    session.execute(my_sql)

        
        sql2 = sql.format(import_or_export = imp_exp[1],
                            code_detail = 8,
                            desc_column_name = "commodity_code_",
                            coo_or_cod = imp_exp[0])

        sql_list = sql2.split(";")
        for my_sql in sql_list:
            logger.debug(my_sql.replace("\n","")[:100])
            session.execute(my_sql)


def create_derived_select_box():

    sql = """
    drop table if exists der_select_box_values;
    create table der_select_box_values as
    select distinct  'product_8' as select_box, mk_comcode8 as my_key,mk_comcode8 || " -  " || mk_commodity_alpha_all as value
    from eightdigitcodes
    where cast(substr(mk_comcode8,1,2) as integer) < 23 and mk_comcode8 in (select distinct comcode8 from imports)

    union all

    select distinct  'product_6' as select_box, combined_nomenclature_6 as my_key, combined_nomenclature_6 || " -  " || combined_nomenclature_6_desc as value
    from combined_nomenclature
    where cast(substr(combined_nomenclature_6,1,2) as integer) < 23

    union all

    select distinct  'product_4' as select_box, combined_nomenclature_4 as my_key, combined_nomenclature_4 || " -  " || combined_nomenclature_4_desc as value
    from combined_nomenclature
    where cast(substr(combined_nomenclature_4,1,2) as integer) < 23

    union all

    select distinct  'product_2' as select_box, combined_nomenclature_2 as my_key, combined_nomenclature_2 || " -  " || combined_nomenclature_2_desc as value
    from combined_nomenclature

    union all

    select distinct  'product_1' as select_box, combined_nomenclature_1 as my_key, combined_nomenclature_1 || " -  " || combined_nomenclature_1_desc as value
    from combined_nomenclature

    union all

    select distinct  'port' as select_box, alpha_code my_key,port_name as value
    from ports

    union all

    select distinct 'country' as select_box, alpha_code as my_key, country_name as value
    from countries

    union all

    select distinct 'date' as select_box, maf_account_ccyy || " " || maf_account_mm as my_key, maf_account_ccyy || " " || maf_account_mm as value
    from imports

    order by select_box, value

    """
    sql_list = sql.split(";")
    for my_sql in sql_list:
        logger.debug(my_sql.replace("\n","")[:100])
        session.execute(my_sql)


def create_derived_importers_for_web():
    sql = """
    drop table if exists der_importers_for_web; 
   create table der_importers_for_web as

    select
    ia_name, ia_addr_1, ia_addr_2, ia_addr_3,ia_addr_4, ia_addr_5, ia_pcode, month_of_import as month, year_of_import as year,
    e.comcode8 as product_code, lat, lng



     from importerseightdigitcodes as e
        left join importers as i
        on i.id = e.importer_id

    left join 
        postcodes as pc

        on i.postcode_nospace =pc.postcode


        where e.importer_id is not null
        and year_of_import >= '2014'
        order by year_of_import desc, month_of_import desc

        ;

      CREATE  INDEX ix_ifw_product_code ON der_importers_for_web (product_code );
      CREATE  INDEX ix_ifw_month ON der_importers_for_web (month );
       CREATE  INDEX ix_ifw_year ON der_importers_for_web (year );
    """

    sql_list = sql.split(";")
    for my_sql in sql_list:
        logger.debug(my_sql.replace("\n","")[:100])
        session.execute(my_sql)





def create_derived_country_products_month_eu():
    sql = """
    drop table if exists der_{import_or_export}_country_products_month_eu_{code_detail};
    create table der_{import_or_export}_country_products_month_eu_{code_detail} as

    select  c.alpha_code as country_code, cn.{desc_column_name}{code_detail} as product_code,  i.smk_period_reference_month as month, i.smk_period_reference_year as year, sum(smk_stat_value_int) as quantity
   
        from eu_imports as i

        left join eightdigitcodes as e
        on i.comcode8 = e.mk_comcode8

        left join combined_nomenclature as cn

        on e.mk_comcode8 = cn.commodity_code_8

        left join countries as c
        on i.smk_cod_alpha = c.alpha_code



        where country_name is not null
        and mk_commodity_alpha_all is not null
 
        and smk_stat_value_int is not null




        group by country_name, {desc_column_name}{code_detail}_desc,  i.smk_period_reference_month, i.smk_period_reference_year;

    CREATE  INDEX ix_{import_or_export}_cppm_eu_product_code_{code_detail} ON der_{import_or_export}_country_products_month_eu_{code_detail} (product_code );
    CREATE  INDEX ix_{import_or_export}_cppm_eu_country_code_{code_detail} ON der_{import_or_export}_country_products_month_eu_{code_detail} (country_code );
    CREATE  INDEX ix_{import_or_export}_cppm_eu_month{code_detail} ON der_{import_or_export}_country_products_month_eu_{code_detail} (month );
    CREATE  INDEX ix_{import_or_export}_cppm_eu_year{code_detail} ON der_{import_or_export}_country_products_month_eu_{code_detail} (year );

    """



    for imp_exp in ["imports","exports"]:

        for code_detail in ["1","2","4","6"]:

                sql2 = sql.format(import_or_export = imp_exp,
                                    code_detail = code_detail,
                                    desc_column_name = "combined_nomenclature_",
                                    coo_or_cod = imp_exp)

                
                sql_list = sql2.split(";")
                for my_sql in sql_list:
                    session.execute(my_sql)

        
        sql2 = sql.format(import_or_export = imp_exp,
                            code_detail = 8,
                            desc_column_name = "commodity_code_",
                            coo_or_cod = imp_exp)


        sql_list = sql2.split(";")
        for my_sql in sql_list:
            logger.debug(my_sql.replace("\n","")[:100])
            session.execute(my_sql)




if __name__ == "__main__":

    #create_derived_select_box()
    create_derived_country_products_month()
    #create_derived_importers_for_web()
