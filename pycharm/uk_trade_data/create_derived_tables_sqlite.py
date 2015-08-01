from my_database import  session



def create_derived_country_products_month():
    sql = """
    drop table if exists country_products_port_month_{0};
    create table country_products_port_month_{0} as
    select  country_name as country, c.alpha_code as country_code, {1}{0}_desc as product,cn.{1}{0} as product_code,  port_name as port, i.maf_port_alpha as port_code, i.maf_account_mm as month, i.maf_account_ccyy as year, sum(cast(maf_value as integer)) as quantity
        from imports as i

        left join eightdigitcodes as e
        on i.maf_comcode8 = e.mk_comcode8

        left join combined_nomenclature as cn

        on e.mk_comcode8 = cn.commodity_code_8

        left join countries as c
        on i.maf_coo_alpha = c.alpha_code

        left join ports as p
        on p.alpha_code = i.maf_port_alpha

        where country_name is not null
        and mk_commodity_alpha_all is not null
        and port_name is not null
        and maf_value is not null




        group by country_name, {1}{0}_desc, port_name, i.maf_account_mm , i.maf_account_ccyy;
    CREATE  INDEX ix_cppm_product_code_{0} ON country_products_port_month_{0} (product_code );
    CREATE  INDEX ix_cppm_port_code_{0} ON country_products_port_month_{0} (port_code );
    CREATE  INDEX ix_cppm_country_code_{0} ON country_products_port_month_{0} (country_code );

    """


    for i in ["1","2","4","6"]:

        sql2 = sql.format(i, "combined_nomenclature_")
        sql_list = sql2.split(";")
        for my_sql in sql_list:
            session.execute(my_sql)

    sql2 = sql.format("8", "commodity_code_")
    sql_list = sql2.split(";")
    for my_sql in sql_list:
        session.execute(my_sql)


def create_derived_select_box():

    sql = """

    create table  select_box_values as
    select distinct  'product_8' as select_box, mk_comcode8 as my_key,mk_comcode8 || " -  " || mk_commodity_alpha_all as value
    from eightdigitcodes
    where cast(substr(mk_comcode8,1,2) as integer) < 23 and mk_comcode8 in (select distinct maf_comcode8 from imports)

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
        session.execute(my_sql)



def create_derived_importers_for_web():
    sql = """
   create table importers_for_web as

    select
    ia_name, ia_addr_1, ia_addr_2, ia_addr_3,ia_addr_4, ia_addr_5, ia_pcode, month_of_import as month, year_of_import as year,
    e.comcode8 as product_code

     from importerseightdigitcodes as e
        left join importers as i
        on i.id = e.importer_id
        where e.importer_id is not null
        and year_of_import >= '2014'
        order by year_of_import desc, month_of_import desc

        ;

      CREATE  INDEX ix_ifw_product_code ON importers_for_web (product_code );
      CREATE  INDEX ix_ifw_month ON importers_for_web (month );
       CREATE  INDEX ix_ifw_year ON importers_for_web (year );
    """

    sql_list = sql.split(";")
    for my_sql in sql_list:
        session.execute(my_sql)




def create_derived_importers_for_web():
    sql = """
   create table importers_for_web as

    select
    ia_name, ia_addr_1, ia_addr_2, ia_addr_3,ia_addr_4, ia_addr_5, ia_pcode, month_of_import as month, year_of_import as year,
    e.comcode8 as product_code

     from importerseightdigitcodes as e
        left join importers as i
        on i.id = e.importer_id
        where e.importer_id is not null
        and year_of_import >= '2014'
        order by year_of_import desc, month_of_import desc

        ;

      CREATE  INDEX ix_ifw_product_code ON importers_for_web (product_code );
      CREATE  INDEX ix_ifw_month ON importers_for_web (month );
       CREATE  INDEX ix_ifw_year ON importers_for_web (year );
    """

    sql_list = sql.split(";")
    for my_sql in sql_list:
        session.execute(my_sql)

if __name__ == "__main__":

    #create_derived_select_box()
    create_derived_country_products_month()
    #create_derived_importers_for_web()


def create_derived_importers_for_web2():
    sql = """
   create table importers_for_web2 as

    select
    ia_name, ia_addr_1, ia_addr_2, ia_addr_3,ia_addr_4, ia_addr_5, ia_pcode, month_of_import as month, year_of_import as year,
    e.comcode8 as product_code, lat, lng
    replace("ia_pcode"," ", "") as nospace 


     from importerseightdigitcodes as e
        left join importers as i
        on i.id = e.importer_id

    left join 
        postcodes as pc

        on nospace =pc.postcode


        where e.importer_id is not null
        and year_of_import >= '2014'
        order by year_of_import desc, month_of_import desc

        ;

      CREATE  INDEX ix_ifw_product_code ON importers_for_web2 (product_code );
      CREATE  INDEX ix_ifw_month ON importers_for_web2 (month );
       CREATE  INDEX ix_ifw_year ON importers_for_web2 (year );
    """

    sql_list = sql.split(";")
    for my_sql in sql_list:
        session.execute(my_sql)

if __name__ == "__main__":

    #create_derived_select_box()
    create_derived_country_products_month()
    #create_derived_importers_for_web()