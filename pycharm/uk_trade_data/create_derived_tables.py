

sql = """
drop table if exists country_products_port_month;

create table country_products_port_month as 
select  country_name as country, c.alpha_code as country_code, mk_commodity_alpha_all as product,e.mk_comcode8 as product_code,  port_name as port, i.maf_port_alpha as port_code, i.maf_account_mm as month, i.maf_account_ccyy as year, sum(cast(maf_value as integer)) as quantity
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



    group by country_name, mk_commodity_alpha_all, port_name, i.maf_account_mm , i.maf_account_ccyy;

CREATE  INDEX ix_cppm_product_code ON country_products_port_month (product_code );
CREATE  INDEX ix_cppm_port_code ON country_products_port_month (port_code );
CREATE  INDEX ix_cppm_country_code ON country_products_port_month (country_code );

"""


sql = """
    create table  select_box_values as
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


sql_server = """
    
    select distinct  'product' as select_box, mk_comcode8 as my_key,mk_comcode8 + ' -  ' + mk_commodity_alpha_all as value
    
    into select_box_values 
    from eightdigitcodes
    where cast(substring(mk_comcode8,1,2) as integer) < 23 and mk_comcode8 in (select distinct maf_comcode8 from imports)

    union 

    select distinct  'port' as select_box, alpha_code my_key,port_name as value
    from ports

    union 

    select distinct 'country' as select_box, alpha_code as my_key, country_name as value
    from countries

    union 

    select distinct 'date' as select_box, maf_account_ccyy + ' ' + maf_account_mm as my_key, maf_account_ccyy + ' ' + maf_account_mm as value
    from imports

    order by select_box, value

    """