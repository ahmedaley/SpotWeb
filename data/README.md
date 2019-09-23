# The Data Files

1- CurrentPricePerReq.csv contains the data for the price of the different spot VM markets normalized per request monitored over a period 
of over 2 months. To get this value, we divide the VM spot price by the total number of requests that this VM can handle.
FullCurrentPrice.csv containes the price of the per VM price for the spot markets

2- failureProbability is the probability of failure for each VM instance based on the values posted by AWS here: https://aws.amazon.com/ec2/spot/instance-advisor/
We note that we ran a script to pull the probabilities every hour. In general, we can see that the failure probability is quite stable.

3- AggReq.out contains the total number of requests on Wikipedia over a period of 5 years. This data is based on the data logged here
https://dumps.wikimedia.org/other/pagecounts-ez/

4- requestsCapacity.csv contains the maximum number of Wikipedia requests each VM type can serve.


