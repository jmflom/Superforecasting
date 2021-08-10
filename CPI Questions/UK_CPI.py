import csv
import numpy as np
from dateutil import parser
from datetime import datetime
from datetime import timedelta
  
# Months table
MONTHS = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}

# csv file name
filename = "CPI Questions/UK_CPI_data.csv"

# reading csv file
with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    cpis = [] # list of historical CPI nums

    historical_cutoff = 20 # how many years back are we considering
    for row in csvreader:
        dte_raw = row[0]
        if len(dte_raw) == 8:
            dte_temp = str(dte_raw[:4]) + '-' + MONTHS[dte_raw[5:]] + '-01'
            dte = parser.parse(dte_temp)
        
            ## append cpis after historical cuttoff to our price list
            if(dte > datetime.now() - timedelta(weeks=(52*historical_cutoff))):
                cpis.append(float(row[1]))

percent_gains_fivemo = [] # list of rolling 5-month % gains (jul, aug, sep, oct, nov)
percent_gains_onemo = [] # list of rolling 1-month % gains

for i in range(len(cpis) - 1):
    if i < len(cpis) - 5:
        percent_gains_fivemo.append(100*(cpis[i+5] - cpis[i])/(cpis[i]))
    percent_gains_onemo.append(100*(cpis[i+1] - cpis[i])/(cpis[i]))

# make into np array
np_gains_fivemo = np.array(percent_gains_fivemo)
np_gains_onemo = np.array(percent_gains_onemo)


gains_mean_fivemo, gains_std_fivemo = np.mean(np_gains_fivemo), np.std(np_gains_fivemo)
gains_mean_onemo, gains_std_onemo = np.mean(np_gains_onemo), np.std(np_gains_onemo)

## run monte carlo simulation for diff buckets using normal sampling
## of percentage gain (1+that sample)
## RUN X times and categorize probability of each bin
buckets_fivemo = [0, 0, 0, 0, 0, 0]
buckets_onemo = [0, 0, 0, 0, 0, 0]
X = 1000000
curr_value = 111.3
cpi_nov2020 = 108.9
for i in range(X):
    cpi_estimate_fivemo = (1 + (np.random.normal(gains_mean_fivemo, gains_std_fivemo)/100)) * curr_value
    
    ## random walk from one month normal distribution to estimate
    ## the five month change
    cpi_estimate_onemo = curr_value
    for j in range(5):
        cpi_estimate_onemo *= (1 + (np.random.normal(gains_mean_onemo, gains_std_onemo)/100))


    pct_change_fivemo = round(100*(cpi_estimate_fivemo - cpi_nov2020)/cpi_nov2020, 2)
    pct_change_onemo = round(100*(cpi_estimate_onemo - cpi_nov2020)/cpi_nov2020, 2)
    
    if pct_change_fivemo < 1.7:
        buckets_fivemo[0] += 1
    elif pct_change_fivemo <= 2.2:
        buckets_fivemo[1] += 1
    elif pct_change_fivemo < 2.9:
        buckets_fivemo[2] += 1
    elif pct_change_fivemo <= 3.4:
        buckets_fivemo[3] += 1
    elif pct_change_fivemo < 4.1:
        buckets_fivemo[4] += 1
    else:
        buckets_fivemo[5] += 1

    if pct_change_onemo < 1.7:
        buckets_onemo[0] += 1
    elif pct_change_onemo <= 2.2:
        buckets_onemo[1] += 1
    elif pct_change_onemo < 2.9:
        buckets_onemo[2] += 1
    elif pct_change_onemo <= 3.4:
        buckets_onemo[3] += 1
    elif pct_change_onemo < 4.1:
        buckets_onemo[4] += 1
    else:
        buckets_onemo[5] += 1

probabilities_onemo = [round(100*float(occurances)/float(X), 3) for occurances in buckets_onemo]
probabilities_fivemo = [round(100*float(occurances)/float(X), 3) for occurances in buckets_fivemo]


print("Five Month Rolling Prob.:", probabilities_fivemo)
print("One Month Rolling Prob.:", probabilities_onemo)
