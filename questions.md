#Question 1

The online table generator seems to exclude some "	NATURE - OF TRANSACTION" codes.  For example in the data from June 2015, we see the following records:

030471100|0|600|CY|0|000|  |000|000|0201506|000|03440|000000000|+00000000001|+000000000001208|+0000000000424|+0000000000000
030471100|0|600|CY|0|000|  |001|000|0201506|000|03440|000000000|+00000000001|+000000000004806|+0000000000676|+0000000000000

But in the online table generator, the first record (value £1,208) is omitted, I think because the nature of transaction code is 000 which is "below threshold trade allocations".  I'm not sure why we wouldn't want to know about this transaction though?

#Question 2
Why in some of the EU Dispatches data is the date things like 0991301 and what should I do with these records?

Similarly in the EU Arrivals data some has 0000000

#Question 3
Why in some of te EU data is the date things like 0991301 and what should I do with these records?


#Question 4
EU estimates - if only interested in 4 digit codes and more detailed, do we need this?


#Question 5
On the interactive tables on uktradestatistics, there's the category for 01-- - HS2 Below Threshold Trade.  Where is this in the data?

#Todo
Need to fix the commodity code lookup - add in the comprehennsive list of 8 digit codes