import csv
import numpy as np
from dateutil import parser
from datetime import datetime
from datetime import timedelta
  
# Months table
MONTHS = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}

# csv file name
filename = "CPI Questions/CPIAUCSL.csv"

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)
    cpis = [] # list of historical CPI nums
    historical_cutoff = 100 # how many years back are we considering
    next(csvreader) # skip header
    
    for row in csvreader:
        dte = parser.parse(row[0])
        
        ## append cpis after historical cuttoff to our price list
        if(dte > datetime.now() - timedelta(weeks=(52*historical_cutoff))):
            cpis.append(float(row[1]))

percent_gains_threemo = [] # list of rolling 5-month % gains (jul, aug, sep)
percent_gains_onemo = [] # list of rolling 1-month % gains

for i in range(len(cpis) - 1):
    if i < len(cpis) - 3:
        percent_gains_threemo.append(100*(cpis[i+3] - cpis[i])/(cpis[i]))
    percent_gains_onemo.append(100*(cpis[i+1] - cpis[i])/(cpis[i]))

# make into np array
np_gains_threemo = np.array(percent_gains_threemo)
np_gains_onemo = np.array(percent_gains_onemo)


gains_mean_threemo, gains_std_threemo = np.mean(np_gains_threemo), np.std(np_gains_threemo)
gains_mean_onemo, gains_std_onemo = np.mean(np_gains_onemo), np.std(np_gains_onemo)

print(gains_mean_onemo, gains_std_onemo)

## run monte carlo simulation for diff buckets using normal sampling
## of percentage gain (1+that sample)
## RUN X times and categorize probability of each bin
buckets_threemo = [0, 0, 0, 0, 0]
buckets_onemo = [0, 0, 0, 0, 0]
X = 1000000
curr_value = 270.981 # June 2021
cpi_sep2020 = 260.149
for i in range(X):
    cpi_estimate_threemo = (1 + (np.random.normal(gains_mean_threemo, gains_std_threemo)/100)) * curr_value
    
    ## random walk from one month normal distribution to estimate
    ## the five month change
    cpi_estimate_onemo = curr_value
    for j in range(3):
        cpi_estimate_onemo *= (1 + (np.random.normal(gains_mean_onemo, gains_std_onemo)/100))


    pct_change_threemo = round(100*(cpi_estimate_threemo - cpi_sep2020)/cpi_sep2020, 2)
    pct_change_onemo = round(100*(cpi_estimate_onemo - cpi_sep2020)/cpi_sep2020, 2)
    
    if pct_change_threemo < 1.7:
        buckets_threemo[0] += 1
    elif pct_change_threemo <= 2.1:
        buckets_threemo[1] += 1
    elif pct_change_threemo < 2.7:
        buckets_threemo[2] += 1
    elif pct_change_threemo <= 3.1:
        buckets_threemo[3] += 1
    else:
        buckets_threemo[4] += 1

    if pct_change_onemo < 1.7:
        buckets_onemo[0] += 1
    elif pct_change_onemo <= 2.1:
        buckets_onemo[1] += 1
    elif pct_change_onemo < 2.7:
        buckets_onemo[2] += 1
    elif pct_change_onemo <= 3.1:
        buckets_onemo[3] += 1
    else:
        buckets_onemo[4] += 1

probabilities_onemo = [round(100*float(occurances)/float(X), 3) for occurances in buckets_onemo]
probabilities_threemo = [round(100*float(occurances)/float(X), 3) for occurances in buckets_threemo]


print("Three Month Rolling Prob.:", probabilities_threemo)
print("One Month Rolling Prob.:", probabilities_onemo)
