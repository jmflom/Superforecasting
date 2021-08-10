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

    historical_cutoff = 5 # how many years back are we considering
    for row in csvreader:
        dte = parser.parse(row[0]) # date of this price
        
        ## append prices after historical cuttoff to our price list
        if(dte > datetime.now() - timedelta(weeks=(52*historical_cutoff))):
            prices.append(float(row[1]))

percent_gains_fourmo = [] # list of rolling 5-month % gains (jul, aug, sep, oct, nov)
percent_gains_onemo = [] # list of rolling 1-month % gains

for i in range(len(prices) - 1):
    if i < len(prices) - 4:
        percent_gains_fourmo.append(100*(prices[i+4] - prices[i])/(prices[i]))
    percent_gains_onemo.append(100*(prices[i+1] - prices[i])/(prices[i]))

# make into np array
np_gains_fourmo = np.array(percent_gains_fourmo)
np_gains_onemo = np.array(percent_gains_onemo)


gains_mean_fourmo, gains_std_fourmo = np.mean(np_gains_fourmo), np.std(np_gains_fourmo)
gains_mean_onemo, gains_std_onemo = np.mean(np_gains_onemo), np.std(np_gains_onemo)

## run monte carlo simulation for diff buckets using normal sampling
## of percentage gain (1+that sample)
## RUN X times and categorize probability of each bin
buckets_fourmo = [0, 0, 0, 0, 0]
buckets_onemo = [0, 0, 0, 0, 0]
X = 1000000
curr_value = n


for i in range(X):
    estimate_fourmo = (1 + (np.random.normal(gains_mean_fourmo, gains_std_fourmo)/100)) * curr_value
    
    ## random walk from one month normal distribution to estimate
    ## the four month change
    estimate_onemo = curr_value
    for j in range(4):
        estimate_onemo *= (1 + (np.random.normal(gains_mean_onemo, gains_std_onemo)/100))
    
    if estimate_fourmo < 220:
        buckets_fourmo[0] += 1
    elif estimate_fourmo <= 260:
        buckets_fourmo[1] += 1
    elif estimate_fourmo < 300:
        buckets_fourmo[2] += 1
    elif estimate_fourmo <= 340:
        buckets_fourmo[3] += 1
    else:
        buckets_fourmo[4] += 1

    if estimate_onemo < 220:
        buckets_onemo[0] += 1
    elif estimate_onemo <= 260:
        buckets_onemo[1] += 1
    elif estimate_onemo < 300:
        buckets_onemo[2] += 1
    elif estimate_onemo <= 340:
        buckets_onemo[3] += 1
    else:
        buckets_onemo[4] += 1

probabilities_onemo = [round(100*float(occurances)/float(X), 3) for occurances in buckets_onemo]
probabilities_fourmo = [round(100*float(occurances)/float(X), 3) for occurances in buckets_fourmo]


print("Four Month Rolling Prob.:", probabilities_fourmo)
print("One Month Rolling Prob.:", probabilities_onemo)
