
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


Note:
    
    select * from (
    select comcode8
    from exports
    where maf_cod_alpha = "QX") as x
    left join eightdigitcodes as e
    on c	omcode8 = e.mk_comcode8

returns some comcodes associated with these 'countries'.  85269200 is a good example

Note if we use BYOT on 8526 we get a message: 
>"Suppression applies to this product code – see suppression metadata"

Note that the aggregation still works though. 

But note that if we choose a ZN code (e.g. 85442000) we get data as expected.

>Question what's the difference between QX and ZN

>Question.  When you BYOT 85 you get different numbers from the database.  Code ZN makes up the difference! In BYOT it seems like somehow ZN is put back into the countries somehow.  So the total is right but the country breakdown is wrong.  THIS MEANS THAT ZN SHOULD BE INCLUDED.


###Further 2 digit code checks - for 2 digit codes that feature include entries for QX and ZN?

####85

Total from truth table 2014: 9318174398

    select sum(maf_value_int) from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,2) = "85"

-> 9318174398

But 

    select sum(maf_value_int), maf_cod_alpha from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,2) = "85"
    group by maf_cod_alpha

On an individual country basis there are differences.  Take Afghanistan
 
Afghanistan from truth table 2014: 6379658

    select sum(maf_value_int), maf_cod_alpha from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,2) = "85"
    and maf_cod_alpha  = "AF"
    group by maf_cod_alpha

-> 6378194

Somehow the 3832497 that is assigned to code ZN in the raw data is assigned to individual countries in the BYOT.

####Let's just check that the four digit aggregations also work

####8526

Total from truth table 2014: 270231579

    select sum(maf_value_int) from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,4) = "8526"
 
->270231579


####8544

Total from truth table 2014: 478219350

    select sum(maf_value_int) from exports
    where 
    maf_account_ccyy = 2014  
    and substr(comcode8,1,4) = "8544"

478219350


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

###8 digit code checks

####19053199 

Total from truth table 2014:  74046711

    select sum(smk_stat_value_int) from
    eu_exports where 
    smk_period_reference_year = 2014 and 
    comcode8 = "19053199"
    
-> 74046711


##6 digit code checks

###190531


Total from truth table 2014:  162454037


    select sum(smk_stat_value_int) from
    eu_exports where 
    smk_period_reference_year = 2014 and 
    substr(comcode8,1,6) = "190531"

-> 162454037


##4 digit code checks

###1905

Total from truth table 2014: 539186226

    select sum(smk_stat_value_int) from
    eu_exports where 
    smk_period_reference_year = 2014 and 
    substr(comcode8,1,4) = "1905"

->539186226

##2 digit code checks

###19


Total from truth table 2014: 999834338

    select sum(smk_stat_value_int) from
    eu_exports where 
    smk_period_reference_year = 2014 and 
    substr(comcode8,1,2) = "19"

999072011

Note that the estimates are 762327 from BYOT and this makes up the difference.

The difference between the two is the estimates - but note these cannot be derived from the raw data.  

> Question:  Is it possible to derive the estimates?  If not, what is wrong with the aggregations?:


##Everything
 
Total from truth table 2014: 146896310324


    select sum(smk_stat_value_int) from
    eu_exports where 
    smk_period_reference_year = 2014  
 
150599318277


Estimates: 231785782

> Cannot match this figure.  Grouping by `smk_trade_ind`	and `smk_record_type` doesn't work. `smk_record_type` gets very close making adjustments for estimates and removing recordtype 3.  But doesn't equal the figure exactly 146664524542 vs 146682462126 so out by £17,937,584.  I can't find this £17m figure associated with any comcodes or anything like that.




#EU Imports

###8 digit code checks

####19053199 
Total from truth table 2014: 115598569


    select sum(smk_stat_value_int) from
    eu_imports where 
    smk_period_reference_year = 2014 and 
    comcode8 = "19053199"

115598569
	

###6 digit code checks

####190531

Total from truth table 2014:  301357897


    select sum(smk_stat_value_int) from
    eu_imports where 
    smk_period_reference_year = 2014 and 
    substr(comcode8,1,6) = "190531"

301357897

###4 digit code checks

####1905

Total from truth table 2014: 1454048223

    select sum(smk_stat_value_int) from
    eu_imports where 
    smk_period_reference_year = 2014 and 
    substr(comcode8,1,4) = "1905"

-> 1454048223

Note (for later) that there are no recordtype = 3 in here.


###2 digit code checks

####19

Total from truth table 2014:2462045169.  Minus the estimates which are not available in the dataset:  2456331638


    select sum(smk_stat_value_int) from
    eu_imports where 
    smk_period_reference_year = 2014 and 
    substr(comcode8,1,4) = "19"

2456331638	

###Everything


Total from truth table 2014: 222331490807
Minus 970524427 estimates = 221360966380

    select sum(smk_stat_value_int)  from
    eu_imports where 
    smk_period_reference_year = 2014  

-> 223884855535

Again, removing recordtype 3 gets very close -  to 221391225018 which is 0.014% off the real answer

