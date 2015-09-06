from my_database import  session

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# and cast(substr(i_or_e.comcode8,1,2) as integer) < 23
def create_derived_country_products_month():
    sql = """
    drop table if exists der_{import_or_export}_country_products_port_month_{code_detail};
    create table der_{import_or_export}_country_products_port_month_{code_detail} as

    select  
        i_or_e.maf_{coo_or_cod}_alpha as country_code, 
        substr(i_or_e.comcode8,1,{code_detail}) as product_code, 
        maf_port_alpha as port_code, 
        i_or_e.maf_account_mm as month, 
        i_or_e.maf_account_ccyy as year, 
        sum(maf_value_int) as quantity

    from {import_or_export} as i_or_e

    where
    maf_value_int is not null

    and product_code is not null
    and country_code is not null

    group by country_code, product_code, port_code,  i_or_e.maf_account_mm, i_or_e.maf_account_ccyy;

    CREATE  INDEX ix_{import_or_export}_cppm_product_code_{code_detail} 
        ON der_{import_or_export}_country_products_port_month_{code_detail} (product_code );
        
    CREATE  INDEX ix_{import_or_export}_cppm_port_code_{code_detail} 
        ON der_{import_or_export}_country_products_port_month_{code_detail} (port_code );
        
    CREATE  INDEX ix_{import_or_export}_cppm_country_code_{code_detail} 
        ON der_{import_or_export}_country_products_port_month_{code_detail} (country_code );
        
    CREATE  INDEX ix_{import_or_export}_cppm_month_{code_detail} 
        ON der_{import_or_export}_country_products_port_month_{code_detail} (month );
        
    CREATE  INDEX ix_{import_or_export}_cppm_year_{code_detail} 
        ON der_{import_or_export}_country_products_port_month_{code_detail} (year);

    """

    for imp_exp in ["imports","exports"]:

        for code_detail in ["2","4","6", "8"]:

            if imp_exp == "imports": coo_or_cod = "cod"
            if imp_exp == "exports": coo_or_cod = "cod"


            sql2 = sql.format(import_or_export = imp_exp,
                                code_detail = code_detail,
                                coo_or_cod = coo_or_cod)


            sql_list = sql2.split(";")
            for my_sql in sql_list:
                logger.debug(my_sql.replace("\n","")[:100])
                session.execute(my_sql)


    for imp_exp in ["imports","exports"]:
        #Special case of one digit code
        coo_or_cod = "cod"

        sql = """
        drop table if exists der_{import_or_export}_country_products_port_month_1;
        create table der_{import_or_export}_country_products_port_month_1 as

        select
            i_or_e.maf_{coo_or_cod}_alpha as country_code,
            lk.code as product_code,
            maf_port_alpha as port_code,
            i_or_e.maf_account_mm as month,
            i_or_e.maf_account_ccyy as year,
            sum(maf_value_int) as quantity

            from {import_or_export} as i_or_e

        left join lookup_codes_1 as lk

        on substr(i_or_e.comcode8,1,2)  = lk.code_2





        where
        maf_value_int is not null

        and product_code is not null
        and country_code is not null

        group by country_code, product_code, port_code,  i_or_e.maf_account_mm, i_or_e.maf_account_ccyy;

        CREATE  INDEX ix_{import_or_export}_cppm_product_code_1
            ON der_{import_or_export}_country_products_port_month_1 (product_code );

        CREATE  INDEX ix_{import_or_export}_cppm_port_code_1
            ON der_{import_or_export}_country_products_port_month_1 (port_code );

        CREATE  INDEX ix_{import_or_export}_cppm_country_code_1
            ON der_{import_or_export}_country_products_port_month_1 (country_code );

        CREATE  INDEX ix_{import_or_export}_cppm_month_1
            ON der_{import_or_export}_country_products_port_month_1 (month );

        CREATE  INDEX ix_{import_or_export}_cppm_year_1
            ON der_{import_or_export}_country_products_port_month_1 (year);

        """

        sql2 = sql.format(import_or_export = imp_exp,
                    code_detail = code_detail,
                    coo_or_cod = coo_or_cod);
        
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

    select distinct 'product_6' as select_box, code as my_key, code || " -  " || desc as value
    from lookup_codes_6
    where cast(substr(code,1,2) as integer) < 23

    union all

    select distinct 'product_4' as select_box, code as my_key, code || " -  " || desc as value
    from lookup_codes_4
    where cast(substr(code,1,2) as integer) < 23

    union all

    select distinct 'product_2' as select_box, code as my_key, code || " -  " || desc as value
    from lookup_codes_2
    where cast(substr(code,1,2) as integer) < 23

    union all

    select * from 
    (select distinct 'product_1' as select_box, code as my_key, code || " -  " || desc as value
    from lookup_codes_1
    where cast(substr(code,1,2) as integer) < 23
    order by cast(my_key as integer) )

    union all

    select distinct  'port' as select_box, alpha_code my_key,port_name as value
    from ports

    union all

    select distinct 'country' as select_box, alpha_code as my_key, country_name as value
    from countries

    union all

    select distinct 'date' as select_box, maf_account_ccyy || " " || maf_account_mm as my_key, maf_account_ccyy || " " || maf_account_mm as value
    from imports

    order by select_box

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




#       and cast(substr(comcode8,1,2) as integer) < 23
def create_derived_country_products_month_eu():
    sql = """
    drop table if exists der_{import_or_export}_country_products_month_eu_{code_detail};
    create table der_{import_or_export}_country_products_month_eu_{code_detail} as

    select  smk_cod_alpha as country_code, 
        substr(i_or_e.comcode8,1,{code_detail}) as product_code, 
        i_or_e.smk_period_reference_month as month, 
        i_or_e.smk_period_reference_year as year, 
        sum(smk_stat_value_int) as quantity
   
    from eu_{import_or_export} as i_or_e



    group by 
        country_code, 
        product_code, 
        i_or_e.smk_period_reference_month, 
        i_or_e.smk_period_reference_year;

    CREATE  INDEX ix_{import_or_export}_cppm_eu_product_code_{code_detail} 
        ON der_{import_or_export}_country_products_month_eu_{code_detail} (product_code );

    CREATE  INDEX ix_{import_or_export}_cppm_eu_country_code_{code_detail} 
        ON der_{import_or_export}_country_products_month_eu_{code_detail} (country_code );

    CREATE  INDEX ix_{import_or_export}_cppm_eu_month{code_detail} 
        ON der_{import_or_export}_country_products_month_eu_{code_detail} (month );

    CREATE  INDEX ix_{import_or_export}_cppm_eu_year{code_detail} 
        ON der_{import_or_export}_country_products_month_eu_{code_detail} (year );
    """

    for imp_exp in ["imports","exports"]:

        for code_detail in ["2","4","6", "8"]:

                sql2 = sql.format(import_or_export = imp_exp,
                                    code_detail = code_detail,
                                    desc_column_name = "combined_nomenclature_",
                                    coo_or_cod = imp_exp)

                if code_detail == "8":
                    sql2 = sql2.replace("cn.combined_nomenclature_8", "comcode8")

                sql_list = sql2.split(";")
                for my_sql in sql_list:
                    logger.debug(my_sql.replace("\n","")[:100])
                    session.execute(my_sql)


    for imp_exp in ["imports","exports"]:
        #Special case of one digit code
        coo_or_cod = "cod"

        sql = """
        drop table if exists der_{import_or_export}_country_products_month_eu_1;
        create table der_{import_or_export}_country_products_month_eu_1 as

        select  smk_cod_alpha as country_code, 
            lk.code as product_code, 
            i_or_e.smk_period_reference_month as month, 
            i_or_e.smk_period_reference_year as year, 
            sum(smk_stat_value_int) as quantity
        
        from eu_{import_or_export} as i_or_e

        left join lookup_codes_1 as lk

        on substr(i_or_e.comcode8,1,2)  = lk.code_2

        group by country_code, product_code,   i_or_e.smk_period_reference_month, i_or_e.smk_period_reference_year;

  CREATE  INDEX ix_{import_or_export}_cppm_eu_product_code_1
        ON der_{import_or_export}_country_products_month_eu_1 (product_code );

    CREATE  INDEX ix_{import_or_export}_cppm_eu_country_code_1
        ON der_{import_or_export}_country_products_month_eu_1 (country_code );

    CREATE  INDEX ix_{import_or_export}_cppm_eu_month1
        ON der_{import_or_export}_country_products_month_eu_1 (month );

    CREATE  INDEX ix_{import_or_export}_cppm_eu_year1
        ON der_{import_or_export}_country_products_month_eu_1 (year );

        """

        sql2 = sql.format(import_or_export = imp_exp,
                    code_detail = code_detail,
                    coo_or_cod = coo_or_cod);
        
        sql_list = sql2.split(";")
        for my_sql in sql_list:
            logger.debug(my_sql.replace("\n","")[:100])
            session.execute(my_sql)


if __name__ == "__main__":
    create_derived_country_products_month()