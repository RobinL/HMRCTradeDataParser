
##Exports

###8 digit code checks

####19053199 

Total from truth table 2014: 46741673

    select sum(maf_value_int) from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,8) = "19053199"

Total from database = 46741673

###6 digit code checks

####190531

Total from truth table 2014: 138815094

    select sum(maf_value_int) from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,5) = "190531"

Total from database = 138815094

###4 digit code checks

####1905

Total from truth table 2014:  257890305


    select sum(maf_value_int) from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,4) = "1905"

Total from database = 257890305

###2 digit code checks

####19


Total from truth table 2014:  487951662


    select sum(maf_value_int) from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,2) = "19"

Total from database = 487951662


###Everything check

Total from truth table 2014: 163578678181

    select sum(maf_value_int) from exports
    where 
    maf_account_ccyy = 2014  


Total from database = 167882089996  __error__

Break down by countries.

We find that every country matches except for:

- NO (Difference betweeen BYOT and database)
- QX  (In database but not in BYOT)
- YT (In database but not in BYOT)  Note that YT is supposed to be Mayotte
- ZN (In database but not in BYOT)

##Imports

###8 digit code checks

####19053199 

Total from truth table 2014: 4117827
 
    select sum(maf_value_int) from imports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,8) = "19053199"

-> 4142168

No match


    select sum(maf_value_int) 
    from imports
    where maf_account_ccyy = 2014  
    and comcode8 = "19053199"
    and  maf_trade_indicator <5

-> 4117827

Note that there are various ways to get to here including `where trim(maf_port_alpha) != ""` and `where maf_mode_of_transport != "000"` but the trade indicator filter seems to be the correct one 

The reason seems to be to do with the SUITE is used in conjunction with TRADEIND to compile General and Special trade. See Section 3 General and Special Trade. 

"There are two recognised systems for recording trade – the ‘general trade’ system and the ‘special trade’ system. General trade is the definition used by HMRC and the ONS to compile UK trade statistics. Special trade is the definition used by Eurostat to compile Community trade statistics. 

The UK Overseas Trade Statistics (OTS) are compiled in accordance with the general trade system of recording (as described in the IMTS). They comprise all merchandise crossing the national boundary of the UK including goods imported into and exported from Customs warehouses and free zones. "

###6 digit code checks

####190531

Total from truth table 2014: 8167337

    select sum(maf_value_int) 
    from imports
    where maf_account_ccyy = 2014  
    and substr(comcode8,1,6) = "190531"
    and  maf_trade_indicator <5

-> 8167337


###4 digit code checks

####1905

Total from truth table 2014: 114332545

    select sum(maf_value_int) 
    from imports
    where maf_account_ccyy = 2014  
    and substr(comcode8,1,4) = "1905"
    and  maf_trade_indicator < 5
    

-> 114332545

###2 digit code checks

####19

Total from truth table 2014: 209318239

    
    select sum(maf_value_int) 
    from imports
    where maf_account_ccyy = 2014  
    and substr(comcode8,1,2) = "19"
    and  maf_trade_indicator < 5


-> 209318239

###Everything check

Total from truth table 2014:  199114761180

    
    select sum(maf_value_int) 
    from imports
    where maf_account_ccyy = 2014  
    and  maf_trade_indicator < 5


-> 204812417254.  __error__


What's the problem here?

Breaking down the figures by country:

    select sum(maf_value_int), maf_cod_alpha 
    from imports
    where maf_account_ccyy = 2014  
    and  maf_trade_indicator <5
    group by maf_cod_alpha

we find that every country matches except three:

ZN QX and NO.

Using [the code definitions]("https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2") we can see that:

- ZN is unassigned
- QX is 'user assigned'; and
- NO is Norway

To get from the results from the SQL table (204812417254) to the result in the truth table (199114761180) we can do the following:

Filter out ZN and QX from the SQL results.  Replace the SQL result for Norway (2860064117) with the truth table result (17203777510).



#EU Exports

    --Want 74046711
    select sum(smk_stat_value_int) from
    eu_exports where 
    smk_period_reference_year = 2014 and 
    comcode8 = "19053199"
    
-> 74063389

Fields crosstabbed:

smk_nature_of_transaction
smk_mode_of_transport
smk_record_type
smk_cod_alpha
smk_coo_alpha



##6 digit code checks

###190531