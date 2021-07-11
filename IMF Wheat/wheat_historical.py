# importing csv module
import csv
import numpy as np
from dateutil import parser
from datetime import datetime
from datetime import timedelta
  
# csv file name
filename = "IMF Wheat/wheatdata.csv"

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)
    
    # skip header row [Date, Price of Wheat/MT]
    next(csvreader) 

    prices = [] # list of historical prices

    historical_cutoff = 20 # how many years back are we considering
    for row in csvreader:
        dte = parser.parse(row[0]) # date of this price
        
        ## append prices after historical cuttoff to our price list
        if(dte > datetime.now() - timedelta(weeks=(52*historical_cutoff))):
            prices.append(float(row[1]))

    percent_gains = [] # list of rolling 5-month % gains
    for i in range(len(prices) - 5):
        percent_gains.append(100*(prices[i+5] - prices[i])/(prices[i]))
    
    np_gains = np.array(percent_gains)
    gains_mean, gains_std = np.mean(np_gains), np.std(np_gains)

    ## run monte carlo simulation for diff buckets using normal sampling
    ## of percentage gain (1+that sample)
    ## RUN X times and categorize probability of each bin
    buckets = [0, 0, 0, 0, 0]
    X = 1000000
    curr_value = 227.44
    for i in range(X):
        
        estimate = (1 + (np.random.normal(gains_mean, gains_std)/100)) * curr_value

        if estimate < 220:
            buckets[0] += 1
        elif estimate < 260:
            buckets[1] += 1
        elif estimate < 300:
            buckets[2] += 1
        elif estimate < 340:
            buckets[3] += 1
        else:
            buckets[4] += 1

probabilities = [round(100*float(occurances)/float(X), 3) for occurances in buckets]
print(probabilities)